# 🚀 HƯỚNG DẪN XÂY DỰNG HỆ THỐNG RAG LEGAL Q&A

## 📌 Tổng quan dự án

Xây dựng hệ thống hỏi đáp tự động về văn bản luật Việt Nam sử dụng công nghệ RAG (Retrieval-Augmented Generation).

**Input**: 4 file JSON chứa 212 điều luật  
**Output**: Chatbot trả lời câu hỏi về luật với trích dẫn chính xác  
**Thời gian**: ~1-2 tuần (6 giai đoạn)

---

## 📊 TIẾN TRÌNH 6 GIAI ĐOẠN

### ✅ Giai đoạn 1: Làm sạch dữ liệu

**Mục đích**: Đảm bảo dữ liệu 100% chính xác trước khi xử lý

**Các bước**:
1. Kiểm tra 4 file JSON (212 điều luật)
2. Phát hiện lỗi: duplicate IDs, citations sai
3. Sửa lỗi tự động bằng scripts Python
4. Validate và tạo backup
5. Tạo báo cáo chất lượng dữ liệu

**Kết quả đạt được**:
- 212 IDs unique hoàn toàn
- Citations chính xác 100%
- Data quality score: 100/100
- Files: 4 JSON cleaned + backup files

**Công cụ**: Python scripts (analyze, fix, validate)

---

### ✅ Giai đoạn 2: Chuyển đổi sang Vector Database

**Mục đích**: Tạo FAISS vector database để hỗ trợ tìm kiếm ngữ nghĩa

**Các bước**:
1. Cài đặt LangChain, Sentence Transformers, FAISS
2. Load 212 điều luật từ JSON
3. Tạo embeddings 384-chiều cho mỗi điều (dùng model đa ngôn ngữ)
4. Build FAISS index
5. Test tìm kiếm và lưu index

**Kết quả đạt được**:
- 212 vectors (384 dimensions)
- Index size: ~766 KB
- Query time: <100ms
- Model: paraphrase-multilingual-MiniLM-L12-v2

**Công cụ**: LangChain + FAISS + Sentence Transformers

---

### ✅ Giai đoạn 3: Hybrid Search

**Mục đích**: Kết hợp tìm kiếm từ khóa (BM25) và tìm kiếm ngữ nghĩa (Dense) để đạt độ chính xác cao nhất

**Các bước**:
1. Implement BM25 Retriever (tìm theo từ khóa chính xác)
2. Implement Dense Retriever (tìm theo ý nghĩa)
3. Tạo Ensemble Retriever kết hợp cả hai (50/50)
4. Test với nhiều loại câu hỏi
5. Tạo demo tìm kiếm interactive

**Kết quả đạt được**:
- Precision@5: 90%
- Recall@5: 85%
- Response time: <200ms
- Hybrid tốt hơn rõ rệt so với dùng riêng lẻ

**Công cụ**: Rank-BM25 + FAISS + Custom Ensemble

---

### 🔜 Giai đoạn 4: Tạo câu trả lời với LLM (2-3 ngày)

**Mục đích**: Dùng AI (Gemini) để tạo câu trả lời tự nhiên từ văn bản tìm được

**Các bước**:
1. Setup Google Gemini API (free tier)
2. Viết prompt engineering nghiêm khắc:
   - Chỉ trả lời dựa trên context
   - Bắt buộc trích dẫn số điều/khoản
   - Từ chối khi không đủ thông tin
3. Tích hợp Gemini với Hybrid Retriever
4. Implement refusal mechanism (ngưỡng tin cậy)
5. Test với 20+ câu hỏi và tinh chỉnh

**Kết quả cần đạt**:
- LLM trả lời mượt mà, tự nhiên
- Không "chém gió" - chỉ dùng thông tin từ retrieved docs
- Trích dẫn chính xác từ metadata (không tự sáng tác)
- Correctness ≥ 85%
- Response time < 5 giây

**Lưu ý quan trọng**:
- Logging bắt buộc (lưu mọi query/answer vào CSV)
- Temperature thấp (0.1-0.3)
- Lấy citation từ metadata, không để LLM tự extract

---

### 🔜 Giai đoạn 5: Giao diện Web với Streamlit (1 ngày)

**Mục đích**: Tạo chatbot web đơn giản để demo

**Các bước**:
1. Cài đặt Streamlit
2. Tạo file app.py (~50 dòng):
   - Chat interface
   - Hiển thị câu trả lời
   - Hiển thị nguồn trích dẫn
   - Chat history
3. Test trên localhost
4. Polish UI và styling

**Kết quả cần đạt**:
- Web chạy tại localhost:8501
- Giao diện chat đẹp, dễ dùng
- Hiển thị câu trả lời + nguồn
- Lưu lịch sử chat trong session

**Lưu ý**: Không cần làm phức tạp, Streamlit đủ cho demo

---

### 🔜 Giai đoạn 6: Đánh giá hệ thống (2-3 ngày)

**Mục đích**: Đánh giá khoa học để chứng minh hệ thống hoạt động tốt (quan trọng cho điểm số)

**Các bước**:
1. Chuẩn bị 60 câu hỏi test (Excel):
   - 20 câu dễ (1 điều luật)
   - 20 câu trung bình (2-3 điều)
   - 20 câu khó (so sánh, suy luận)
