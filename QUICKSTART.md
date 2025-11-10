# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

**Get your API key:**
- Go to https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy the key and paste it in the `.env` file

### 3. Run the Application

**Option A: Using the run script (Recommended)**
```bash
python run.py
```

**Option B: Directly with Streamlit**
```bash
cd src/app
streamlit run streamlit_frontend.py
```

**Option C: Programmatic usage**
```bash
python example.py
```

### 4. Use the System

Once the Streamlit app opens:

#### Step 1: Upload Reference Documents
1. Go to "📚 Reference Documents" tab
2. Upload IS Codes, CPWD manuals, or standards (PDF format)
3. Click "Process Reference Documents"

#### Step 2: Analyze Tender Documents
1. Go to "🔍 Detect Vagueness" tab
2. Upload tender/specification documents (PDF format)
3. Click "📥 Load Documents" (text extraction only)
4. **NEW:** Select specific document from dropdown
5. **NEW:** Choose page range:
   - Single Page (e.g., page 5)
   - Page Range (e.g., pages 10-15)
   - All Pages (entire document)
6. Click "🔍 Analyze Selection"
7. Review detected vague phrases for selected pages

#### Step 3: Generate Suggestions
1. Go to "💡 Generate Suggestions" tab
2. Click "Generate Suggestions"
3. Review AI-generated improvements
4. Export results as JSON or CSV

## Sample Workflow

### Example Vague Text
```
"The contractor shall use quality materials where possible 
and complete work to a reasonable standard."
```

### System Output
- **Detected Issues:**
  - "quality materials" - Abstractness & Subjective Language
  - "where possible" - Open-Ended Terms
  - "reasonable standard" - Abstractness & Subjective Language

- **Suggested Improvement:**
```
"The contractor shall use materials conforming to IS 383:2016 
for aggregates and IS 456:2000 Grade M25 for concrete, and 
complete work meeting IS 456:2000 specifications for workmanship."
```

## Configuration Options

### In Streamlit Sidebar:
- **API Key**: Enter your Gemini API key
- **Model**: Choose between:
  - `gemini-1.5-pro` (more accurate, slower)
  - `gemini-1.5-flash` (faster, slightly less accurate)
- **Chunk Size**: 300-1000 characters (default: 500)
- **Overlap**: 50-200 characters (default: 100)
- **Threshold**: 0.0-1.0 (default: 0.3)

## Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not found
```
**Solution:** Make sure `.env` file exists with your API key

### Import Errors
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:** Run `pip install -r requirements.txt`

### No PDFs Detected
```
Warning: No documents found
```
**Solution:** 
- Make sure PDFs are in the correct directory
- Check file permissions
- Ensure PDFs are not password-protected

### Memory Issues
```
MemoryError or system slowdown
```
**Solution:**
- Reduce chunk size in settings
- Process fewer documents at once
- Use `gemini-1.5-flash` instead of `gemini-1.5-pro`

## Tips for Best Results

1. **Reference Documents:**
   - Upload actual IS Codes and standards for better suggestions
   - Include CPWD specifications relevant to your domain
   - More reference documents = better suggestions

2. **Tender Documents:**
   - Ensure text is extractable (not scanned images)
   - Break very large documents into sections
   - Remove irrelevant pages before processing

3. **Detection Threshold:**
   - Lower threshold (0.2-0.3): Catches more issues, may have false positives
   - Higher threshold (0.5-0.7): More conservative, fewer false positives
   - Default (0.3): Balanced approach

4. **Model Selection:**
   - Use `gemini-1.5-pro` for final analysis
   - Use `gemini-1.5-flash` for quick checks and testing

## Directory Structure

```
mtp_v2/
├── data/
│   ├── raw_docs/          # Put tender PDFs here
│   ├── reference_docs/    # Put IS Codes/standards here
│   └── embeddings/        # Auto-generated (don't modify)
├── outputs/               # Results saved here
└── src/                   # Source code (don't modify)
```

## Next Steps

1. **Add Your Documents:**
   - Place tender PDFs in `data/raw_docs/`
   - Place reference PDFs in `data/reference_docs/`

2. **Run Analysis:**
   - Process documents through the web interface
   - Review and export results

3. **Customize:**
   - Adjust thresholds based on your needs
   - Try different models for comparison

4. **Export Results:**
   - Use JSON for programmatic processing
   - Use CSV for spreadsheet analysis

## Support

For issues or questions:
1. Check the main README.md
2. Review the troubleshooting section above
3. Check that all dependencies are installed
4. Verify your API key is valid and has quota

## Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **ChromaDB Docs**: https://docs.trychroma.com

---

**Ready to start? Run `python run.py` now!** 🚀
