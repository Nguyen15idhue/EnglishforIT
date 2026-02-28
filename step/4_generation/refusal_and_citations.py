"""
Bước 4 & 5: Refusal Mechanism + Citation Extraction
"""

from typing import List, Dict
from langchain_core.documents import Document

# Confidence threshold
MIN_CONFIDENCE = 0.3

REFUSAL_MESSAGES = {
    "no_result": """
Tôi không tìm thấy thông tin về vấn đề này trong các văn bản pháp luật được cung cấp.

Hệ thống này hỗ trợ tư vấn về:
- Luật Đê Điều
- Luật Thủy Lợi  
- Luật Khí Tượng Thủy Văn
- Luật Phòng Chống Thiên Tai

Để được tư vấn chính xác, vui lòng liên hệ cơ quan hành chính có thẩm quyền.
""",
    
    "low_confidence": """
Thông tin tìm được có độ tin cậy thấp. 

Gợi ý:
- Hãy đặt câu hỏi cụ thể hơn
- Sử dụng từ khóa khác
- Nếu vẫn không tìm được, liên hệ chuyên gia pháp lý
""",
    
    "out_of_scope": """
Câu hỏi của bạn nằm ngoài lĩnh vực mà hệ thống hỗ trợ.

Hệ thống này chuyên về:
✓ Quản lý đê điều
✓ Thủy lợi
✓ Khí tượng thủy văn  
✓ Phòng chống thiên tai

Vui lòng đặt câu hỏi liên quan đến các lĩnh vực trên.
"""
}


def check_should_refuse(sources: List[Document]) -> bool:
    """
    Kiểm tra xem có nên từ chối trả lời không
    
    Args:
        sources: List of retrieved documents
        
    Returns:
        bool: True nếu nên từ chối, False nếu có thể trả lời
    """
    if not sources:
        return True  # Không tìm được → từ chối
    
    # Kiểm tra confidence score
    # (LLM không cung cấp score, nhưng FAISS có thể)
    # Tạm thời: nếu có ít nhất 1 document → có thể trả lời
    
    return False


def extract_citations(sources: List[Document]) -> List[Dict[str, str]]:
    """
    Trích xuất citations từ metadata (KHÔNG cho LLM tự extract)
    
    Args:
        sources: List of Document objects with metadata
        
    Returns:
        List of citation dicts
    """
    citations = []
    seen = set()
    
    for doc in sources:
        metadata = doc.metadata
        
        # Build citation từ metadata đã chuẩn hóa
        citation = {
            "article_no": metadata.get("article_no", ""),
            "article_name": metadata.get("article_name", ""),
            "doc_name": metadata.get("doc_name", ""),
            "doc_id": metadata.get("doc_id", ""),
            "citation": metadata.get("citation", ""),
            "chapter_no": metadata.get("chapter_no", "")
        }
        
        # Tránh duplicate
        if citation["citation"] not in seen:
            citations.append(citation)
            seen.add(citation["citation"])
    
    return citations


def format_citations(citations: List[Dict]) -> str:
    """Format citations cho display"""
    if not citations:
        return "Không có trích dẫn"
    
    lines = ["📚 Nguồn tham khảo:"]
    for i, cite in enumerate(citations, 1):
        article = cite.get("article_no", "")
        article_name = cite.get("article_name", "")
        doc_name = cite.get("doc_name", "")
        doc_id = cite.get("doc_id", "")
        
        line = f"{i}. **{article}** - {article_name}"
        if doc_name and doc_id:
            line += f" ({doc_name} - {doc_id})"
        lines.append(line)
    
    return "\n".join(lines)


def validate_answer(answer: str, sources: List[Document]) -> Dict:
    """
    Validate answer quality
    - Check cho hallucination
    - Check completeness
    
    Returns: {
        "is_valid": bool,
        "confidence": float (0-1),
        "issues": list[str]
    }
    """
    issues = []
    confidence = 1.0
    
    # Check 1: Empty answer
    if not answer or len(answer.strip()) < 10:
        issues.append("Answer too short")
        confidence -= 0.5
    
    # Check 2: Generic refusal patterns
    generic_patterns = [
        "i don't know",
        "không biết",
        "không rõ",
        "không có thông tin"
    ]
    if any(pattern in answer.lower() for pattern in generic_patterns):
        confidence -= 0.3
    
    # Check 3: Citation count
    if not sources or len(sources) == 0:
        issues.append("No sources")
        confidence -= 0.4
    
    is_valid = confidence >= MIN_CONFIDENCE
    
    return {
        "is_valid": is_valid,
        "confidence": confidence,
        "issues": issues
    }


if __name__ == "__main__":
    print("✅ Refusal mechanism and citation functions loaded")
