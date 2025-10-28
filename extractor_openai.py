#!/usr/bin/env python3
"""
ISEC Contract Note Data Extractor using OpenAI API

A comprehensive system for extracting financial data from ISEC (ICICI Securities) contract notes.
This extractor uploads the PDF directly to OpenAI and uses GPT models for analysis.
"""

import json
import logging
import re
import os
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from pypdf import PdfReader, PdfWriter

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try manual .env loading
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Data class to hold extraction results with metadata"""
    success: bool
    data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class ISECAPIExtractor:
    """
    Extractor for ISEC (ICICI Securities) contract notes using OpenAI API.
    Uploads PDF directly and analyzes with GPT models.
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the extractor with OpenAI configuration.

        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: OpenAI model to use for extraction (if None, uses config file)
        """
        self.config = self._load_config()

        # Use provided values or defaults from config
        api_key = api_key or os.getenv(self.config["openai"]["api_key_env_var"])
        if not api_key:
            raise ValueError(f"OpenAI API key not found. Set {self.config['openai']['api_key_env_var']} environment variable or provide api_key parameter.")

        self.client = OpenAI(api_key=api_key)
        self.model = model or self.config["openai"]["default_model"]
        self.system_prompt = self._load_system_prompt()
        self.output_schema = self._load_output_schema()
        self.full_schema = self._load_full_schema()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json file."""
        config_path = Path(__file__).parent / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Configuration file not found: config.json")
            raise FileNotFoundError("Required config.json file not found. Please ensure the file exists in the same directory as the extractor.")

    def _load_system_prompt(self) -> str:
        """Load the system prompt from file."""
        # Use minimal prompt if configured
        if self.config["extraction"]["use_minimal_prompts"]:
            prompt_file = self.config["files"]["system_prompt"]
        else:
            prompt_file = self.config["files"]["full_system_prompt"]

        prompt_path = Path(__file__).parent / prompt_file
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"System prompt file not found: {prompt_file}")
            raise FileNotFoundError(f"Required {prompt_file} file not found. Please ensure the file exists in the same directory as the extractor.")

    def _load_output_schema(self) -> Dict[str, Any]:
        """Load the output schema from file."""
        # Use compact schema for prompts, full schema for validation
        schema_file = self.config["files"]["compact_schema"]
        schema_path = Path(__file__).parent / schema_file
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_file}")
            return {}

    def _load_full_schema(self) -> Dict[str, Any]:
        """Load the full schema for validation."""
        schema_file = self.config["files"]["full_schema"]
        schema_path = Path(__file__).parent / schema_file
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Full schema file not found: {schema_file}, using compact schema for validation")
            return self.output_schema

    def extract_from_pdf(self, pdf_path: str, system_prompt: str = None, position_prompt: str = None) -> ExtractionResult:
        """
        Main extraction method using OpenAI API.

        Args:
            pdf_path: Path to the PDF file
            system_prompt: Optional custom system prompt (overrides default)
            position_prompt: Optional custom position prompt (combined with system prompt)

        Returns:
            ExtractionResult with extracted data and metadata
        """
        errors = []
        warnings = []
        reduced_pdf_path = None
        original_pdf_path = pdf_path

        try:
            # Check file size and reduce if necessary
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            pdf_config = self.config.get("pdf_reduction", {})
            reduction_enabled = pdf_config.get("enabled", True)
            max_size_mb = pdf_config.get("max_file_size_mb", 50)

            logger.info(f"PDF file size: {file_size_mb:.2f}MB")
            logger.info(f"PDF reduction enabled: {reduction_enabled}, threshold: {max_size_mb}MB")

            if reduction_enabled and file_size_mb > max_size_mb:
                logger.info(f"PDF size exceeds threshold ({max_size_mb}MB), reducing size...")
                try:
                    reduced_pdf_path = self._reduce_pdf_size(pdf_path)
                    pdf_path = reduced_pdf_path
                    reduced_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
                    warnings.append(f"PDF was reduced from {file_size_mb:.2f}MB to {reduced_size_mb:.2f}MB")
                except Exception as reduce_error:
                    logger.error(f"Failed to reduce PDF size: {str(reduce_error)}")
                    errors.append(f"PDF size reduction failed: {str(reduce_error)}")
                    return ExtractionResult(
                        success=False,
                        data={},
                        errors=errors,
                        warnings=warnings,
                        metadata={}
                    )

            # Upload PDF to OpenAI
            file_id = self._upload_pdf(pdf_path)
            if not file_id:
                errors.append("Failed to upload PDF to OpenAI")
                return ExtractionResult(
                    success=False,
                    data={},
                    errors=errors,
                    warnings=warnings,
                    metadata={}
                )

            # Extract data using OpenAI with custom prompts if provided
            extracted_data = self._extract_with_openai(file_id, system_prompt, position_prompt)

            # Validate the extracted data
            validation_errors = self._validate_extracted_data(extracted_data)
            errors.extend(validation_errors)

            success = len(errors) == 0

            # Create metadata
            metadata = {
                "extraction_timestamp": datetime.now().isoformat(),
                "pdf_path": original_pdf_path,
                "model_used": self.model,
                "file_id": file_id,
                "total_transactions": len(extracted_data.get('transactions', [])),
                "validation_errors": len(errors),
                "original_file_size_mb": file_size_mb,
                "file_reduced": reduced_pdf_path is not None
            }

            if reduced_pdf_path:
                metadata["reduced_file_size_mb"] = os.path.getsize(reduced_pdf_path) / (1024 * 1024)

            return ExtractionResult(
                success=success,
                data=extracted_data,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return ExtractionResult(
                success=False,
                data={},
                errors=[f"Extraction failed: {str(e)}"],
                warnings=warnings,
                metadata={
                    "pdf_path": original_pdf_path,
                    "extraction_timestamp": datetime.now().isoformat()
                }
            )

        finally:
            # Clean up temporary files
            if reduced_pdf_path:
                self._cleanup_temp_file(reduced_pdf_path)

    def _reduce_pdf_size(self, pdf_path: str) -> str:
        """
        Reduce PDF size by extracting only first 2 and last 2 pages.

        Args:
            pdf_path: Path to the original PDF file

        Returns:
            Path to the reduced PDF file
        """
        try:
            # Create temporary file for reduced PDF
            temp_file = tempfile.NamedTemporaryFile(
                suffix="_reduced.pdf",
                delete=False,
                dir=Path(pdf_path).parent
            )
            temp_path = temp_file.name
            temp_file.close()

            # Read the original PDF
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            total_pages = len(reader.pages)

            logger.info(f"Original PDF has {total_pages} pages")

            # Handle edge cases
            if total_pages <= 4:
                # If PDF has 4 or fewer pages, use all pages
                for page in reader.pages:
                    writer.add_page(page)
                logger.info("PDF has 4 or fewer pages, using all pages")
            else:
                # Extract first 2 pages
                for i in range(min(2, total_pages)):
                    writer.add_page(reader.pages[i])
                logger.info(f"Added first {min(2, total_pages)} pages")

                # Extract last 2 pages
                for i in range(max(0, total_pages - 2), total_pages):
                    writer.add_page(reader.pages[i])
                logger.info(f"Added last 2 pages (pages {total_pages-1} and {total_pages})")

            # Write the reduced PDF
            with open(temp_path, "wb") as f:
                writer.write(f)

            # Check file size reduction
            original_size = os.path.getsize(pdf_path)
            reduced_size = os.path.getsize(temp_path)
            reduction_pct = (1 - reduced_size / original_size) * 100

            logger.info(f"PDF size reduced from {original_size:,} to {reduced_size:,} bytes ({reduction_pct:.1f}% reduction)")
            logger.info(f"Reduced PDF saved to: {temp_path}")

            return temp_path

        except Exception as e:
            logger.error(f"Failed to reduce PDF size: {str(e)}")
            raise

    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary files."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {str(e)}")

    def _upload_pdf(self, pdf_path: str) -> Optional[str]:
        """Upload PDF file to OpenAI."""
        try:
            with open(pdf_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose="user_data"
                )
            logger.info(f"PDF uploaded successfully: {uploaded_file.id}")
            return uploaded_file.id
        except Exception as e:
            logger.error(f"Failed to upload PDF: {str(e)}")
            return None

    def _extract_with_openai(self, file_id: str, system_prompt: str = None, position_prompt: str = None) -> Dict[str, Any]:
        """Extract data using OpenAI API."""
        try:
            # Prepare the extraction prompt
            extraction_prompt = self._prepare_extraction_prompt()

            # Use custom prompts if provided, otherwise use default
            effective_system_prompt = system_prompt if system_prompt else self.system_prompt

            # Combine system prompt and position prompt if both are provided
            if position_prompt:
                effective_system_prompt = f"{effective_system_prompt}\n\n{position_prompt}"

            # Prepare request parameters based on model type
            request_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": effective_system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "file",
                                "file": {
                                    "file_id": file_id
                                }
                            },
                            {
                                "type": "text",
                                "text": extraction_prompt,
                            }
                        ]
                    }
                ]
            }

            # Add model-specific parameters
            if self.model.startswith("gpt-5"):
                # GPT-5 models use max_completion_tokens instead of max_tokens
                request_params["max_completion_tokens"] = self.config["openai"]["max_tokens"]
                # Note: temperature is not supported by GPT-5 models in Chat Completions API
            else:
                # Legacy models use max_tokens and temperature
                request_params["max_tokens"] = self.config["openai"]["max_tokens"]
                request_params["temperature"] = self.config["openai"].get("temperature", 0.1)

            # Create the extraction request
            response = self.client.chat.completions.create(**request_params)

            # Parse the response
            response_text = response.choices[0].message.content
            logger.info(f"OpenAI response received: {len(response_text)} characters")

            # Debug: Check if response is empty or None
            if not response_text:
                logger.warning("Empty response received from OpenAI")
                logger.warning(f"Response object: {response}")
                logger.warning(f"Choices: {response.choices}")
                logger.warning(f"Choice 0: {response.choices[0] if response.choices else 'No choices'}")
                if response.choices:
                    logger.warning(f"Message: {response.choices[0].message}")
                    logger.warning(f"Content: {response.choices[0].message.content}")
                    logger.warning(f"Finish reason: {response.choices[0].finish_reason}")

                # Check usage information
                if hasattr(response, 'usage') and response.usage:
                    logger.info(f"Token usage: {response.usage}")

                # If GPT-5 returns empty response, try fallback to GPT-4o
                if self.model.startswith("gpt-5"):
                    logger.warning(f"GPT-5 model {self.model} returned empty response, trying fallback to gpt-4o")
                    fallback_params = request_params.copy()
                    fallback_params["model"] = "gpt-4o"
                    # Add back temperature and max_tokens for GPT-4o
                    fallback_params["max_tokens"] = self.config["openai"]["max_tokens"]
                    fallback_params["temperature"] = self.config["openai"].get("temperature", 0.1)
                    # Remove GPT-5 specific parameters
                    if "max_completion_tokens" in fallback_params:
                        del fallback_params["max_completion_tokens"]

                    try:
                        logger.info("Attempting fallback extraction with GPT-4o...")
                        fallback_response = self.client.chat.completions.create(**fallback_params)
                        fallback_response_text = fallback_response.choices[0].message.content
                        logger.info(f"Fallback response received: {len(fallback_response_text)} characters")

                        if fallback_response_text:
                            extracted_data = self._parse_json_response(fallback_response_text)
                            logger.info("Successfully used GPT-4o fallback")
                            return extracted_data
                        else:
                            logger.error("Fallback model also returned empty response")
                    except Exception as fallback_error:
                        logger.error(f"Fallback extraction failed: {str(fallback_error)}")

                return {}

            # Extract JSON from response
            extracted_data = self._parse_json_response(response_text)

            return extracted_data

        except Exception as e:
            error_msg = str(e)
            logger.error(f"OpenAI extraction failed: {error_msg}")

            # Check if it's a token limit error and suggest fallback
            if "token size" in error_msg.lower() or "exceeds the maximum limit" in error_msg.lower():
                logger.error("PDF file too large for OpenAI API. Suggest using traditional extractor (extractor.py) instead.")
                logger.error("Example: python extractor.py both.pdf -o both_traditional.json")

            return {}

    def _prepare_extraction_prompt(self) -> str:
        """Prepare the extraction prompt for OpenAI."""
        # Create compact prompt
        schema_text = json.dumps(self.output_schema, separators=(',', ':'))

        prompt = f"""Extract ISEC contract note data. Return JSON only:

{schema_text}"""

        # Check prompt length
        if self._check_prompt_length(prompt + self.system_prompt):
            logger.info("Using optimized prompt (compact)")
            return prompt
        else:
            logger.warning("Prompt too long, using ultra-compact version")
            return self._prepare_ultra_compact_prompt()

    def _check_prompt_length(self, prompt_text: str) -> bool:
        """Check if prompt is within acceptable token limits."""
        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = len(prompt_text) // 4
        max_tokens = self.config["extraction"]["max_prompt_tokens"]

        logger.info(f"Estimated prompt tokens: {estimated_tokens}, max: {max_tokens}")
        return estimated_tokens <= max_tokens

    def _prepare_ultra_compact_prompt(self) -> str:
        """Prepare ultra-compact prompt for very large files."""
        return "Extract ISEC contract note data. Return JSON with header, transactions, obligations."

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from OpenAI response text."""
        try:
            # Clean the response text first
            cleaned_text = self._clean_response_text(response_text)
            logger.info(f"Original response length: {len(response_text)}, Cleaned length: {len(cleaned_text)}")

            # Try to extract JSON from the response
            # Look for JSON pattern in the text
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, cleaned_text)

            if match:
                json_str = match.group(0)
                # Try to fix any truncation issues
                json_str = self._fix_truncated_json(json_str)

                data = json.loads(json_str)
                logger.info("Successfully parsed JSON from response")
                return data
            else:
                # If no JSON pattern found, try parsing the entire response
                data = json.loads(cleaned_text.strip())
                logger.info("Successfully parsed entire response as JSON")
                return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {str(e)}")
            logger.error(f"Response text: {response_text[:1000]}...")
            # Try to show what we cleaned
            cleaned_text = self._clean_response_text(response_text)
            logger.error(f"Cleaned text: {cleaned_text[:1000]}...")

            # Try one more time with aggressive cleaning
            try:
                logger.info("Attempting aggressive JSON fix...")
                cleaned_text = self._clean_response_text(response_text)
                json_str = self._fix_truncated_json(cleaned_text)
                data = json.loads(json_str)
                logger.info("Successfully parsed JSON with aggressive fix")
                return data
            except Exception as retry_e:
                logger.error(f"Aggressive fix also failed: {retry_e}")
                return {}

    def _clean_response_text(self, response_text: str) -> str:
        """Clean response text by removing markdown code blocks and other formatting."""
        logger.info(f"Cleaning response text, original length: {len(response_text)}")

        # Remove markdown code blocks
        if '```json' in response_text:
            # Extract content between ```json and ```
            pattern = r'```json\s*(.*?)\s*```'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                cleaned = match.group(1).strip()
                logger.info(f"Found ```json block, cleaned length: {len(cleaned)}")
                return cleaned

        if '```' in response_text:
            # Extract content between any ``` blocks
            pattern = r'```\s*(.*?)\s*```'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                cleaned = match.group(1).strip()
                logger.info(f"Found generic ``` block, cleaned length: {len(cleaned)}")
                return cleaned

        # Remove any remaining markdown formatting
        cleaned = re.sub(r'```[a-zA-Z]*\s*', '', response_text)
        cleaned = re.sub(r'\s*```\s*', '', cleaned)
        cleaned = cleaned.strip()

        logger.info(f"No markdown blocks found, returning stripped text, length: {len(cleaned)}")
        return cleaned

    def _fix_truncated_json(self, json_str: str) -> str:
        """Attempt to fix truncated JSON by finding the last complete object."""
        try:
            # Find the last complete closing brace
            brace_count = 0
            last_complete_pos = -1

            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_complete_pos = i

            if last_complete_pos > 0 and last_complete_pos < len(json_str) - 1:
                # Truncate to the last complete object
                fixed_json = json_str[:last_complete_pos + 1]
                logger.info(f"Fixed truncated JSON, new length: {len(fixed_json)}")
                return fixed_json
            else:
                return json_str
        except Exception as e:
            logger.error(f"Error fixing truncated JSON: {e}")
            return json_str

    def _validate_extracted_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate extracted data against schema and business rules."""
        errors = []

        if not data:
            errors.append("No data extracted from PDF")
            return errors

        # Validate header
        if 'header' not in data:
            errors.append("Missing header section")
        else:
            header = data['header']
            required_header_fields = [
                'contract_note_no', 'trade_date', 'settlement_no',
                'settlement_date', 'client_id', 'client_name'
            ]

            for field in required_header_fields:
                if field not in header or not header[field]:
                    errors.append(f"Missing required header field: {field}")

        # Validate transactions
        if 'transactions' not in data:
            errors.append("Missing transactions section")
        else:
            transactions = data['transactions']
            if not isinstance(transactions, list):
                errors.append("Transactions should be a list")
            else:
                for i, transaction in enumerate(transactions):
                    transaction_errors = self._validate_transaction(transaction, i)
                    errors.extend(transaction_errors)

        # Validate obligations
        if 'obligations' not in data:
            errors.append("Missing obligations section")
        else:
            obligation_errors = self._validate_obligations(data['obligations'])
            errors.extend(obligation_errors)

        return errors

    def _validate_transaction(self, transaction: Dict[str, Any], index: int) -> List[str]:
        """Validate a single transaction."""
        errors = []
        prefix = f"Transaction {index}"

        # Check ISIN
        isin = transaction.get('isin', '')
        if not isin:
            errors.append(f"{prefix}: Missing ISIN")
        elif not re.match(r'^[A-Z]{2}[0-9A-Z]{10}$', isin):
            errors.append(f"{prefix}: Invalid ISIN format: {isin}")

        # Check security name
        if not transaction.get('security_name'):
            errors.append(f"{prefix}: Missing security name")

        # Validate numeric fields are actually numbers
        numeric_fields = [
            'buy_quantity', 'sell_quantity', 'total_quantity',
            'buy_weighted_average_price', 'sell_weighted_average_price',
            'buy_net_payable_receivable', 'sell_net_payable_receivable',
            'total_net_payable_receivable'
        ]

        for field in numeric_fields:
            value = transaction.get(field)
            if value is not None and not isinstance(value, (int, float)):
                try:
                    transaction[field] = float(value)
                except (ValueError, TypeError):
                    errors.append(f"{prefix}: Invalid numeric value for {field}: {value}")

        return errors

    def _validate_obligations(self, obligations: Dict[str, Any]) -> List[str]:
        """Validate obligations section."""
        errors = []

        # Check required top-level fields
        required_fields = [
            'pay_out_obligation', 'taxable_value_of_supply',
            'gst_details', 'securities_transaction_tax', 'stamp_duty',
            'net_amount_receivable_by_client', 'net_amount_to_be_credited_in_bank'
        ]

        for field in required_fields:
            if field not in obligations:
                errors.append(f"Missing obligations field: {field}")

        # Validate taxable value supply structure
        if 'taxable_value_of_supply' in obligations:
            tvs = obligations['taxable_value_of_supply']
            tvs_fields = ['total_brokerage', 'exchange_transaction_charges',
                         'sebi_turnover_fees', 'total_taxable_value']

            for field in tvs_fields:
                if field not in tvs:
                    errors.append(f"Missing taxable value field: {field}")

        # Validate GST details structure
        if 'gst_details' in obligations:
            gst = obligations['gst_details']
            gst_fields = [
                'cgst_rate', 'cgst_brokerage_amount', 'cgst_charges_amount', 'cgst_total_amount',
                'sgst_rate', 'sgst_brokerage_amount', 'sgst_charges_amount', 'sgst_total_amount',
                'igst_rate', 'igst_brokerage_amount', 'igst_charges_amount', 'igst_total_amount'
            ]

            for field in gst_fields:
                if field not in gst:
                    errors.append(f"Missing GST detail field: {field}")

        return errors

    def save_result(self, result: ExtractionResult, output_path: str):
        """Save extraction result to JSON file."""
        output_data = {
            "success": result.success,
            "data": result.data,
            "errors": result.errors,
            "warnings": result.warnings,
            "metadata": result.metadata
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)

        logger.info(f"Results saved to: {output_path}")

