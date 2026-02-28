"""Test kết nối Gemini API"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key từ .env
load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ API key không tìm thấy. Kiểm tra file .env")
    exit(1)

print("📡 Đang kết nối tới Gemini API...")

try:
    # Test kết nối
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.1
    )
    
    # Gửi test query
    response = llm.invoke("Bạn là ai?")
    
    print("✅ Kết nối thành công!")
    print(f"\n🤖 Phản hồi từ Gemini:\n{response.content}")
    
except Exception as e:
    print(f"❌ Lỗi: {str(e)}")
    print("\nKiểm tra lại:")
    print("1. API key có đúng không?")
    print("2. Internet connection ổn không?")
    print("3. Quota API còn không?")
