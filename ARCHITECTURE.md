# Application Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB APPLICATION                    │
│                         (app.py)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │Configuration │
│   (Streamlit)│    │   (OpenAI)   │    │   (Files)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Component Architecture

### 1. Frontend Layer (Streamlit UI)

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Sidebar    │  │ Main Content │  │Session State │ │
│  │              │  │              │  │              │ │
│  │ • Model      │  │ • Prompts    │  │ • Results    │ │
│  │ • Upload     │  │ • Results    │  │ • Config     │ │
│  │ • Process    │  │ • Download   │  │ • Cache      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. Processing Layer

```
┌─────────────────────────────────────────────────────────┐
│                  PROCESSING PIPELINE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. PDF Upload                                          │
│     ↓                                                   │
│  2. Size Check & Reduction                              │
│     ↓                                                   │
│  3. Upload to OpenAI                                    │
│     ↓                                                   │
│  4. Prepare Prompts                                     │
│     ↓                                                   │
│  5. API Request                                         │
│     ↓                                                   │
│  6. Parse Response                                      │
│     ↓                                                   │
│  7. Validate Data                                       │
│     ↓                                                   │
│  8. Display Results                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Data Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   User   │────▶│Streamlit │────▶│  OpenAI  │────▶│  Result  │
│  Upload  │     │   App    │     │   API    │     │   JSON   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                 │                │
     │                │                 │                │
     ▼                ▼                 ▼                ▼
  PDF File      Process PDF      Extract Data      Download
```

## Detailed Component Breakdown

### Frontend Components

#### 1. Sidebar
```python
st.sidebar
├── header("⚙️ Configuration")
├── selectbox("OpenAI Model")
├── success/error("API Key Status")
├── divider()
├── header("📤 Upload PDF")
├── file_uploader()
└── button("🚀 Process PDF")
```

#### 2. Main Content
```python
st.main
├── title("📄 ISEC Contract Note Data Extractor")
├── columns([col1, col2])
│   ├── col1: text_area("System Prompt")
│   └── col2: text_area("Position Prompt")
├── header("📊 Extraction Results")
└── json(result) + download_button()
```

#### 3. Session State
```python
st.session_state
├── result: Dict (current extraction result)
└── processing: bool (processing status)
```

### Backend Functions

#### 1. Data Loading
```python
@st.cache_data
├── load_default_system_prompt()
├── load_default_position_prompt()
├── load_default_result()
├── load_config()
└── load_compact_schema()
```

#### 2. PDF Processing
```python
process_pdf()
├── validate_api_key()
├── check_file_size()
├── reduce_pdf_size() [if needed]
├── upload_pdf_to_openai()
├── extract_with_openai()
└── create_result()
```

#### 3. OpenAI Integration
```python
extract_with_openai()
├── prepare_extraction_prompt()
├── create_chat_completion()
├── parse_json_response()
└── handle_errors()
```

### Configuration Layer

#### 1. Application Config (config.json)
```json
{
  "openai": {
    "default_model": "gpt-4o",
    "max_tokens": 8000,
    "temperature": 0.1
  },
  "pdf_reduction": {
    "enabled": true,
    "max_file_size_mb": 0.1
  }
}
```

#### 2. Streamlit Config (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"

[server]
port = 8501
```

#### 3. Environment (.env)
```bash
OPENAI_API_KEY=sk-...
```

## Data Models

### Input Data
```python
{
  "pdf_file": UploadedFile,
  "system_prompt": str,
  "position_prompt": str,
  "model": str,
  "config": Dict
}
```

### Processing Data
```python
{
  "file_id": str,
  "original_size": int,
  "reduced_size": int,
  "pdf_path": str
}
```

### Output Data
```python
{
  "success": bool,
  "data": {
    "header": {...},
    "transactions": [...],
    "obligations": {...}
  },
  "errors": [...],
  "warnings": [...],
  "metadata": {...}
}
```

## Process Flow Diagram

### Complete Processing Flow

```
START
  │
  ├─▶ Load Defaults
  │   ├─ System Prompt
  │   ├─ Position Prompt
  │   ├─ Sample Result
  │   └─ Configuration
  │
  ├─▶ User Interaction
  │   ├─ Select Model
  │   ├─ Edit Prompts (optional)
  │   └─ Upload PDF(s)
  │
  ├─▶ Validation
  │   ├─ Check API Key
  │   ├─ Validate File Type
  │   └─ Check File Size
  │
  ├─▶ Pre-Processing
  │   ├─ Size Check
  │   └─ Reduce PDF (if needed)
  │
  ├─▶ OpenAI Processing
  │   ├─ Upload PDF
  │   ├─ Prepare Prompts
  │   ├─ API Request
  │   └─ Parse Response
  │
  ├─▶ Post-Processing
  │   ├─ Validate Data
  │   ├─ Create Metadata
  │   └─ Format Result
  │
  ├─▶ Display
  │   ├─ Show Status
  │   ├─ Display JSON
  │   └─ Enable Download
  │
  └─▶ Cleanup
      └─ Delete Temp Files
  │
