"""
Bước 3: RAG Chain - Tích hợp LLM + Retriever + Prompts
"""

import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from system_prompt import SYSTEM_PROMPT, PROMPT_TEMPLATE, REFUSAL_RESPONSE
from refusal_and_citations import REFUSAL_MESSAGES

# Load API key
load_dotenv(override=True)

# Confidence threshold for relevance
RELEVANCE_THRESHOLD = 0.5  # Similarity score must be > 0.5 to answer


def get_api_key():
    """Get API key from environment, reload from .env if needed"""
    # Reload .env to pick up any changes
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key.startswith("GOOGLE_API_KEY="):
        raise ValueError("API key not found or invalid in .env file")
    return api_key


def load_faiss_vectorstore():
    """Load FAISS index từ giai đoạn 2"""
    print("📦 Loading FAISS index...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    vectorstore = FAISS.load_local(
        "step/2_ingestion/output/law_documents_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    print(f"✅ Loaded {vectorstore.index.ntotal} vectors")
    return vectorstore


def build_rag_chain(temperature=0.1, top_k=5, rebuild_llm=False):
    """Build RAG chain: Retriever + LLM + Prompt
    
    Args:
        temperature: LLM temperature (0.0-1.0), lower = more factual
        top_k: Number of documents to retrieve in search_kwargs
        rebuild_llm: Force rebuild LLM with fresh API key
    """
    print("🔧 Building RAG chain...")
    
    # 1. Load vectorstore
    vectorstore = load_faiss_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    
    # 2. Init LLM with fresh API key
    api_key = get_api_key()
    print(f"[Using API Key: {api_key[:15]}...]")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=temperature,  # Configurable: Low = more factual
        top_p=0.95,
        top_k=40,
        request_timeout=60  # 60 second timeout
    )
    
    # 3. Build chain (RetrievalQA manages its own prompt)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",  # Stuff all docs into context
        verbose=False
    )
    
    print("✅ RAG chain built successfully")
    return qa_chain


