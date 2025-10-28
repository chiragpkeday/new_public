# Streamlit App Layout Documentation

## Application Structure

The ISEC Contract Note Extractor Streamlit application has a clean, intuitive layout designed for ease of use.

## Main Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📄 ISEC Contract Note Data Extractor                                   │
│  Extract structured data from ISEC (ICICI Securities) contract notes    │
│  using OpenAI                                                           │
├──────────────┬──────────────────────────────────────────────────────────┤
│              │                                                           │
│  SIDEBAR     │  MAIN CONTENT AREA                                       │
│              │                                                           │
│  ⚙️ Config   │  ┌─────────────────────┬─────────────────────┐          │
│              │  │  📝 System Prompt   │  🎯 Position Prompt │          │
│  Model:      │  │                     │                     │          │
│  [gpt-4o ▼]  │  │  [Editable Text     │  [Editable Text     │          │
│              │  │   Area - 300px      │   Area - 300px      │          │
│  ✅ API Key  │  │   height]           │   height]           │          │
│  Loaded      │  │                     │                     │          │
│              │  │  Full extraction    │  Minimal/compact    │          │
│  ─────────   │  │  instructions       │  prompt             │          │
│              │  │                     │                     │          │
│  📤 Upload   │  └─────────────────────┴─────────────────────┘          │
│  PDF         │                                                           │
│              │  📊 Extraction Results                                   │
│  [Browse     │  ┌─────────────────────────────────────────────────┐    │
│   files]     │  │  📄 Current Result (JSON)                       │    │
│              │  │                                                 │    │
│  🚀 Process  │  │  {                                              │    │
│  PDF         │  │    "success": true,                             │    │
│              │  │    "data": {                                    │    │
│              │  │      "header": { ... },                         │    │
│              │  │      "transactions": [ ... ],                   │    │
│              │  │      "obligations": { ... }                     │    │
│              │  │    },                                           │    │
│              │  │    "metadata": { ... }                          │    │
│              │  │  }                                              │    │
│              │  │                                                 │    │
│              │  │  💾 Download Current Result                     │    │
│              │  └─────────────────────────────────────────────────┘    │
│              │                                                           │
└──────────────┴──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Header Section
- **Title**: "📄 ISEC Contract Note Data Extractor"
- **Subtitle**: Brief description of the application
- **Full width** across the top of the page

### 2. Sidebar (Left Panel)

#### Configuration Section
```
⚙️ Configuration
├── OpenAI Model Dropdown
│   ├── gpt-4o (default)
│   ├── gpt-4o-mini
│   ├── gpt-4-turbo
│   ├── gpt-4
│   └── gpt-3.5-turbo
│
├── API Key Status
│   ├── ✅ API Key Loaded (green)
│   └── ❌ API Key Not Found (red)
│
├── Divider
│
├── 📤 Upload PDF Section
│   ├── File uploader widget
│   └── Accepts multiple PDFs
│
└── 🚀 Process PDF Button
    ├── Primary button (blue)
    ├── Full width
    └── Disabled if no files or no API key
```

### 3. Main Content Area

#### Prompts Section (Two Columns)
```
┌─────────────────────────┬─────────────────────────┐
│  📝 System Prompt       │  🎯 Position Prompt     │
├─────────────────────────┼─────────────────────────┤
│  Editable text area     │  Editable text area     │
│  Height: 300px          │  Height: 300px          │
│  Monospace font         │  Monospace font         │
│  Default: Full prompt   │  Default: Minimal prompt│
│  from system_prompt.md  │  from minimal_system_   │
│                         │  prompt.md              │
└─────────────────────────┴─────────────────────────┘
```

#### Results Section
```
📊 Extraction Results
├── Before Processing:
│   ├── "📄 Current Result (JSON)"
│   ├── JSON viewer (st.json)
│   ├── Shows default result from chirag_both.json
│   └── 💾 Download Current Result button
│
└── After Processing:
    ├── Expandable section per PDF
    │   ├── Processing: filename.pdf
    │   ├── Status indicator
    │   │   ├── ✅ Success (green box)
    │   │   ├── ❌ Error (red box)
    │   │   └── ⚠️ Warning (yellow box)
    │   │
    │   ├── Metadata (3 columns)
    │   │   ├── Transactions count
    │   │   ├── Model used
    │   │   └── File size
    │   │
    │   ├── 📄 Extracted Data (JSON)
    │   │   └── JSON viewer (st.json)
    │   │
    │   └── 💾 Download JSON button
    │
    └── Multiple PDFs = Multiple expandable sections
```

