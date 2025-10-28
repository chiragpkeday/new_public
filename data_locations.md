# ISEC Contract Note Data Location Mapping

## Document Structure Overview

ISEC (ICICI Securities) contract notes are typically multi-page documents with a standardized layout. Understanding the structure is crucial for accurate data extraction.

## 1. Header Information Location

### Page: First Page (Top Section)
**Visual Location**: Upper portion of the first page, usually in a header area

**Data Points and Search Patterns**:

| Field | Location | Search Text/Pattern | Extraction Notes |
|-------|----------|---------------------|------------------|
| contract_note_no | Top header area | "Contract Note No." | Usually appears with colon, extract the value immediately after |
| trade_date | Top header area | "TRADE DATE :" | Extract date string, handle various formats |
| settlement_no | Top header area | "SETTLEMENT NO. :" | Usually alphanumeric, extract after colon |
| settlement_date | Top header area | "SETTLEMENT DATE :" | Date format may vary (DD/MM/YYYY, DD-MM-YYYY) |
| client_id | Last page, Annexure section | "Trading Client Code" | Found in "Annexure Statement of Securities Transaction Tax" section |
| client_name | Last page, Annexure section | "Trading Client Name" | Same section as client_id, may appear as "client name" or "customer name" |

**Extraction Tips**:
- Header data is usually aligned in a table or structured format
- Look for variations in label wording (e.g., "Contract Note" vs "Contract Note No.")
- Client information may also appear near the top right of the first page in some formats

## 2. Transaction Data Location

### Page: Throughout Document (Where Trades Occur)
**Visual Location**: In tables labeled "Summary including statutory levies"

**Identification Pattern**:
- Look for the introductory text: "Sir/Madam, I/We have this day done by your order and on your account the following transactions:"
- Transaction tables follow this text immediately

**Table Structure**:
Each security (ISIN) has **EXACTLY THREE ROWS**:

### Row 1: Buy Transaction
- Label: Usually "Buy" or similar
- Contains: buy_quantity, buy_weighted_average_price, buy_brokerage_per_share, etc.
- If all values are 0, this indicates no buy transactions occurred

### Row 2: Sell Transaction
- Label: Usually "Sell" or similar
- Contains: sell_quantity, sell_weighted_average_price, sell_brokerage_per_share, etc.
- If all values are 0, this indicates no sell transactions occurred

### Row 3: Total Payable/Receivable
- Label: "Total Payable / Receivable" or similar
- Contains: total_* fields
- This row summarizes the net position for the security

**Column Mapping** (from left to right, typical layout):
1. ISIN (12-character identifier)
2. Security Name
3. Quantity
4. Weighted Average Price
5. Brokerage Per Share
6. WAP After Brokerage
7. Total Trade Value After Brokerage
8. Exchange Transaction Charges
9. SEBI Turnover Charges
10. Total GST
11. Stamp Duty
12. Securities Transaction Tax
13. Net Payable/Receivable

**Extraction Rules**:
- Extract values column-wise for each of the three rows
- Preserve positive/negative signs in Net Payable/Receivable columns
- Handle comma-separated numbers (remove commas, convert to float)
- Zero values in Buy or Sell rows indicate absence of that transaction type

## 3. Obligation Data Location

### Page: Last 2nd Page (Bottom Right Side)
**Visual Location**: Bottom right corner of the second-to-last page

**Key Section**: "Pay Out Obligation"

**Text Pattern Structure**:
```
[AMOUNT] Pay out Obligation
[AMOUNT] a) Total brokerage
[AMOUNT] b) Exchange Transaction Charges
[AMOUNT] c) SEBI Turnover Fees
Total Taxable value of supply (a+b+c) [AMOUNT]

CGST*   Rate(percentage%) [RATE]
[AMOUNT1] [AMOUNT2] [AMOUNT3]`

SGST/UTGST*  Rate (percentage%) [RATE]
[AMOUNT1] [AMOUNT2] [AMOUNT3]`

IGST*   Rate(percentage%) [RATE]
[AMOUNT1] [AMOUNT2] [AMOUNT3]`

