"""
FINAL TEST - Test RAG chain with gemini-2.5-flash
Safe: Only 1 query to confirm everything works
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 70)
print("[FINAL TEST - RAG CHAIN WITH GEMINI 2.5 FLASH]")
print("=" * 70)

# Check API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: API key not found in .env")
    sys.exit(1)

# Validate API key format
if api_key.startswith("GOOGLE_API_KEY="):
    print("ERROR: API key contains variable name - invalid .env format")
    print(f"Expected: GOOGLE_API_KEY=AIzaSy...")
    print(f"Got: {api_key[:40]}...")
    sys.exit(1)

if not api_key.startswith("AIzaSy"):
    print("WARNING: API key format looks unusual (should start with AIzaSy)")

print(f"[API Key validated: {api_key[:15]}...]")

try:
    print("\n[Loading RAG chain...]")
    
    # Add step/4_generation to path
    import sys
    sys.path.insert(0, 'step/4_generation')
    
    from rag_chain import build_rag_chain, query_rag, format_output, get_api_key
    
    # Build initial chain
    qa_chain = build_rag_chain(temperature=0.1, top_k=5)
    last_api_key = get_api_key()
    
    print("\n" + "=" * 70)
    print("[RAG CHAIN READY - Enter your questions below]")
    print("[Type 'exit' or 'quit' to stop]")
    print("[Type 'reload' to reload chain with new API key]")
    print("=" * 70)
    
    # Interactive loop
    while True:
        try:
            test_query = input("\n[Your question]: ").strip()
            
            if not test_query:
                print("[Please enter a valid question]")
                continue
            
            # Handle special commands
            if test_query.lower() in ['exit', 'quit', 'q']:
                print("\n[Exiting RAG system...]")
                break
            
            if test_query.lower() == 'reload':
                print("\n[Reloading RAG chain...]")
                try:
                    new_api_key = get_api_key()
                    if new_api_key != last_api_key:
                        print(f"[API key changed: {last_api_key[:15]}... -> {new_api_key[:15]}...]")
                        last_api_key = new_api_key
                    qa_chain = build_rag_chain(temperature=0.1, top_k=5, rebuild_llm=True)
                    print("[Chain reloaded successfully]")
                except Exception as e:
                    print(f"[Failed to reload chain]: {str(e)}")
                continue
            
            print("\n[Processing...]")
            
            # Check if API key changed since last query
            current_api_key = get_api_key()
            if current_api_key != last_api_key:
                print(f"[API key changed - rebuilding chain]")
                qa_chain = build_rag_chain(temperature=0.1, top_k=5, rebuild_llm=True)
                last_api_key = current_api_key
            
            # Query with retry logic
            result = query_rag(qa_chain, test_query, max_retries=3)
            print(format_output(result))
            
        except KeyboardInterrupt:
            print("\n\n[Interrupted by user - Exiting...]")
            break
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "401" in error_msg or "403" in error_msg:
                print(f"[API Error - Your API key may have expired or quota exceeded]")
                print(f"[Please update .env file with a new API key and type 'reload' to continue]")
            else:
                print(f"[Error processing query]: {str(e)[:100]}")
            continue
    
    print("\n" + "=" * 70)
    print("[Thank you for using RAG system]")
    print("=" * 70)
    
except Exception as e:
    error_msg = str(e).lower()
    
    if "api" in error_msg or "key" in error_msg:
        print(f"\n[SETUP ERROR] API Key Issue:")
        print(f"  - Check if .env file has valid GOOGLE_API_KEY")
        print(f"  - Current value: {('GOOGLE_API_KEY' in str(e))}")
    elif "quota" in error_msg:
        print(f"\n[API ERROR] Quota exceeded - API key may be out of quota")
    else:
        print(f"\n[ERROR]: {str(e)}")
    
    import traceback
    if "-v" in sys.argv or "--verbose" in sys.argv:
        print("\n[Full traceback]:")
        traceback.print_exc()
    
    sys.exit(1)