## Color Scheme

### Status Indicators
- **Success**: Green background (#d4edda), green border (#c3e6cb), dark green text (#155724)
- **Error**: Red background (#f8d7da), red border (#f5c6cb), dark red text (#721c24)
- **Warning**: Yellow background (#fff3cd), yellow border (#ffeaa7), dark yellow text (#856404)

### Theme Colors
- **Primary**: #FF4B4B (Streamlit red)
- **Background**: #FFFFFF (white)
- **Secondary Background**: #F0F2F6 (light gray)
- **Text**: #262730 (dark gray)

## Interactive Elements

### Buttons
1. **Process PDF** (Primary)
   - Blue background
   - Full width in sidebar
   - Disabled state when no files/API key

2. **Download JSON** (Secondary)
   - Default Streamlit button style
   - Appears below each result
   - Triggers file download

### Input Fields
1. **Model Selector**
   - Dropdown/selectbox
   - Shows available models
   - Default: gpt-4o

2. **File Uploader**
   - Drag-and-drop or browse
   - Multiple file support
   - PDF files only

3. **Text Areas**
   - Monospace font
   - Scrollable
   - Real-time editing
   - 300px height

## User Flow

### Initial Load
```
1. App loads
   ↓
2. Default prompts displayed
   ↓
3. Default result JSON shown
   ↓
4. User sees upload widget
   ↓
5. Ready to process
```

### Processing Flow
```
1. User selects model
   ↓
2. User uploads PDF(s)
   ↓
3. (Optional) User edits prompts
   ↓
4. User clicks "Process PDF"
   ↓
5. Spinner shows "Processing..."
   ↓
6. Results appear in expandable sections
   ↓
7. User reviews data
   ↓
8. User downloads JSON
```

## Responsive Design

### Desktop (Wide Screen)
- Two-column layout for prompts
- Sidebar visible by default
- Full JSON viewer width

### Tablet/Mobile
- Single column layout
- Collapsible sidebar
- Scrollable content areas

## Loading States

### Processing Indicator
```
⏳ Processing filename.pdf...
[Spinner animation]
```

### Success State
```
✅ Extraction completed successfully!

📋 Metadata
┌──────────────┬──────────┬──────────┐
│ Transactions │  Model   │ File Size│
│      5       │  gpt-4o  │ 0.08 MB  │
└──────────────┴──────────┴──────────┘

📄 Extracted Data (JSON)
{ ... }

💾 Download JSON
```

### Error State
```
❌ Extraction completed with errors

Error: Failed to parse PDF
Error: Missing required field: contract_note_no

📄 Partial Data (JSON)
{ ... }
```

## Accessibility Features

1. **Clear Labels**: All inputs have descriptive labels
2. **Status Messages**: Color-coded with icons
3. **Help Text**: Tooltips on hover
4. **Keyboard Navigation**: Full keyboard support
5. **Screen Reader**: Semantic HTML structure

## Performance Optimizations

1. **Caching**: Default data cached with @st.cache_data
2. **Session State**: Results persist across interactions
3. **Lazy Loading**: JSON rendered on demand
4. **Efficient Updates**: Only changed sections re-render

## File Size Display

### Before Reduction
```
Original: 0.25 MB
```

### After Reduction
```
⚠️ PDF was reduced from 0.25MB to 0.08MB

Original: 0.25 MB → Reduced: 0.08 MB (68% reduction)
```

## Metadata Display

```
📋 Metadata
┌─────────────────┬──────────────┬─────────────┐
│  Transactions   │    Model     │  File Size  │
│       5         │   gpt-4o     │   0.08 MB   │
└─────────────────┴──────────────┴─────────────┘

Additional Info:
• Extraction Time: 2025-10-28T14:34:36
• File ID: file-R5dwLZyN2x3zyVxzW3xWCJ
• Validation Errors: 0
```

## Download Functionality

### Download Button
```
💾 Download JSON
├── Filename: {original_name}_extracted.json
├── Format: Pretty-printed JSON (indent=2)
└── MIME type: application/json
```

## Error Handling Display

### API Key Missing
```
❌ API Key Not Found
ℹ️ Set OPENAI_API_KEY environment variable
```

### Upload Failed
```
❌ Failed to upload PDF to OpenAI
• Check internet connection
• Verify API key is valid
```

### Extraction Failed
```
❌ Extraction failed: Invalid JSON response
• Try a different model
• Check PDF format
• Review prompts
```

This layout provides a clean, professional interface that guides users through the extraction process while maintaining flexibility for customization.

