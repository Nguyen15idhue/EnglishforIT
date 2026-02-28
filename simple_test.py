"""
Simple Test - No Input Required
Just run and it will test a question
"""

import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

sys.path.insert(0, 'step/4_generation')

from rag_chain import build_rag_chain, query_rag

print("=" * 80)
print("SIMPLE TEST - HARDCODED QUESTION")
print("=" * 80)
print()

# Load chain
print("Loading RAG chain...")
try:
    qa_chain = build_rag_chain(temperature=0.1, top_k=5)
    print("[OK] RAG chain loaded!\n")
except Exception as e:
    print(f"[ERROR] Failed to load: {e}")
    sys.exit(1)

# Test question
test_question = "Quy định về bảo vệ đê điều là gì?"
print(f"Testing question: {test_question}")
print()

# Query
print("Processing...")
start = time.time()
result = query_rag(qa_chain, test_question)
elapsed = time.time() - start

# Show answer
print()
print("=" * 80)
print("ANSWER:")
print("=" * 80)
answer = result.get("answer", "")
if answer:
    print(answer)
    
# Show sources
if result.get("source_citations"):
    print()
    print("=" * 80)
    print("SOURCES:")
    print("=" * 80)
    for i, citation in enumerate(result["source_citations"], 1):
        print(f"{i}. {citation}")
else:
    print("[NO ANSWER]")

# Show metrics
print()
print("=" * 80)
print("METRICS:")
print("=" * 80)
print(f"Response time: {elapsed:.2f} seconds")
print(f"Documents retrieved: {len(result.get('source_documents', []))}")

# Show sources
if result.get('source_documents'):
    print()
    print("=" * 80)
    print("SOURCES:")
    print("=" * 80)
    for i, doc in enumerate(result['source_documents'], 1):
        meta = doc.metadata
        print(f"{i}. {meta.get('citation', 'Unknown')}")