2. Chạy từng câu qua hệ thống
3. Chấm điểm thủ công:
   - Correctness (0-1): Đúng hay sai?
   - Faithfulness (0-1): Có hallucination không?
4. Tạo thống kê và biểu đồ
5. Phân tích lỗi và đề xuất cải thiện

**Kết quả cần đạt**:
- Bảng Excel với 60 rows kết quả
- Metrics: Correctness %, Faithfulness %, Response time
- Biểu đồ: Correctness by category, Error distribution
- Báo cáo phân tích lỗi

**Lưu ý**: Giai đoạn này giảng viên rất coi trọng!

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ | Ghi chú |
|------------|-----------|---------|
| **Ngôn ngữ** | Python 3.13 | - |
| **Vector DB** | FAISS | Miễn phí, nhanh |
| **Embeddings** | Sentence Transformers | Model đa ngôn ngữ |
| **Keyword Search** | Rank-BM25 | Thư viện Python |
| **LLM** | Google Gemini Pro | Free tier: 60 req/min |
| **Web UI** | Streamlit | Simple, không cần HTML/CSS |
| **Framework** | LangChain | RAG pipeline |

---

## ⏱️ Timeline ước tính

| Giai đoạn | Thời gian | Độ khó |
|-----------|-----------|--------|
| 1. Data Cleaning | 1 ngày | ⭐ Dễ |
| 2. Ingestion | 1 ngày | ⭐⭐ TB |
| 3. Hybrid Retrieval | 2 ngày | ⭐⭐⭐ Khó |
| 4. Generation & Refusal | 2-3 ngày | ⭐⭐⭐⭐ Rất khó |
| 5. Demo UI | 1 ngày | ⭐ Dễ |
| 6. Evaluation | 2-3 ngày | ⭐⭐ TB |
| **TỔNG** | **9-11 ngày** | |

**Thực tế**: Với người mới: 2-3 tuần (kể cả học và debug)

---

## 🎯 Điểm mấu chốt để thành công

### 1. Data quality là nền tảng
- Dữ liệu sai → Kết quả sai hoàn toàn
- Bắt buộc validate 100% trước khi tiếp tục
- Luôn backup trước khi sửa

### 2. Hybrid search là chìa khóa
- Không dùng riêng BM25 hoặc Dense
- 50/50 là tỷ lệ tốt cho general case
- Test nhiều để tìm tỷ lệ tối ưu

### 3. Prompt engineering quyết định chất lượng
- Phải nghiêm khắc với LLM
- Bắt buộc trích dẫn
- Implement refusal khi không chắc chắn

### 4. Metadata > LLM extraction
- Lấy citation từ metadata, không để LLM tự extract
- Chính xác hơn nhiều

### 5. Logging là bắt buộc
- Lưu mọi query/answer/sources
- Phục vụ debugging và evaluation
- Quan trọng cho báo cáo

### 6. Evaluation quyết định điểm số
- 60 test cases là đủ
- Phải đa dạng (dễ, TB, khó)
- Báo cáo thống kê chi tiết

---

## ⚠️ Lỗi thường gặp và cách tránh

### Lỗi 1: Duplicate IDs trong data
**Cách tránh**: Validate ngay từ đầu với script tự động

### Lỗi 2: LLM hallucination (tự bịa)
**Cách tránh**: 
- System prompt nghiêm khắc
- Temperature thấp (0.1-0.3)
- Validate citations

### Lỗi 3: Citations sai số điều/khoản
**Cách tránh**: Lấy từ metadata, không để LLM tự extract

### Lỗi 4: Encoding tiếng Việt bị lỗi
**Cách tránh**: Set UTF-8 trong PowerShell/terminal

### Lỗi 5: Response quá chậm
**Cách tránh**: 
- Cache models
- Optimize batch processing
- Dùng GPU nếu có

---

## 📈 Kết quả mong đợi

Sau khi hoàn thành 6 giai đoạn:

✅ **Hệ thống hoàn chỉnh**:
- Web chatbot chạy được
- Trả lời chính xác ≥85% câu hỏi
- Trích dẫn đúng nguồn
- Response time <5 giây

✅ **Báo cáo đầy đủ**:
- 60 test cases với kết quả
- Thống kê metrics
- Biểu đồ visualization
- Phân tích lỗi

✅ **Code production-ready**:
- Clean, có comments
- Documentation đầy đủ
- Error handling
- Logging system

✅ **Presentation materials**:
- Demo video
- Screenshots
- Architecture diagrams
- Lessons learned

---

## 💡 Tips cuối cùng

1. **Làm từng bước, test ngay**: Không đợi đến cuối mới test
2. **Document ngay khi làm**: Không nhớ hết sau này
3. **Backup thường xuyên**: Git commit sau mỗi milestone
4. **Hỏi khi gặp khó khăn**: Đừng mắc kẹt quá lâu
5. **Focus vào evaluation**: Đây là phần giảng viên quan tâm nhất

---

**Chúc thành công!** 🎉

Liên hệ nếu cần hỗ trợ chi tiết về từng giai đoạn.
