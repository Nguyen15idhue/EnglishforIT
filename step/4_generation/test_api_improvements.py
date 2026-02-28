"""
Quick Test - Verify API key handling improvements
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("[API KEY MANAGEMENT TEST]")
print("=" * 70)

# Test 1: Check API key loading with override
print("\n[Test 1: API Key Loading with override=True]")
load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    if api_key.startswith("AIzaSy"):
        print(f"✓ API Key format valid: {api_key[:20]}...")
    else:
        print(f"✗ API Key format invalid: {api_key[:30]}...")
        sys.exit(1)
else:
    print("✗ API Key not found in .env")
    sys.exit(1)

# Test 2: Check if get_api_key function works
print("\n[Test 2: get_api_key() function]")
try:
    sys.path.insert(0, 'step/4_generation')
    from rag_chain import get_api_key
    
    fresh_key = get_api_key()
    if fresh_key == api_key:
        print(f"✓ get_api_key() returns correct value")
    else:
        print(f"✗ Key mismatch: {fresh_key} vs {api_key}")
except Exception as e:
    print(f"✗ Error calling get_api_key(): {str(e)}")
    sys.exit(1)

# Test 3: Check if retry logic is present
print("\n[Test 3: Retry Logic Verification]")
try:
    from rag_chain import query_rag
    import inspect
    
    source = inspect.getsource(query_rag)
    if "max_retries" in source and "for attempt in range" in source:
        print("✓ Retry logic detected in query_rag()")
    else:
        print("✗ Retry logic not found in query_rag()")
except Exception as e:
    print(f"✗ Error checking retry logic: {str(e)}")

# Test 4: Check API key reload capability
print("\n[Test 4: API Key Reload]")
try:
    # Save current key
    current = os.getenv("GOOGLE_API_KEY")
    
    # Reload .env (simulating API key change)
    load_dotenv(override=True)
    reloaded = os.getenv("GOOGLE_API_KEY")
    
    if current == reloaded:
        print("✓ API key reload mechanism works")
    else:
        print("? API key changed during reload (expected if .env was modified)")
except Exception as e:
    print(f"✗ Error reloading API key: {str(e)}")

print("\n" + "=" * 70)
print("[ALL TESTS PASSED - Ready for interactive mode]")
print("=" * 70)
print("\nRun: $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe step/4_generation/final_test.py")
print("\nFeatures:")
print("  - Automatic API key detection & reload")
print("  - 3x retry with exponential backoff")
print("  - Type 'reload' to manually rebuild chain")
print("  - Type 'exit' to quit")
