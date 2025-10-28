#!/usr/bin/env python3
"""
Streamlit Application for ISEC Contract Note Data Extraction

A web interface for extracting financial data from ISEC (ICICI Securities) contract notes
using OpenAI API with editable prompts and real-time processing.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
from extractor_openai import ISECAPIExtractor, ExtractionResult

# Configure page
st.set_page_config(
    page_title="ISEC Contract Note Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file."""
    config_path = Path(__file__).parent / 'config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Configuration file not found: config.json")
        return {}

def load_system_prompt() -> str:
    """Load the system prompt from file."""
    config = load_config()
    if not config:
        return ""

    prompt_file = config["files"]["system_prompt"]
    prompt_path = Path(__file__).parent / prompt_file
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"System prompt file not found: {prompt_file}")
        return ""

def load_position_prompt() -> str:
    """Load the position prompt (using minimal prompt as position prompt)."""
    config = load_config()
    if not config:
        return ""

    prompt_file = config["files"]["system_prompt"]  # Using minimal as position prompt
    prompt_path = Path(__file__).parent / prompt_file
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Position prompt file not found: {prompt_file}")
        return ""

def main():
    """Main Streamlit application."""
    st.title("📄 ISEC Contract Note Data Extractor")
    st.markdown("Extract structured financial data from ISEC (ICICI Securities) contract notes using OpenAI.")

    # Initialize session state
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    # Load default prompts
    default_system_prompt = load_system_prompt()
    default_position_prompt = load_position_prompt()

    # Create two columns layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Configuration")

        # System Prompt
        st.subheader("System Prompt")
        system_prompt = st.text_area(
            "Edit the system prompt:",
            value=default_system_prompt,
            height=200,
            key="system_prompt",
            help="Instructions for the AI model on how to extract data"
        )

        # Position Prompt
        st.subheader("Position Prompt")
        position_prompt = st.text_area(
            "Edit the position prompt:",
            value=default_position_prompt,
            height=200,
            key="position_prompt",
            help="Additional context or instructions for data extraction"
        )

        # OpenAI Model Selection
        st.subheader("OpenAI Model")
        available_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        selected_model = st.selectbox(
            "Choose OpenAI model:",
            options=available_models,
            index=0,
            help="Select the OpenAI model for data extraction"
        )

        # PDF Upload
        st.subheader("PDF Upload")
        uploaded_files = st.file_uploader(
            "Upload PDF files:",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more ISEC contract note PDF files"
        )

        # Process Button
        if st.button("🔍 Extract Data", type="primary", use_container_width=True):
            if not uploaded_files:
                st.error("Please upload at least one PDF file.")
            elif not system_prompt.strip():
                st.error("Please provide a system prompt.")
            else:
                process_pdfs(uploaded_files, system_prompt, position_prompt, selected_model)

    with col2:
        st.header("Results")

        # Display processing status
        if st.session_state.processing_status:
            if st.session_state.processing_status == "processing":
                st.info("🔄 Processing PDFs... Please wait.")
            elif st.session_state.processing_status == "completed":
                st.success("✅ Processing completed!")
            elif st.session_state.processing_status == "error":
                st.error("❌ Processing failed. Check errors below.")

        # Display extracted data
        if st.session_state.extracted_data:
            st.subheader("Extracted JSON Data")
            st.json(st.session_state.extracted_data)
        else:
            st.info("No data extracted yet. Upload PDFs and click 'Extract Data' to begin.")

def process_pdfs(uploaded_files: List[Any], system_prompt: str, position_prompt: str, model: str):
    """Process uploaded PDF files and extract data."""
    try:
        st.session_state.processing_status = "processing"

        # Save uploaded files temporarily
        temp_files = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_files.append(tmp_file.name)

        # Initialize extractor with custom prompts
        extractor = ISECAPIExtractor(model=model)

        # For now, process only the first file (can be extended for multiple files)
        pdf_path = temp_files[0]

        # Extract data
        result = extractor.extract_from_pdf(pdf_path)

        # Store results
        if result.success:
            st.session_state.extracted_data = result.data
            st.session_state.processing_status = "completed"
        else:
            st.session_state.extracted_data = {"errors": result.errors}
            st.session_state.processing_status = "error"

        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")
        st.session_state.processing_status = "error"
        st.session_state.extracted_data = {"error": str(e)}

if __name__ == "__main__":
    main()