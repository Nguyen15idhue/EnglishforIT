# RAG System Improvements - API Key Management

## Changes Made

### 1. **Dynamic API Key Loading** (rag_chain.py)
- Added `get_api_key()` function that reloads .env before each query
- API key is validated and refreshed automatically
- Detects invalid API key formats

### 2. **Retry Logic with Exponential Backoff** (rag_chain.py)
- `query_rag()` now retries failed queries up to 3 times
- Handles different error types:
  - **Quota/Auth errors**: Wait 5 seconds before retry
  - **Timeout errors**: Exponential backoff (1, 2, 4 seconds)
  - **Other errors**: Exponential backoff
- Better error messages for debugging

### 3. **API Key Change Detection** (final_test.py)
- Checks if API key changed between queries
- Automatically rebuilds LLM when API key changes
- No manual reload needed - happens transparently

### 4. **Interactive Commands**
- `reload` - Manually reload RAG chain with new API key
- `exit`, `quit`, `q` - Exit program
- Smart error handling with helpful messages

## How to Use

### Basic Usage
```bash
cd L:\Download\EnglishforIT
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe step/4_generation/final_test.py
```

### Scenario 1: Change API Key Mid-Session
1. Script is running and asking for questions
2. Edit `.env` file with new API key
3. Script will detect change and rebuild chain automatically
4. Or type `reload` to manually trigger rebuild

### Scenario 2: API Quota Exceeded
1. Script shows "[API Key/Quota issue detected]"
2. Update `.env` with new API key
3. Type `reload` to continue
4. Or next question will trigger automatic rebuild

### Scenario 3: Network Timeout
1. Script automatically retries up to 3 times
2. Shows "[Attempt X/3] Timeout error, retrying..."
3. No manual intervention needed

## Files Modified

1. **rag_chain.py**
   - Added `get_api_key()` function
   - Enhanced `query_rag()` with retry logic
   - Added timeout parameter to LLM

2. **final_test.py**
   - Added API key validation at startup
   - Implemented API key change detection
   - Added `reload` command support
   - Better error messages

## Error Handling Examples

**API Key Issue:**
```
[ERROR] API Key Issue:
  - Check if .env file has valid GOOGLE_API_KEY
```

**Quota Exceeded:**
```
[API Error - Your API key may have expired or quota exceeded]
[Please update .env file with a new API key and type 'reload' to continue]
```

**Network Timeout (Auto-Retry):**
```
[Attempt 1/3] Timeout error, retrying in 1s...
[Attempt 2/3] Timeout error, retrying in 2s...
[Attempt 3/3] Timeout error, retrying in 4s...
```

## Testing

To test API key change handling:
1. Start the program
2. Ask a question - it works
3. Change API key in `.env`
4. Ask another question - script detects change and rebuilds
5. Or type `reload` to manually rebuild

To test retry logic:
- Temporarily disconnect network (if testing timeout)
- Script will retry automatically
- Once network is back, query succeeds

## Verbose Mode

For debugging, run with --verbose flag:
```bash
.\.venv\Scripts\python.exe step/4_generation/final_test.py --verbose
```

This shows full traceback for any errors.
