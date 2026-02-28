"""
Bước 6: Testing và Validation - Test 5 câu hỏi đa dạng
"""

from rag_chain import build_rag_chain, query_rag, format_output
from refusal_and_citations import (
    check_should_refuse, 
    extract_citations, 
    format_citations, 
    validate_answer
)
import time

TEST_QUERIES = [
    {
        "query": "Quy định về bảo vệ đê điều như thế nào?",
        "category": "operational",
        "expected_law": "Luật Đê Điều"
    },
    {
        "query": "Trách nhiệm của UBND tỉnh trong quản lý đê điều?",
        "category": "responsibility",
        "expected_law": "Luật Đê Điều"
    },
    {
        "query": "Nội dung chính của Luật Thủy Lợi?",
        "category": "overview",
        "expected_law": "Luật Thủy Lợi"
    },
    {
        "query": "Xử phạt vi phạm Luật PCTT bị bao nhiêu?",
        "category": "penalty",
        "expected_law": "Luật PCTT"
    },
    {
        "query": "Luật giao thông có quy định gì về xe máy?",
        "category": "out_of_scope",
        "expect_refusal": True
    }
]


def run_tests():
    """Run test suite"""
    print("🧪 TESTING RAG CHAIN\n")
    print("=" * 70)
    
    try:
        # Build chain once
        print("⏳ Building RAG chain...")
        qa_chain = build_rag_chain(temperature=0.1, top_k=5)
        print("✅ Chain ready\n")
        
        results = []
        
        for i, test in enumerate(TEST_QUERIES, 1):
            print(f"\n{'='*70}")
            print(f"Test #{i}: {test['category'].upper()}")
            print(f"{'='*70}")
            
            query = test["query"]
            print(f"❓ Query: {query}\n")
            
            # Time the query
            start = time.time()
            result = query_rag(qa_chain, query)
            elapsed = time.time() - start
            
            # Extract info
            answer = result["answer"]
            sources = result["sources"]
            citations = extract_citations(sources)
            
            # Validate
            validation = validate_answer(answer, sources)
            
            # Print results
            print(f"📝 Answer:\n{answer[:300]}...\n")
            
            if citations:
                print(format_citations(citations))
            
            print(f"\n⏱️  Response time: {elapsed:.2f}s")
            print(f"📊 Confidence: {validation['confidence']:.1%}")
            print(f"✓ Valid: {validation['is_valid']}")
            
            if validation['issues']:
                print(f"⚠️  Issues: {', '.join(validation['issues'])}")
            
            # Store result
            results.append({
                "test_no": i,
                "category": test["category"],
                "query": query,
                "valid": validation["is_valid"],
                "confidence": validation["confidence"],
                "time": elapsed,
                "source_count": len(sources)
            })
        
        # Summary
        print(f"\n\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"{'='*70}")
        
        valid_count = sum(1 for r in results if r["valid"])
        avg_time = sum(r["time"] for r in results) / len(results)
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        
        print(f"✅ Valid answers: {valid_count}/{len(results)}")
        print(f"⏱️  Avg response time: {avg_time:.2f}s")
        print(f"📊 Avg confidence: {avg_confidence:.1%}")
        print(f"📚 Total sources: {sum(r['source_count'] for r in results)}")
        
        print("\nDetailed results:")
        print(f"{'No':<3} {'Category':<15} {'Valid':<7} {'Confidence':<12} {'Time':<7}")
        print("-" * 50)
        for r in results:
            print(f"{r['test_no']:<3} {r['category']:<15} {str(r['valid']):<7} {r['confidence']:<12.1%} {r['time']:<7.2f}s")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = run_tests()
    if results:
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Tests failed!")
