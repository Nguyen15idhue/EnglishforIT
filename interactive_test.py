"""
Interactive Test Mode - Nhap cau hoi tuy y de test
"""

import sys
import time

# Fix encoding for Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

sys.path.insert(0, 'step/4_generation')

from rag_chain import build_rag_chain, query_rag

print("=" * 80)
print("VIETNAMESE LEGAL ASSISTANT - INTERACTIVE TEST MODE")
print("=" * 80)
print("\nLoading RAG chain (this may take 20-30 seconds on first run)...")
print()

try:
    qa_chain = build_rag_chain(temperature=0.1, top_k=5)
    print("\n[OK] RAG chain loaded successfully!")
    print("=" * 80)
    print()
except Exception as e:
    print(f"\n[ERROR] Error loading RAG chain: {e}")
    sys.exit(1)

print("HOW TO USE:")
print("  * Type your question in Vietnamese")
print("  * Press Enter to submit")
print("  * Type 'exit' or 'quit' to exit")
print("  * Type 'clear' to clear screen")
print()
print("=" * 80)
print()

query_count = 0

while True:
    try:
        # Get user input
        question = input("[QUESTION] Your question: ").strip()
        
        # Check for exit commands
        if question.lower() in ['exit', 'quit', 'q']:
            print("\nGoodbye!")
            break
        
        # Check for clear command
        if question.lower() == 'clear':
            print("\n" * 50)
            continue
        
        # Skip empty input
        if not question:
            print("[WARNING] Please enter a question\n")
            continue
        
        # Process query
        query_count += 1
        print()
        print("[PROCESSING] Processing...")
        
        start_time = time.time()
        result = query_rag(qa_chain, question)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Display answer
        print()
        print("=" * 80)
        print("ANSWER")
        print("=" * 80)
        print()
        print(result.get("result", "No answer generated"))
        print()
        
        # Display metrics
        print("=" * 80)
        print("METRICS")
        print("=" * 80)
        print(f"[TIME] Response time: {response_time:.2f} seconds")
        print(f"[DOCS] Sources retrieved: {len(result.get('source_documents', []))} documents")
        
        # Display sources
        if result.get('source_documents'):
            print()
            print("=" * 80)
            print("SOURCES (Citations)")
            print("=" * 80)
            print()
            
            for i, doc in enumerate(result['source_documents'], 1):
                metadata = doc.metadata
                print(f"{i}. {metadata.get('citation', 'Unknown citation')}")
                print(f"   Article: Dieu {metadata.get('article_no', 'N/A')}")
                print(f"   Law: {metadata.get('doc_name', 'N/A')}")
                print()
        else:
            print()
            print("[WARNING] No sources found - System may have refused to answer")
            print()
        
        print("=" * 80)
        print()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        break
    except Exception as e:
        print(f"\n[ERROR] Error processing query: {e}")
        print("Please try again\n")

# Summary
print()
print("=" * 80)
print(f"[SUMMARY] {query_count} queries processed")
print("=" * 80)
print("=" * 80)
