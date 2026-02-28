"""
Simple Test - Call API chỉ 1 lần duy nhất để xác nhận hoạt động
KHÔNG CHẠY LIÊN TỤC - chỉ chạy KHI CHẮC CHẮN quota còn
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(override=True)

def test_once():
    """Test API 1 lần duy nhất"""
    print("=" * 60)
    print("⚠️  TEST API - CHỈ CHẠY 1 LẦN!")
    print("=" * 60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ API key không tìm thấy trong .env")
        return False
    
    try:
        print(f"\n🔑 API key: {api_key[:20]}...")
        print("📡 Đang kết nối...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        print("✅ Model loaded")
        print("📝 Sending test query...")
        
        # 1 query duy nhất
        response = llm.invoke("Xin chào")
        
        print("✅ API hoạt động!")
        print(f"\n🤖 Response: {response.content[:100]}...")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print(f"❌ Quota hết: {error_msg[:100]}...")
            print("⏳ Chờ quota reset (hôm nay tối hoặc ngày mai)")
        elif "404" in error_msg or "NOT_FOUND" in error_msg:
            print(f"❌ Model không tìm thấy: {error_msg[:100]}...")
            print("💡 Thử model khác: gemini-1.5-pro, gemini-2.0-flash")
        else:
            print(f"❌ Lỗi: {error_msg[:150]}...")
        
        return False


if __name__ == "__main__":
    success = test_once()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API OK - Có thể chạy RAG chain")
    else:
        print("❌ API không OK - Chờ quota reset hoặc fix issue")
    print("=" * 60)