END
```

## Error Handling Flow

```
┌─────────────────┐
│  User Action    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │◀─── API Key Check
└────────┬────────┘     File Type Check
         │              Size Check
         ▼
┌─────────────────┐
│   Processing    │◀─── Upload Error
└────────┬────────┘     API Error
         │              Parse Error
         ▼
┌─────────────────┐
│ Error Handler   │
└────────┬────────┘
         │
         ├─▶ Log Error
         ├─▶ Display Message
         └─▶ Return Gracefully
```

## State Management

### Session State Flow

```
Initial Load
  │
  ├─▶ st.session_state.result = default_result
  └─▶ st.session_state.processing = False
  │
User Uploads PDF
  │
  └─▶ st.session_state.processing = True
  │
Processing Complete
  │
  ├─▶ st.session_state.result = new_result
  └─▶ st.session_state.processing = False
  │
Display Updated
```

## Caching Strategy

```python
# Static Data (cached)
@st.cache_data
├── Default Prompts (rarely change)
├── Configuration (rarely change)
├── Schema (rarely change)
└── Sample Result (rarely change)

# Dynamic Data (not cached)
├── User Uploads (always new)
├── Processing Results (always new)
└── Session State (per session)
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│          Security Layers                │
├─────────────────────────────────────────┤
│                                         │
│  1. Environment Variables               │
│     └─ API Key (not in code)            │
│                                         │
│  2. File Validation                     │
│     └─ PDF type check                   │
│                                         │
│  3. Temporary Files                     │
│     └─ Auto cleanup                     │
│                                         │
│  4. XSRF Protection                     │
│     └─ Enabled in config                │
│                                         │
│  5. Secure Communication                │
│     └─ HTTPS to OpenAI                  │
│                                         │
└─────────────────────────────────────────┘
```

## Performance Optimization

### 1. Caching
- Default data cached with `@st.cache_data`
- Reduces load time on subsequent runs
- Invalidates on file changes

### 2. Session State
- Results persist during session
- No re-processing on UI interactions
- Efficient state updates

### 3. PDF Reduction
- Automatic for large files
- Reduces API costs
- Faster processing

### 4. Lazy Loading
- JSON rendered on demand
- Expandable sections
- Efficient memory usage

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Local Development               │
├─────────────────────────────────────────┤
│  python -m streamlit run app.py         │
│  └─▶ http://localhost:8501              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Production Deployment           │
├─────────────────────────────────────────┤
│  Streamlit Cloud / Docker / Server      │
│  └─▶ https://your-domain.com            │
└─────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│          Technology Stack               │
├─────────────────────────────────────────┤
│                                         │
│  Frontend:                              │
│  └─ Streamlit 1.39.0                    │
│                                         │
│  Backend:                               │
│  ├─ Python 3.8+                         │
│  ├─ OpenAI API 1.51.2                   │
│  └─ pypdf 4.2.0                         │
│                                         │
│  Configuration:                         │
│  ├─ JSON (config.json)                  │
│  ├─ TOML (.streamlit/config.toml)       │
│  └─ ENV (.env)                          │
│                                         │
│  Documentation:                         │
│  └─ Markdown (.md files)                │
│                                         │
└─────────────────────────────────────────┘
```

## Integration Points

### 1. OpenAI API
```
app.py ──▶ OpenAI Client ──▶ GPT Models
   │           │                  │
   │           │                  │
   ▼           ▼                  ▼
File Upload  API Request    JSON Response
```

### 2. File System
```
app.py ──▶ Read Config Files
   │
   ├─▶ system_prompt.md
   ├─▶ minimal_system_prompt.md
   ├─▶ config.json
   ├─▶ compact_schema.json
   └─▶ chirag_both.json
```

### 3. Environment
```
app.py ──▶ Load .env ──▶ OPENAI_API_KEY
```

## Scalability Considerations

### Current Design
- Single user per session
- Sequential PDF processing
- Local file storage

### Future Enhancements
- Multi-user support
- Parallel processing
- Cloud storage integration
- Database for results
- API endpoints

## Monitoring & Logging

```
┌─────────────────────────────────────────┐
│          Logging Architecture           │
├─────────────────────────────────────────┤
│                                         │
│  Console Logs:                          │
│  ├─ INFO: Processing status             │
│  ├─ WARNING: Non-critical issues        │
│  └─ ERROR: Critical failures            │
│                                         │
│  UI Messages:                           │
│  ├─ Success: Green boxes                │
│  ├─ Warning: Yellow boxes               │
│  └─ Error: Red boxes                    │
│                                         │
│  Metadata:                              │
│  ├─ Extraction timestamp                │
│  ├─ Model used                          │
│  ├─ File sizes                          │
│  └─ Processing stats                    │
│                                         │
└─────────────────────────────────────────┘
```

This architecture provides a solid foundation for the ISEC Contract Note Extractor, with clear separation of concerns, robust error handling, and room for future enhancements.

