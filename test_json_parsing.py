#!/usr/bin/env python3
"""Test script for JSON parsing with markdown code blocks"""

import json
import re

def _clean_response_text(response_text: str) -> str:
    """Clean response text by removing markdown code blocks and other formatting."""
    print(f"Original text starts with: {repr(response_text[:100])}")

    # Remove markdown code blocks
    if '```json' in response_text:
        # Extract content between ```json and ```
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            result = match.group(1).strip()
            print(f"Found ```json block, cleaned length: {len(result)}")
            print(f"Cleaned text starts with: {repr(result[:100])}")
            return result

    if '```' in response_text:
        # Extract content between any ``` blocks
        pattern = r'```\s*(.*?)\s*```'
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            result = match.group(1).strip()
            print(f"Found generic ``` block, cleaned length: {len(result)}")
            print(f"Cleaned text starts with: {repr(result[:100])}")
            return result

    # Remove any remaining markdown formatting
    cleaned = re.sub(r'```[a-zA-Z]*\s*', '', response_text)
    cleaned = re.sub(r'\s*```\s*', '', cleaned)

    print(f"No markdown blocks found, returning stripped text")
    return cleaned.strip()

# Test with a sample response that might be similar to what we're getting
sample_response = '''```json
{
  "header": {
    "contract_note_no": "ISEC/2025029/036170355",
    "trade_date": "10-02-2025",
    "settlement_no": "2025029",
    "settlement_date": "07-02-2025",
    "client_id": "5550001544",
    "client_name": "PKEDAY ADVISORS LLP"
  },
  "transactions": [
    {
      "isin": "INE00WC01027",
      "security_name": "AFFLE (INDIA) LIMITED",
      "buy_quantity": 6000,
      "buy_weighted_average_price": 1655.9795,
      "buy_brokerage_per_share": 1.1592,
      "buy_wap_after_brokerage": 1657.1387,
      "buy_total_trade_value_after_brokerage": 9942832.2,
      "buy_exchange_transaction_charges": 9.9428,
      "buy_sebi_turnover_charges": 9.9428,
      "buy_total_gst": 2615.3,
      "buy_stamp_duty": 497.14,
      "buy_securities_transaction_tax": 0.0,
      "buy_net_payable_receivable": 9947895.58
    }
  ]
}
```'''

print("Testing JSON parsing...")
cleaned = _clean_response_text(sample_response)
print(f"\nCleaned JSON length: {len(cleaned)}")

try:
    parsed = json.loads(cleaned)
    print("✅ JSON parsing successful!")
    print(f"Contract Note: {parsed['header']['contract_note_no']}")
    print(f"Transactions: {len(parsed['transactions'])}")
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing failed: {e}")
    print(f"Error location: {e.pos}")
    if e.pos < len(cleaned):
        print(f"Context around error: {repr(cleaned[max(0, e.pos-20):e.pos+20])}")