e) Securities Transaction Tax** ` [AMOUNT]
f) Stamp Duty** ` [AMOUNT]
Net amount receivable by Client ` [AMOUNT]
Net Amount to be Credited in Bank ` [AMOUNT]
```

**Field-Specific Extraction Patterns**:

| Field | Exact Text Pattern | Extraction Method |
|-------|-------------------|-------------------|
| pay_out_obligation | [NUMBER] "Pay out Obligation" | Extract number immediately before text |
| total_brokerage | [NUMBER] "a) Total brokerage" | Extract number immediately before text |
| exchange_transaction_charges | [NUMBER] "b) Exchange Transaction Charges" | Extract number immediately before text |
| sebi_turnover_fees | [NUMBER] "c) SEBI Turnover Fees" | Extract number immediately before text |
| total_taxable_value | "Total Taxable value of supply (a+b+c)" [NUMBER] | Extract number after text |
| cgst_rate | "CGST* Rate(percentage%)" [NUMBER] | Extract percentage |
| sgst_rate | "SGST/UTGST* Rate (percentage%)" [NUMBER] | Extract percentage |
| igst_rate | "IGST* Rate(percentage%)" [NUMBER] | Extract percentage |
| cgst_brokerage_amount | After CGST rate line, first number | Extract first numeric value |
| cgst_charges_amount | After CGST rate line, second number | Extract second numeric value |
| cgst_total_amount | After CGST section, after ` symbol | Extract amount after ` |
| sgst_brokerage_amount | After SGST rate line, first number | Extract first numeric value |
| sgst_charges_amount | After SGST rate line, second number | Extract second numeric value |
| sgst_total_amount | After SGST section, after ` symbol | Extract amount after ` |
| igst_brokerage_amount | After IGST rate line, first number | Extract first numeric value |
| igst_charges_amount | After IGST rate line, second number | Extract second numeric value |
| igst_total_amount | After IGST section, after ` symbol | Extract amount after ` |
| securities_transaction_tax | "e) Securities Transaction Tax** ` [NUMBER] | Extract number after ` |
| stamp_duty | "f) Stamp Duty** ` [NUMBER] | Extract number after ` |
| net_amount_receivable_by_client | "Net amount receivable by Client ` [NUMBER] | Extract number after ` |
| net_amount_to_be_credited_in_bank | "Net Amount to be Credited in Bank ` [NUMBER] | Extract number after ` |

**GST Table Format Notes**:
- GST details appear in multi-column format
- Rates are shown as percentages
- Amounts are typically separated by spaces or tabs
- Final amounts for each GST type appear after the ` symbol

## 4. Common Variations and Troubleshooting

### Format Variations
- Date formats: DD/MM/YYYY, DD-MM-YYYY, DDMonYYYY
- Number formats: With/without commas, different decimal separators
- Label variations: "Total brokerage" vs "Brokerage Total"
- Table layouts: Different column orders in some document versions

### Common Extraction Challenges
1. **Multi-page tables**: Transactions may span multiple pages
2. **Footer/header overlap**: Obligation data may be near page boundaries
3. **Font formatting**: Bold/italic text may affect OCR accuracy
4. **Table borders**: Missing or faint table lines
5. **Alignment issues**: Misaligned columns in transaction tables

### Quality Check Points
- ISIN should always be 12 characters (first 2 letters, rest alphanumeric)
- Transaction quantities should be positive integers
- Prices should be positive decimals
- Net amounts follow sign conventions (negative = receivable, positive = payable)
- GST calculations should be mathematically consistent

## 5. Extraction Sequence Recommendation

1. **First Pass - Document Structure**:
   - Identify total pages
   - Locate header section (page 1)
   - Find transaction tables
   - Locate obligation section (last 2nd page)

2. **Second Pass - Header Data**:
   - Extract contract note details
   - Extract settlement information
   - Note client information location

3. **Third Pass - Transaction Data**:
   - Find "Summary including statutory levies" tables
   - For each table, identify ISIN and security name
   - Extract three rows per security (Buy, Sell, Total)
   - Validate data consistency

4. **Fourth Pass - Obligation Data**:
   - Locate "Pay Out Obligation" section
   - Extract amounts using pattern matching
   - Parse GST table details
   - Extract final settlement amounts

5. **Final Validation**:
   - Check all required fields are present
   - Validate numeric ranges and formats
   - Verify mathematical relationships
   - Ensure JSON structure compliance