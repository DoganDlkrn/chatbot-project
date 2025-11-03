from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from haystack import Document
from haystack.components.retrievers import InMemoryBM25Retriever
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
        # Query normalization & expansion for short/keyword queries and TR↔EN terms
        def normalize(s: str) -> str:
            return s.strip()

        def expand_query(q: str) -> str:
            base = q.lower().strip()
            # Common ML term expansions (TR <-> EN) and typo fixes
            synonyms = {
                "karışıklık matrisi": "confusion matrix",
                "karisiklik matrisi": "confusion matrix",
                "özgüllük": "specificity true negative rate",
                "ozgulluk": "specificity true negative rate",
                "duyarlılık": "sensitivity true positive rate",
                "duyarlilik": "sensitivity true positive rate",
                "hassasiyet": "sensitivity true positive rate",
                "doğruluk": "accuracy",
                "dogruluk": "accuracy",
            }
            extra = []
            for k, v in synonyms.items():
                if k in base:
                    extra.append(v)
            # If very short (<=2 words) treat as definition question
            words = base.split()
            if len(words) <= 2:
                extra.append("nedir tanımı açıklama definition")
            return (base + " " + " ".join(extra)).strip()

        request.query = normalize(request.query)
        expanded_query = expand_query(request.query)
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
        results = retriever.run(query=expanded_query, top_k=max(5, request.top_k))
        
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
        
        # Query-aware answer extraction
        raw = best_doc.content

        import re
        def clean_reference_text(t: str) -> str:
            # Remove URLs and access notes, collapse spaces
            t = re.sub(r"https?://\S+", "", t)
            t = re.sub(r"\((Erişim|Accessed).*?\)", "", t, flags=re.IGNORECASE)
            t = re.sub(r"\[[0-9]+\]", "", t)
            t = re.sub(r"\s+", " ", t).strip()
            return t

        def clean_line(s: str) -> str:
            return s.strip().lstrip('•-*·–:;').strip()

        # If query asks for a list (nelerdir/which/list), try to extract bullets
        q_lower = request.query.lower()
        explanation_intent = any(k in q_lower for k in [
            "nasıl", "nasil", "ne yapar", "anlat", "nasıldır", "nasildir", "nasıl işler", "özetle", "ozetle"
        ])

        # Region disambiguation (Türkiye vs Dünya)
        region = None
        tr_terms = ["türkiye", "turkiye", "ülkemizde", "yurt içi", "yurt ici"]
        world_terms = ["dünya", "dunyada", "küresel", "kuresel", "global"]
        if any(t in q_lower for t in tr_terms):
            region = "tr"
        elif any(t in q_lower for t in world_terms):
            region = "world"

        def region_bonus(text: str) -> float:
            tl = text.lower()
            if region == "tr" and any(t in tl for t in tr_terms):
                return 0.3
            if region == "world" and any(t in tl for t in world_terms):
                return 0.3
            return 0.0
        if any(k in q_lower for k in ["nelerdir", "hangileri", "list", "çeşitleri", "türleri"]):
            lines = [clean_line(line) for line in raw.split('\n')]
            bullets = [ln for ln in lines if ln.startswith(("-", "•", "·", "*", "–", "▪")) or ln[:2].isdigit()]
            bullets = [clean_line(ln) for ln in bullets if len(clean_line(ln)) > 0]
            if bullets:
                answer = ' ; '.join(bullets[:8])
            else:
                answer = clean_line(raw[:400])
        else:
            # Sentence scoring by keyword overlap, prefer definition-like sentences
            words = set(re.findall(r"\w+", q_lower))
            sentences = re.split(r"(?<=[.!?])\s+|\n+", raw)
            indexed = []
            for idx, s in enumerate(sentences):
                s_clean = clean_line(s)
                if not s_clean:
                    continue
                s_words = set(re.findall(r"\w+", s_clean.lower()))
                overlap = len(words & s_words) / (len(words) + 1e-6)
                # Lightweight boost if looks like a tanım/definition sentence
                is_def = any(k in s_clean.lower() for k in ["nedir", "denir", "tanıml", "kapsar", "amaç", "kullanılır"])
                score = overlap + (0.15 if is_def else 0.0) + region_bonus(s_clean)
                indexed.append((score, idx, s_clean))
            indexed.sort(reverse=True, key=lambda x: x[0])

            # If user yazdığı ifade dokümanda geçiyorsa, oradan itibaren devamını getir
            q_norm = request.query.lower().strip()
            if q_norm and q_norm in raw.lower() and len(q_norm) >= 4:
                # Choose the paragraph containing the query
                lower_raw = raw.lower()
                start = lower_raw.find(q_norm)
                para_start = raw.rfind("\n\n", 0, start)
                para_end = raw.find("\n\n", start)
                if para_start == -1:
                    para_start = 0
                if para_end == -1:
                    para_end = len(raw)
                paragraph = raw[para_start:para_end]
                paragraph = clean_reference_text(paragraph)
                # If paragraph looks like a heading (mostly uppercase or very short or dotted lines), use next paragraph
                def looks_like_heading(p: str) -> bool:
                    p_strip = p.strip()
                    if len(p_strip) < 25:
                        return True
                    upper_ratio = sum(1 for c in p_strip if c.isupper()) / max(1, sum(1 for c in p_strip if c.isalpha()))
                    if upper_ratio > 0.6:
                        return True
                    if '...' in p_strip or p_strip.count('.') > len(p_strip) // 3:
                        return True
                    return False

                if looks_like_heading(paragraph):
                    next_start = para_end + 2
                    next_end = raw.find("\n\n", next_start)
                    if next_end == -1:
                        next_end = len(raw)
                    paragraph = raw[next_start:next_end]
                    paragraph = clean_reference_text(paragraph)
                # Take next 2 sentences after the query phrase inside the paragraph
                # Build from sentence boundary BEFORE the query
                lower_para = paragraph.lower()
                local_pos = lower_para.find(q_norm)
                before = paragraph[:local_pos]
                # find last sentence end
                last_dot = max(before.rfind("."), before.rfind("!"), before.rfind("?"))
                sent_start = last_dot + 1 if last_dot != -1 else 0
                after = paragraph[local_pos + len(q_norm):]
                parts = re.split(r"(?<=[.!?])\s+", after)
                cont = ''.join(parts[:2]).strip()
                answer = (paragraph[sent_start:local_pos] + request.query + ' ' + cont).strip()
                # cleanup dotted lines and stray numbers
                answer = re.sub(r"\.{3,}", " ", answer)
                answer = clean_reference_text(answer)
                if len(answer) < 40 and indexed:
                    # Fallback to window method if too short
                    pass
                else:
                    confidence = best_doc.score if hasattr(best_doc, 'score') else 0.7
                    return QueryResponse(
                        answer=answer,
                        confidence=float(confidence),
                        source="document",
                        documents=contexts
                    )

            # If explanation intent (how/what does it do), return 2-3 sentences from a suitable paragraph
            if explanation_intent:
                paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
                def looks_like_heading(p: str) -> bool:
                    p_strip = p.strip()
                    if len(p_strip) < 25:
                        return True
                    upper_ratio = sum(1 for c in p_strip if c.isupper()) / max(1, sum(1 for c in p_strip if c.isalpha()))
                    return upper_ratio > 0.6
                candidates = [clean_reference_text(p) for p in paragraphs if not looks_like_heading(p)]
                if candidates:
                    # pick paragraph with highest keyword overlap, fallback to first
                    def score_para(p: str) -> float:
                        w = set(re.findall(r"\w+", p.lower()))
                        base = len(words & w) / (len(words) + 1e-6)
                        return base + region_bonus(p)
                    chosen = max(candidates, key=score_para) if words else candidates[0]
                    sent = re.split(r"(?<=[.!?])\s+", chosen)
                    answer = ' '.join([clean_line(s) for s in sent[:3] if clean_line(s)])
                    confidence = best_doc.score if hasattr(best_doc, 'score') else 0.7
                    return QueryResponse(
                        answer=answer,
                        confidence=float(confidence),
                        source="document",
                        documents=contexts
                    )

            if indexed:
                # Prefer exact-term window if present
                term = next(iter(words)) if words else ""
                exact_idx = None
                if term:
                    for i, s in enumerate(sentences):
                        if term and term in s.lower():
                            exact_idx = i
                            break
                use_i = exact_idx if exact_idx is not None else indexed[0][1]
                # Take a window: best sentence + next 1-2 sentences to avoid cutting mid-thought
                window = sentences[use_i: use_i + 3]
                window = [clean_line(s) for s in window if clean_line(s)]
                answer = clean_reference_text(' '.join(window))
            else:
                answer = clean_reference_text(clean_line(raw[:300]))

            # Cleanup duplicates and spacing, ensure sentence end
            answer = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", answer, flags=re.IGNORECASE)
            answer = re.sub(r"\s+", " ", answer).strip()
            if answer and answer[-1] not in ".!?":
                answer += "."

        confidence = best_doc.score if hasattr(best_doc, 'score') else 0.7

        return QueryResponse(
            answer=answer.strip(),
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