def main():
    """Main function for command-line usage."""
    import argparse
    import os
    import re

    # Load config to get defaults
    try:
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error("Configuration file not found: config.json")
        return

    parser = argparse.ArgumentParser(description='Extract data from ISEC contract notes using OpenAI API')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('-o', '--output', help='Output JSON file path',
                       default='extracted_data_openai.json')
    parser.add_argument('-k', '--api-key', help='OpenAI API key (if not set in environment)')
    parser.add_argument('-m', '--model', help=f'OpenAI model to use (default: {config["openai"]["default_model"]})')

    args = parser.parse_args()

    # Initialize extractor
    try:
        extractor = ISECAPIExtractor(api_key=args.api_key, model=args.model)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to initialize extractor: {str(e)}")
        return

    # Extract data
    logger.info(f"Extracting data from: {args.pdf_path}")
    logger.info(f"Using model: {extractor.model}")

    result = extractor.extract_from_pdf(args.pdf_path)

    # Save results
    extractor.save_result(result, args.output)

    # Print summary
    if result.success:
        logger.info("Extraction completed successfully")
        logger.info(f"Extracted {len(result.data.get('transactions', []))} transactions")
        logger.info(f"Client: {result.data.get('header', {}).get('client_name', 'N/A')}")
        logger.info(f"Contract Note: {result.data.get('header', {}).get('contract_note_no', 'N/A')}")
    else:
        logger.error("Extraction completed with errors")
        for error in result.errors:
            logger.error(f"Error: {error}")

if __name__ == "__main__":
    main()