# Debugging Guide for Render Deployment

## Issue: Chatbot Timeout / LLM Connection Failure

### What We've Added

1. **Comprehensive Logging**: Added detailed print statements throughout the QA initialization and query process
2. **Better Error Handling**: Specific error types are now caught and logged separately
3. **Health Check Endpoint**: Added `/health` endpoint to verify deployment status
4. **Timeout Protection**: Added 30-second timeout to OpenAI API calls

### How to Debug

#### Step 1: Check Health Endpoint

Visit: `https://your-app.onrender.com/health`

This will show:
- ✅ If `responses.json` exists
- ✅ If `softdel_index` directory exists  
- ✅ If `OPENAI_API_KEY` is set correctly

**Expected Response:**
```json
{
  "status": "ok",
  "checks": {
    "responses.json": true,
    "softdel_index": true,
    "OPENAI_API_KEY": true
  }
}
```

#### Step 2: Check Render Logs

In Render Dashboard → Your Service → Logs

Look for these log messages:

**During Initialization (first QA call):**
- `🔄 Initializing QA components...`
- `🔑 API Key check: Found` or `NOT FOUND`
- `✅ OpenAI API key set`
- `📁 Looking for FAISS index at: ...`
- `✅ FAISS index loaded successfully`
- `✅ OpenAI LLM initialized`
- `✅ QA components initialization complete!`

**During Query Processing:**
- `🔍 Processing query: ...`
- `🔍 Retrieving relevant documents...`
- `✅ Retrieved X documents`
- `🤖 Calling OpenAI API...`
- `✅ Received response from OpenAI`

**If Errors Occur:**
- `❌ Error loading embeddings: ...`
- `❌ Error loading FAISS index: ...`
- `❌ Error initializing OpenAI LLM: ...`
- `❌ Error calling OpenAI API: ...`

#### Step 3: Common Issues and Solutions

##### Issue 1: API Key Not Set
**Symptoms:**
- Logs show: `🔑 API Key check: NOT FOUND`
- Health check shows: `"OPENAI_API_KEY": false`

**Solution:**
1. Go to Render Dashboard → Your Service → Environment
2. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)
3. Redeploy

##### Issue 2: FAISS Index Not Found
**Symptoms:**
- Logs show: `❌ FAISS index not found at ...`
- Health check shows: `"softdel_index": false`

**Solution:**
1. Ensure `softdel_index/` directory is in your repository
2. Check `.gitignore` - make sure it's NOT ignoring `softdel_index/`
3. Verify the directory contains `index.faiss` and `index.pkl` files
4. Commit and push if missing

##### Issue 3: Network/API Timeout
**Symptoms:**
- Logs show: `🤖 Calling OpenAI API...` but no response
- Timeout error after 30 seconds

**Solution:**
1. Check if OpenAI API is accessible from Render (should be fine)
2. Verify API key is valid and has credits
3. Check Render logs for network errors
4. May need to increase timeout (currently 30 seconds)

##### Issue 4: Embeddings Model Download Failing
**Symptoms:**
- Logs show: `❌ Error loading embeddings: ...`
- First initialization takes too long

**Solution:**
1. This is normal on first run - HuggingFace downloads the model
2. Subsequent runs should be faster (model cached)
3. If persistent, check Render logs for network issues

### Testing Locally

Before deploying, test locally:

```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Run the app
python main.py

# In another terminal, test health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "hello"}'
```

### Next Steps

1. **Deploy these changes** to Render
2. **Check the health endpoint** to verify all components
3. **Monitor Render logs** during first QA call
4. **Share the logs** if issues persist - the detailed logging will help identify the exact problem

### Files Modified

- `qanstest.py`: Added comprehensive logging and error handling
- `main.py`: Added health check endpoint and better error handling
