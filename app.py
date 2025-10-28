#!/usr/bin/env python3
"""
Streamlit Application for ISEC Contract Note Data Extraction
"""

import streamlit as st
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from pypdf import PdfReader, PdfWriter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Page configuration
st.set_page_config(
    page_title="ISEC Contract Note Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: monospace;
        font-size: 12px;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Load default data
@st.cache_data
def load_default_system_prompt():
    """Load the default system prompt from file."""
    try:
        with open('system_prompt.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "# System Prompt\nExtract data from ISEC contract notes."

@st.cache_data
def load_default_position_prompt():
    """Load the default position prompt (minimal prompt) from file."""
    try:
        with open('minimal_system_prompt.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "# Position Prompt\nExtract ISEC contract note data."

@st.cache_data
def load_default_result():
    """Load the default result JSON from file."""
    try:
        with open('chirag_both.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"message": "No default result available"}

@st.cache_data
def load_config():
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "openai": {
                "default_model": "gpt-4o",
                "max_tokens": 8000,
                "temperature": 0.1
            }
        }

@st.cache_data
def load_compact_schema():
    """Load the compact schema from file."""
    try:
        with open('compact_schema.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def reduce_pdf_size(pdf_file, config):
    """
    Reduce PDF size by extracting only first 2 and last 2 pages.
    
    Args:
        pdf_file: Uploaded file object
        config: Configuration dictionary
        
    Returns:
        Path to the reduced PDF file
    """
    try:
        # Create temporary file for the uploaded PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_input:
            temp_input.write(pdf_file.read())
            temp_input_path = temp_input.name
        
        # Create temporary file for reduced PDF
        temp_output = tempfile.NamedTemporaryFile(suffix="_reduced.pdf", delete=False)
        temp_output_path = temp_output.name
        temp_output.close()
        
        # Read the original PDF
        reader = PdfReader(temp_input_path)
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
            logger.info(f"Added last 2 pages")
        
        # Write the reduced PDF
        with open(temp_output_path, "wb") as f:
            writer.write(f)
        
        # Check file size reduction
        original_size = os.path.getsize(temp_input_path)
        reduced_size = os.path.getsize(temp_output_path)
        reduction_pct = (1 - reduced_size / original_size) * 100
        
        logger.info(f"PDF size reduced from {original_size:,} to {reduced_size:,} bytes ({reduction_pct:.1f}% reduction)")
        
        # Clean up input temp file
        os.unlink(temp_input_path)
        
        return temp_output_path, original_size, reduced_size
        
    except Exception as e:
        logger.error(f"Failed to reduce PDF size: {str(e)}")
        raise

def upload_pdf_to_openai(pdf_path, client):
    """Upload PDF file to OpenAI."""
    try:
        with open(pdf_path, "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose="user_data"
            )
        logger.info(f"PDF uploaded successfully: {uploaded_file.id}")
        return uploaded_file.id
    except Exception as e:
        logger.error(f"Failed to upload PDF: {str(e)}")
        return None

def extract_with_openai(file_id, system_prompt, position_prompt, schema, model, config, client):
    """Extract data using OpenAI API."""
    try:
        # Prepare the extraction prompt
        schema_text = json.dumps(schema, separators=(',', ':'))
        extraction_prompt = f"""{position_prompt}

Extract ISEC contract note data. Return JSON only:

{schema_text}"""
        
        # Create the extraction request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
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
            ],
            max_tokens=config["openai"]["max_tokens"],
            temperature=config["openai"]["temperature"]
        )
        
        # Parse the response
        response_text = response.choices[0].message.content
        logger.info(f"OpenAI response received: {len(response_text)} characters")
        
        # Extract JSON from response
        import re
        
        # Clean the response text
        cleaned_text = response_text
        if '```json' in response_text:
            pattern = r'```json\s*(.*?)\s*```'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                cleaned_text = match.group(1).strip()
        elif '```' in response_text:
            pattern = r'```\s*(.*?)\s*```'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                cleaned_text = match.group(1).strip()
        
        # Parse JSON
        extracted_data = json.loads(cleaned_text)
        
        return extracted_data, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI extraction failed: {error_msg}")
        return None, error_msg

def process_pdf(uploaded_file, system_prompt, position_prompt, model, config, schema):
    """Process the uploaded PDF and extract data."""
    errors = []
    warnings = []
    
    try:
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, ["OpenAI API key not found. Please set OPENAI_API_KEY environment variable."], []
        
        client = OpenAI(api_key=api_key)
        
        # Check file size and reduce if necessary
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        pdf_config = config.get("pdf_reduction", {})
        reduction_enabled = pdf_config.get("enabled", True)
        max_size_mb = pdf_config.get("max_file_size_mb", 0.1)
        
        logger.info(f"PDF file size: {file_size_mb:.2f}MB")
        
        pdf_path = None
        original_size = len(uploaded_file.getvalue())
        reduced_size = original_size
        
        if reduction_enabled and file_size_mb > max_size_mb:
            logger.info(f"PDF size exceeds threshold ({max_size_mb}MB), reducing size...")
            try:
                pdf_path, original_size, reduced_size = reduce_pdf_size(uploaded_file, config)
                warnings.append(f"PDF was reduced from {original_size/(1024*1024):.2f}MB to {reduced_size/(1024*1024):.2f}MB")
            except Exception as reduce_error:
                logger.error(f"Failed to reduce PDF size: {str(reduce_error)}")
                errors.append(f"PDF size reduction failed: {str(reduce_error)}")
                return None, errors, warnings
        else:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                pdf_path = temp_file.name
        
        # Upload PDF to OpenAI
        file_id = upload_pdf_to_openai(pdf_path, client)
        if not file_id:
            errors.append("Failed to upload PDF to OpenAI")
            return None, errors, warnings
        
        # Extract data using OpenAI
        extracted_data, error = extract_with_openai(file_id, system_prompt, position_prompt, schema, model, config, client)
        
        if error:
            errors.append(f"Extraction failed: {error}")
            return None, errors, warnings
        
        # Create result
        result = {
            "success": len(errors) == 0,
            "data": extracted_data,
            "errors": errors,
            "warnings": warnings,
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "model_used": model,
                "file_id": file_id,
                "total_transactions": len(extracted_data.get('transactions', [])),
                "original_file_size_mb": original_size / (1024 * 1024),
                "file_reduced": reduced_size < original_size,
                "reduced_file_size_mb": reduced_size / (1024 * 1024)
            }
        }
        
        # Clean up temp file
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)
        
        return result, errors, warnings
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        errors.append(f"Processing failed: {str(e)}")
        return None, errors, warnings

