import os
from langchain_google_genai import ChatGoogleGenerativeAI

print("="*60)
print("🧪 GEMINI API - SINGLE CALL TEST")
print("="*60)

# Kiểm tra API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("❌ GOOGLE_API_KEY chưa được set")

print(f"✓ API key loaded: {api_key[:15]}...")

print("\n🔗 Initializing model...")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-pro",
    temperature=0.3
)
print("✓ Model initialized")

print("\n📤 Sending test request...")
response = llm.invoke(
    "Chào bạn, hãy trả lời ngắn gọn: API có hoạt động không?"
)

print("\n✅ Response:")
print(response.content)
