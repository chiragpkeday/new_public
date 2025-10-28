# Streamlit Cloud Deployment Guide

## 📋 Pre-Deployment Checklist

### Required Files (Must be in repository)
- [x] `app.py` - Main application
- [x] `requirements.txt` - Python dependencies
- [x] `system_prompt.md` - Full system prompt
- [x] `minimal_system_prompt.md` - Compact prompt
- [x] `config.json` - Configuration
- [x] `compact_schema.json` - JSON schema
- [x] `chirag_both.json` - Sample result
- [x] `.streamlit/config.toml` - Streamlit configuration

### Files to Exclude (Should be in .gitignore)
- [x] `.env` - Local environment variables
- [x] `*.pyc` - Python bytecode
- [x] `__pycache__/` - Python cache

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy ISEC Contract Note Extractor"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub
3. **Click** "New app"
4. **Select**:
   - Repository: `your-username/your-repo-name`
   - Branch: `main`
   - Main file path: `app.py`
5. **Click** "Deploy"

### Step 3: Add Secrets

1. **While app is deploying**, click the **three dots menu (⋮)** > **Settings**
2. **Click** "Secrets" in the left sidebar
3. **Add your OpenAI API key**:
   ```toml
   OPENAI_API_KEY = "sk-your-actual-api-key-here"
   ```
4. **Click** "Save"
5. **App will automatically restart** with the new secrets

### Step 4: Verify Deployment

1. **Wait** for deployment to complete (usually 2-3 minutes)
2. **Check** that the app loads without errors
3. **Verify** API key status shows "✅ API Key Loaded"
4. **Test** by uploading a sample PDF

## 🔧 Troubleshooting

### Error: "Health check failed"

**Cause**: App is crashing during startup

**Solutions**:
1. Check that all required files are in the repository
2. Verify `minimal_system_prompt.md` exists
3. Check Streamlit Cloud logs for specific errors
4. Ensure `requirements.txt` has all dependencies

### Error: "API Key Not Found"

**Cause**: Secrets not configured

**Solution**:
1. Go to App Settings > Secrets
2. Add: `OPENAI_API_KEY = "your-key"`
3. Save and wait for restart

### Error: "Module not found"

**Cause**: Missing dependency in requirements.txt

**Solution**:
1. Add missing package to `requirements.txt`
2. Commit and push changes
3. Streamlit Cloud will auto-redeploy

### Error: "File not found"

**Cause**: Required file missing from repository

**Solution**:
1. Verify all files in checklist above
2. Add missing files
3. Commit and push

## 📊 Monitoring

### View Logs
1. Click **"Manage app"** in Streamlit Cloud
2. Click **"Logs"** tab
3. Monitor for errors or warnings

### Check Status
- **Green dot** = App running
- **Red dot** = App crashed
- **Yellow dot** = App deploying

## 🔐 Security Best Practices

### DO:
- ✅ Use Streamlit Secrets for API keys
- ✅ Add `.env` to `.gitignore`
- ✅ Keep secrets out of code
- ✅ Use environment variables

### DON'T:
- ❌ Commit `.env` file
- ❌ Hardcode API keys
- ❌ Share secrets publicly
- ❌ Commit sensitive data

## 🎯 Post-Deployment

### Test Functionality
1. **Upload PDF** - Test with sample file
2. **Select Model** - Try different models
3. **Edit Prompts** - Verify editing works
4. **Download Results** - Check JSON export
5. **Error Handling** - Test with invalid PDF

### Share Your App
Your app URL will be:
```
https://your-app-name.streamlit.app
```

Share this URL with users!

## 🔄 Updating Your App

### Method 1: Git Push (Recommended)
```bash
# Make changes locally
git add .
git commit -m "Update app"
git push origin main
# Streamlit Cloud auto-deploys
```

### Method 2: Streamlit Cloud UI
1. Go to your app
2. Click "Reboot app" to restart
3. Click "Rerun" to refresh

## 📝 Common Issues & Solutions

### Issue: App is slow
**Solution**: 
- Use `gpt-4o-mini` for faster processing
- Enable PDF reduction (already enabled)
- Check OpenAI API rate limits

### Issue: Large PDFs fail
**Solution**:
- PDF reduction is automatic (>0.1MB)
- Adjust threshold in `config.json`
- Use smaller PDFs for testing

### Issue: Secrets not loading
**Solution**:
1. Verify secrets format (TOML)
2. Check for typos in key name
3. Restart app after adding secrets

## 🎓 Resources

### Streamlit Documentation
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [App Settings](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)

### Your App Documentation
- `QUICKSTART.md` - Quick start guide
- `README_STREAMLIT.md` - Full documentation
- `FEATURES.md` - Feature list

## ✅ Deployment Checklist

Before deploying:
- [ ] All required files committed
- [ ] `.env` in `.gitignore`
- [ ] `requirements.txt` updated
- [ ] Tested locally
- [ ] GitHub repository ready

During deployment:
- [ ] App deployed on Streamlit Cloud
- [ ] Secrets added (OPENAI_API_KEY)
- [ ] App restarted with secrets
- [ ] No errors in logs

After deployment:
- [ ] App loads successfully
- [ ] API key status shows green
- [ ] Test PDF upload works
- [ ] Results display correctly
- [ ] Download works

## 🎉 Success!

Your app is now live at:
```
https://your-app-name.streamlit.app
```

Users can:
- Upload ISEC contract note PDFs
- Select OpenAI models
- Edit prompts in real-time
- Download extracted JSON data

---

**Need Help?**
- Check logs in Streamlit Cloud
- Review error messages in app
- Read troubleshooting section above
- Check Streamlit Community forums

