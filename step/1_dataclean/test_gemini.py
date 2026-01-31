import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load API Key từ file .env
load_dotenv()

# 2. Khởi tạo model Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 3. Thử hỏi một câu
try:
    response = llm.invoke("Chào bạn, bạn có thể giúp tôi hiểu về luật pháp Việt Nam không?")
    print("--- Kết nối thành công! ---")
    print("Gemini trả lời:", response.content)
except Exception as e:
    print("--- Lỗi kết nối! ---")
    print(e)