def query_rag(qa_chain, question: str, max_retries=3) -> dict:
    """
    Query RAG chain with CONFIDENCE CHECKING to prevent hallucination
    
    Args:
        qa_chain: RAG chain instance (must have retriever accessible)
        question: User question
        max_retries: Max retry attempts if API fails
    
    Returns:
        dict: {
            "answer": str,
            "sources": list[Document],
            "source_citations": list[str],
            "refused": bool
        }
    
    Raises:
        Exception: If all retries fail
    """
    
    # STEP 0: Pre-check for obviously out-of-domain questions
    question_lower = question.lower()
    
    # Keywords that indicate question is definitely NOT about laws
    out_of_domain_keywords = [
        "who are you", "ai la ai", "ban la ai", "maye la ai", "mai la ai", 
        "ban ten la gi", "ban la gì", "ai la ban", "tim ban",
        "what is your name", "who built you", "tu tien huy",
        "reckon", "recipe", "nau an", "nan", "anh la ai", "chi la ai",
        "me la ai", "cha la ai", "con la gì",  
        "love", "dating", "em la ai", "yeu", "hen ho",
        "joke", "tro chuyen", "tao la ai", "co la ai",
        "xau", "xin", "van phong", "cong ty", "di lam"
    ]
    
    # Check if question contains any out-of-domain keywords
    if any(keyword in question_lower for keyword in out_of_domain_keywords):
        return {
            "answer": REFUSAL_MESSAGES["out_of_scope"],
            "sources": [],
            "source_citations": [],
            "refused": True
        }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # STEP 1: Check relevance BEFORE calling LLM
            # Get the vectorstore from the chain's retriever
            retriever = qa_chain.retriever
            vectorstore = retriever.vectorstore
            
            # Retrieve with similarity scores
            docs = vectorstore.similarity_search(question, k=5)
            
            if not docs:
                # No documents found at all
                return {
                    "answer": REFUSAL_MESSAGES["no_result"],
                    "sources": [],
                    "source_citations": [],
                    "refused": True
                }
            
            # For FAISS, check if top document is sufficiently long (meaningful)
            top_doc = docs[0]
            doc_length = len(top_doc.page_content) if top_doc else 0
            
            # If top result is extremely short (< 30 chars), likely not relevant
            if doc_length < 30:
                return {
                    "answer": REFUSAL_MESSAGES["low_confidence"],
                    "sources": [],
                    "source_citations": [],
                    "refused": True
                }
            
            # STEP 2: Proceed with RAG chain only if all checks pass
            result = qa_chain({"query": question})
            
            # STEP 3: Post-check - if answer seems like hallucination, refuse
            # Check if LLM generated an answer using its own knowledge
            answer = result.get("result", "")
            
            # Indicators of hallucination (LLM answering from its own knowledge):
            hallucination_indicators = [
                "i am a", "i'm a", "tôi là một", "tôi là một mô hình",
                "có thể giúp", "xin chào", "hello", "nice to meet",
                "trained by", "built by", "developed by"
            ]
            
            if any(indicator in answer.lower() for indicator in hallucination_indicators):
                # LLM is hallucinating - refuse
                return {
                    "answer": REFUSAL_MESSAGES["no_result"],
                    "sources": [],
                    "source_citations": [],
                    "refused": True
                }
            
            # Extract citations from source documents
            citations = []
            for doc in result.get("source_documents", []):
                citation = doc.metadata.get("citation", "")
                if citation and citation not in citations:
                    citations.append(citation)
            
            return {
                "answer": result["result"],
                "sources": result.get("source_documents", []),
                "source_citations": citations,
                "refused": False
            }
            
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            
            # Check if it's an API key/quota error
            is_quota_error = any(keyword in error_msg for keyword in [
                "quota", "429", "403", "unauthorized", "invalid", "authentication"
            ])
            is_timeout_error = any(keyword in error_msg for keyword in [
                "timeout", "deadline", "exceeded", "connection"
            ])
            
            if attempt < max_retries - 1:
                if is_quota_error:
                    print(f"[Attempt {attempt + 1}/{max_retries}] API Key/Quota issue detected")
                    print(f"[Waiting 5 seconds before retry...]")
                    time.sleep(5)
                elif is_timeout_error:
                    wait_time = 2 ** attempt
                    print(f"[Attempt {attempt + 1}/{max_retries}] Timeout error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    wait_time = 2 ** attempt
                    print(f"[Attempt {attempt + 1}/{max_retries}] Error: {str(e)[:60]}...")
                    time.sleep(wait_time)
            else:
                print(f"[Failed after {max_retries} attempts]")
                break
    
    # If we get here, all retries failed
    raise Exception(f"[Query failed after {max_retries} attempts]: {str(last_error)}")


def format_output(result: dict) -> str:
    """Format output cho display"""
    output = []
    output.append("=" * 60)
    
    # Check if answer was refused
    if result.get("refused"):
        output.append("[HE THONG TU CHOI TRA LOI]\n")
        output.append(result["answer"])
    else:
        output.append("TRICH DAN PHAP LUAT\n")
        output.append(result["answer"])
        
        if result.get("source_citations"):
            output.append("\nNguon tham khao:")
            for i, citation in enumerate(result["source_citations"], 1):
                output.append(f"{i}. {citation}")
    
    output.append("=" * 60)
    return "\n".join(output)


if __name__ == "__main__":
    print("🚀 Testing RAG chain...\n")
    
    try:
        # Build chain
        qa_chain = build_rag_chain()
        
        # Test query
        test_query = "Quy định về bảo vệ đê điều như thế nào?"
        print(f"❓ Query: {test_query}\n")
        
        result = query_rag(qa_chain, test_query)
        output = format_output(result)
        print(output)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
