# Quick Start Guide - ISEC Contract Note Extractor

Get started with the Streamlit application in 3 simple steps!

## 🚀 Quick Start (3 Steps)

### Step 1: Set Your API Key

Create a `.env` file in this directory with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**Don't have an API key?** Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the App

**Windows:**
```bash
run_app.bat
```
Or:
```bash
streamlit run app.py
```

**Linux/Mac:**
```bash
chmod +x run_app.sh
./run_app.sh
```
Or:
```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📖 Using the App

### First Time Use

1. **Check API Key Status** - Look for "✅ API Key Loaded" in the sidebar
2. **Review Default Prompts** - The system and position prompts are pre-loaded
3. **See Sample Result** - A sample extraction result is displayed by default

### Processing Your First PDF

1. **Select Model** - Choose an OpenAI model (default: gpt-4o)
2. **Upload PDF** - Click "Browse files" and select your ISEC contract note PDF
3. **Click Process** - Hit the "🚀 Process PDF" button
4. **View Results** - Expand the result section to see extracted data
5. **Download** - Click "💾 Download JSON" to save the results

## 🎯 What You'll See

### Default Display (Before Processing)
- **Left Panel**: System Prompt (full extraction instructions)
- **Right Panel**: Position Prompt (minimal/compact prompt)
- **Bottom**: Sample result JSON from `chirag_both.json`

### After Processing
- **Status Messages**: Success/Error/Warning indicators
- **Metadata**: Transaction count, model used, file size
- **Extracted Data**: Complete JSON with all extracted fields
- **Download Button**: Save results as JSON file

## ⚙️ Configuration

### Available Models
- `gpt-4o` (default, recommended)
- `gpt-4o-mini` (faster, cheaper)
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

### Editing Prompts
- **System Prompt**: Full instructions for the AI model
- **Position Prompt**: Compact extraction guidelines
- Both are editable in real-time - just type in the text areas!

### PDF Size Limits
- PDFs larger than 0.1MB are automatically reduced
- Only first 2 and last 2 pages are used (contains all needed data)
- This saves API costs and processing time

## 💡 Tips

1. **Start with gpt-4o** - Best balance of quality and speed
2. **Try gpt-4o-mini** - If you need faster/cheaper processing
3. **Edit prompts carefully** - The default prompts are optimized for ISEC contract notes
4. **Process multiple PDFs** - Upload several files at once for batch processing
5. **Download results** - Save JSON files for record-keeping or further analysis

## 🔧 Troubleshooting

### "API Key Not Found"
- Create a `.env` file with `OPENAI_API_KEY=your_key`
- Or set environment variable: `export OPENAI_API_KEY=your_key` (Linux/Mac) or `$env:OPENAI_API_KEY="your_key"` (Windows PowerShell)

### "Failed to upload PDF"
- Check internet connection
- Verify API key is valid
- Ensure PDF is not corrupted

### "Extraction failed"
- Try a different model (gpt-4o recommended)
- Check if PDF is a valid ISEC contract note
- Review error message for specific details

### App won't start
- Ensure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for port conflicts (default: 8501)

## 📁 Sample Files

The project includes sample files for testing:
- `both.pdf` - Sample ISEC contract note
- `chirag22.pdf` - Another sample contract note
- `chirag_both.json` - Sample extraction result (displayed by default)

Try processing these files first to see how the app works!

## 🎓 Next Steps

1. **Read the full README** - See `README_STREAMLIT.md` for detailed documentation
2. **Customize prompts** - Experiment with different prompt variations
3. **Batch process** - Upload multiple PDFs to process them all at once
4. **Export results** - Download JSON files for integration with other systems

## 📞 Need Help?

- Check error messages in the app (they're usually helpful!)
- Review logs in the terminal/console where you ran the app
- Ensure your PDFs are valid ISEC contract notes
- Verify your OpenAI API key has sufficient credits

---

**Ready to extract data?** Run the app and start processing! 🚀