# Main app
def main():
    st.title("📄 ISEC Contract Note Data Extractor")
    st.markdown("Extract structured data from ISEC (ICICI Securities) contract notes using OpenAI")
    
    # Load defaults
    config = load_config()
    default_system_prompt = load_default_system_prompt()
    default_position_prompt = load_default_position_prompt()
    default_result = load_default_result()
    compact_schema = load_compact_schema()
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = default_result
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI Model Selection
        available_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        default_model = config["openai"].get("default_model", "gpt-4o")
        if default_model not in available_models:
            available_models.insert(0, default_model)
        
        selected_model = st.selectbox(
            "OpenAI Model",
            options=available_models,
            index=available_models.index(default_model),
            help="Select the OpenAI model to use for extraction"
        )
        
        st.divider()
        
        # API Key status
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✅ API Key Loaded")
        else:
            st.error("❌ API Key Not Found")
            st.info("Set OPENAI_API_KEY environment variable")
        
        st.divider()
        
        # PDF Upload
        st.header("📤 Upload PDF")
        uploaded_files = st.file_uploader(
            "Choose PDF file(s)",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more ISEC contract note PDF files"
        )
        
        # Process button
        process_button = st.button(
            "🚀 Process PDF",
            type="primary",
            disabled=not uploaded_files or not api_key,
            use_container_width=True
        )
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📝 System Prompt")
        system_prompt = st.text_area(
            "Edit System Prompt",
            value=default_system_prompt,
            height=300,
            help="The main system prompt that guides the extraction process",
            label_visibility="collapsed"
        )
    
    with col2:
        st.header("🎯 Position Prompt")
        position_prompt = st.text_area(
            "Edit Position Prompt",
            value=default_position_prompt,
            height=300,
            help="The position/minimal prompt used for extraction",
            label_visibility="collapsed"
        )
    
    # Results section
    st.header("📊 Extraction Results")
    
    # Process PDFs if button clicked
    if process_button and uploaded_files:
        st.session_state.processing = True
        
        for uploaded_file in uploaded_files:
            with st.expander(f"Processing: {uploaded_file.name}", expanded=True):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    result, errors, warnings = process_pdf(
                        uploaded_file,
                        system_prompt,
                        position_prompt,
                        selected_model,
                        config,
                        compact_schema
                    )
                    
                    if result:
                        st.session_state.result = result
                        
                        # Show success/error status
                        if result['success']:
                            st.markdown('<div class="success-box">✅ Extraction completed successfully!</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">❌ Extraction completed with errors</div>', unsafe_allow_html=True)
                        
                        # Show warnings
                        if warnings:
                            for warning in warnings:
                                st.markdown(f'<div class="warning-box">⚠️ {warning}</div>', unsafe_allow_html=True)
                        
                        # Show errors
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                        
                        # Display metadata
                        if 'metadata' in result:
                            st.subheader("📋 Metadata")
                            meta_col1, meta_col2, meta_col3 = st.columns(3)
                            with meta_col1:
                                st.metric("Transactions", result['metadata'].get('total_transactions', 0))
                            with meta_col2:
                                st.metric("Model", result['metadata'].get('model_used', 'N/A'))
                            with meta_col3:
                                file_size = result['metadata'].get('reduced_file_size_mb', result['metadata'].get('original_file_size_mb', 0))
                                st.metric("File Size", f"{file_size:.2f} MB")
                        
                        # Display result JSON
                        st.subheader("📄 Extracted Data (JSON)")
                        st.json(result)
                        
                        # Download button
                        json_str = json.dumps(result, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_str,
                            file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted.json",
                            mime="application/json"
                        )
                    else:
                        st.error("Failed to process PDF")
                        for error in errors:
                            st.error(f"❌ {error}")
        
        st.session_state.processing = False
    
    # Display current result
    else:
        st.subheader("📄 Current Result (JSON)")
        st.json(st.session_state.result)
        
        # Download button for current result
        json_str = json.dumps(st.session_state.result, indent=2)
        st.download_button(
            label="💾 Download Current Result",
            data=json_str,
            file_name="current_result.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()

