# backend/app/services/query_service.py
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from backend.app.core.config import settings
from backend.app.services.vector_store_manager import VectorStoreManager

async def handle_query(query: str):
    """Handle user queries against the vector store"""
    vector_store_manager = VectorStoreManager()
    vector_store = vector_store_manager.get_active_store()
    
    if not vector_store or vector_store.index.ntotal == 0:
        raise ValueError("No documents available for querying")
    
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="Llama3-8b-8192"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the questions based on the provided context only."),
        ("user", "<context>\n{context}\n<context>\nQuestion: {input}")
    ])
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    try:
        result = retrieval_chain.invoke({'input': query})
        return format_response(result)
    except Exception as e:
        raise ValueError(f"Query processing failed: {str(e)}")

def format_response(result: dict) -> dict:
    """Format the response for the API"""
    return {
        "response": result.get("answer", "No relevant information found"),
        "sources": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result.get("context", [])
        ]
    }