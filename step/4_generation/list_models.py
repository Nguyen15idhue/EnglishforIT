"""
⚡ SAFEST TEST - List available models (1 read-only call)
This will show which models are actually available to your API key
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ API key not found in .env")
    exit(1)

print("=" * 70)
print("🔍 CHECKING AVAILABLE MODELS")
print("=" * 70)
print(f"\n✓ API Key: {api_key[:40]}...\n")

try:
    # Using official google.genai library (newest)
    import google.genai as genai
    
    print("🔗 Connecting to Gemini API...\n")
    
    client = genai.Client(api_key=api_key)
    
    print("📋 Available models:\n")
    
    # List all models
    models = client.models.list()
    
    count = 0
    for model in models:
        count += 1
        print(f"  ✓ {model.name}")
        if hasattr(model, 'display_name'):
            print(f"    - Display: {model.display_name}")
        print()
    
    print("=" * 70)
    if count == 0:
        print("❌ NO MODELS AVAILABLE")
        print("   This API key may not have access to Gemini models")
        print("\n   Solutions:")
        print("   1. Check Google Cloud Console > APIs & Services")
        print("   2. Enable 'Generative Language API'")
        print("   3. Ensure API key has proper permissions")
    else:
        print(f"✅ FOUND {count} AVAILABLE MODELS")
        print("   You can use any of the models listed above")
    print("=" * 70)
    
except ImportError:
    print("⚠️  google.genai not installed")
    print("   Try: pip install google-genai")
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ ERROR: {error_msg[:300]}\n")
    
    if "401" in error_msg or "permission" in error_msg.lower():
        print("⚠️  API key issue - check permissions")
    elif "403" in error_msg:
        print("⚠️  Access denied - may need to enable API")
    else:
        print("⚠️  Check API key and network connection")
