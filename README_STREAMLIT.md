# ISEC Contract Note Data Extractor - Streamlit Application

A user-friendly web interface for extracting structured data from ISEC (ICICI Securities) contract notes using OpenAI's GPT models.

## Features

### 🎯 Core Functionality
- **PDF Upload**: Upload one or more PDF contract notes for processing
- **OpenAI Model Selection**: Choose from multiple GPT models (gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo)
- **Editable Prompts**: Customize both system and position prompts in real-time
- **Live Processing**: Process PDFs and see results immediately
- **JSON Export**: Download extracted data as JSON files

### 📊 Default Display
On initial load, the application displays:
1. **System Prompt** - Full extraction instructions (editable)
2. **Position Prompt** - Minimal/compact prompt (editable)
3. **Result JSON** - Sample extraction result from `chirag_both.json`
4. **PDF Upload Widget** - Ready to accept PDF files

### 🎨 User Interface
- **Two-column layout** for prompts (System Prompt | Position Prompt)
- **Sidebar configuration** with model selection and upload controls
- **Expandable results** for each processed PDF
- **Color-coded status messages** (success, error, warning)
- **Metadata display** showing transaction count, model used, and file size
- **Download buttons** for extracted JSON data

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd pdf_testing_2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Or set the environment variable directly:
   ```bash
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your_openai_api_key_here"
   
   # Windows (Command Prompt)
   set OPENAI_API_KEY=your_openai_api_key_here
   
   # Linux/Mac
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Alternative: Specify Port
```bash
streamlit run app.py --server.port 8080
```

## Usage Guide

### Step 1: Configure Settings
1. Open the **sidebar** (left panel)
2. Select your preferred **OpenAI model** from the dropdown
3. Verify that the **API Key status** shows "✅ API Key Loaded"

### Step 2: Customize Prompts (Optional)
1. Edit the **System Prompt** in the left text area
2. Edit the **Position Prompt** in the right text area
3. Changes are applied immediately when you process a PDF

### Step 3: Upload and Process PDFs
1. Click **"Browse files"** in the sidebar
2. Select one or more PDF files (ISEC contract notes)
3. Click the **"🚀 Process PDF"** button
4. Wait for processing to complete (progress spinner will show)

### Step 4: Review Results
1. Expand the result section for each processed PDF
2. Review the **status** (success/error/warning messages)
3. Check the **metadata** (transaction count, model, file size)
4. Examine the **extracted JSON data**
5. Click **"💾 Download JSON"** to save the results

## Features in Detail

### PDF Size Reduction
- Automatically reduces large PDFs (>0.1MB) by extracting first 2 and last 2 pages
- Reduces API costs and processing time
- Configurable in `config.json`

### Error Handling
- Validates API key presence
- Handles PDF upload errors
- Catches and displays extraction errors
- Shows detailed error messages for debugging

### Real-time Updates
- No page reload required
- Results update immediately after processing
- Session state maintains current results

### Multi-file Support
- Upload and process multiple PDFs in one session
- Each PDF is processed independently
- Results are displayed in expandable sections

## Configuration

### Model Settings
Edit `config.json` to change default settings:
```json
{
  "openai": {
    "default_model": "gpt-4o",
    "max_tokens": 8000,
    "temperature": 0.1
  }
}
```

### PDF Reduction Settings
```json
{
  "pdf_reduction": {
    "enabled": true,
    "max_file_size_mb": 0.1,
    "strategy": "first_and_last_pages",
    "first_pages": 2,
    "last_pages": 2
  }
}
```

## File Structure

```
pdf_testing_2/
├── app.py                          # Main Streamlit application
├── extractor_openai.py             # Backend extraction logic
├── config.json                     # Configuration settings
├── system_prompt.md                # Full system prompt
├── minimal_system_prompt.md        # Compact position prompt
├── compact_schema.json             # JSON schema for extraction
├── chirag_both.json                # Sample result (default display)
├── requirements.txt                # Python dependencies
└── .env                            # Environment variables (create this)
```

## Troubleshooting

### API Key Not Found
**Error**: "❌ API Key Not Found"
**Solution**: 
- Create a `.env` file with `OPENAI_API_KEY=your_key`
- Or set the environment variable before running the app

### PDF Upload Fails
**Error**: "Failed to upload PDF to OpenAI"
**Solution**:
- Check your internet connection
- Verify API key is valid
- Ensure PDF file is not corrupted

### Extraction Errors
**Error**: "Extraction failed: ..."
**Solution**:
- Try a different model (e.g., gpt-4o instead of gpt-3.5-turbo)
- Check if PDF is a valid ISEC contract note
- Review the system and position prompts

### Large PDF Files
**Warning**: "PDF was reduced from X MB to Y MB"
**Solution**: This is normal behavior. The app automatically reduces large PDFs to save costs.

## Advanced Usage

### Custom Prompts
You can create custom extraction prompts for different document types:
1. Edit the prompts in the text areas
2. Save your custom prompts to new files
3. Update `config.json` to use your custom prompt files

### Batch Processing
To process multiple PDFs:
1. Select all PDFs in the file uploader
2. Click "Process PDF" once
3. Results will appear for each file in separate expandable sections

### Export Results
- Click "💾 Download JSON" for individual results
- Results include full metadata and extraction details
- JSON files can be used for further analysis or integration

## Performance Tips

1. **Use gpt-4o-mini** for faster, cheaper processing
2. **Enable PDF reduction** to minimize API costs
3. **Process multiple files** in one session to save time
4. **Customize prompts** to improve extraction accuracy

## Support

For issues or questions:
1. Check the error messages in the app
2. Review the logs in the terminal/console
3. Verify your API key and internet connection
4. Ensure PDFs are valid ISEC contract notes

## License

This application is part of the ISEC Contract Note Data Extraction system.

