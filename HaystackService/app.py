from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from haystack import Pipeline, Document
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Haystack Service", version="1.0.0")

# Initialize Document Store
document_store = InMemoryDocumentStore()

# Global storage for documents
documents_db = {}

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class DocumentContext(BaseModel):
    content: str
    document_name: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    source: str
    documents: Optional[List[DocumentContext]] = None

class IndexRequest(BaseModel):
    document_id: int
    filename: str
    content: str

@app.get("/")
def root():
    return {
        "service": "Haystack Document Search & QA",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "documents_count": document_store.count_documents()
    }

@app.post("/api/index")
async def index_document(request: IndexRequest):
    """Index a document into the document store"""
    try:
        # Create Haystack Document
        doc = Document(
            content=request.content,
            meta={
                "document_id": request.document_id,
                "filename": request.filename
            }
        )
        
        # Store in document store
        document_store.write_documents([doc])
        
        # Keep track in our database
        documents_db[request.document_id] = {
            "filename": request.filename,
            "content": request.content
        }
        
        logger.info(f"Indexed document {request.document_id}: {request.filename}")
        
        return {
            "status": "success",
            "document_id": request.document_id,
            "filename": request.filename,
            "total_documents": document_store.count_documents()
        }
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the document store and return relevant answers"""
    try:
        if document_store.count_documents() == 0:
            return QueryResponse(
                answer="Henüz sisteme yüklenmiş doküman bulunmamaktadır.",
                confidence=0.0,
                source="none",
                documents=[]
            )
        
        # Create retriever
        retriever = InMemoryBM25Retriever(document_store=document_store)
        
        # Retrieve relevant documents
        results = retriever.run(query=request.query, top_k=request.top_k)
        
        if not results or "documents" not in results or not results["documents"]:
            return QueryResponse(
                answer="Bu konuda ilgili bir bilgi bulunamadı.",
                confidence=0.0,
                source="none",
                documents=[]
            )
        
        # Get the best matching document
        best_doc = results["documents"][0]
        
        # Build context from retrieved documents
        contexts = []
        for doc in results["documents"]:
            score = doc.score if hasattr(doc, 'score') else 0.5
            contexts.append(DocumentContext(
                content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                document_name=doc.meta.get("filename", "unknown"),
                score=float(score)
            ))
        
        # Simple answer extraction (first relevant chunk)
        answer = best_doc.content
        if len(answer) > 500:
            # Find the most relevant sentence
            sentences = answer.split('.')
            answer = '. '.join(sentences[:3]) + '.'
        
        confidence = best_doc.score if hasattr(best_doc, 'score') else 0.7
        
        return QueryResponse(
            answer=answer,
            confidence=float(confidence),
            source="document",
            documents=contexts
        )
        
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List all indexed documents"""
    return {
        "total": document_store.count_documents(),
        "documents": [
            {
                "document_id": doc_id,
                "filename": info["filename"]
            }
            for doc_id, info in documents_db.items()
        ]
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document from the index"""
    try:
        if document_id in documents_db:
            del documents_db[document_id]
            # Note: InMemoryDocumentStore doesn't have direct delete by meta
            # In production, you'd use a different document store with delete capability
            logger.info(f"Deleted document {document_id}")
            return {"status": "success", "document_id": document_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

