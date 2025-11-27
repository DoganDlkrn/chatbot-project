from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from haystack import Document
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
try:
    from haystack.document_stores import FAISSDocumentStore  # optional
except Exception:
    FAISSDocumentStore = None  # type: ignore
from typing import Tuple
import math
import numpy as np
from sqlalchemy import create_engine, text as sql_text
import requests

# Setup logging early (before we instantiate clients so logger exists)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM & Embedding Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY") or "ollama"
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or "http://localhost:11434/v1"
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:1b")

# Embeddings (default to Ollama nomic-embed-text unless overridden)
EMBED_API_KEY = os.getenv("EMBED_API_KEY") or "ollama"
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL") or "http://localhost:11434/v1"
EMBED_MODEL = os.getenv("LLM_EMBEDDINGS_MODEL") or os.getenv("EMBED_MODEL") or "nomic-embed-text"

# FAISS persistence paths
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/data/vector/faiss.index")
FAISS_CONFIG_PATH = os.getenv("FAISS_CONFIG_PATH", "/data/vector/faiss_config.json")
FAISS_DOC_PATH = os.getenv("FAISS_DOC_PATH", "/data/vector/faiss_store.db")

def call_chat_completion(messages: List[dict], temperature: float = 0.3, max_tokens: int = 400) -> Optional[str]:
    if not LLM_API_KEY or not LLM_BASE_URL:
        return None
    url = LLM_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices")
        if not choices:
            return None
        return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.warning(f"Chat completion call failed: {e}")
        return None

def get_embedding(text: str) -> Optional[List[float]]:
    if not EMBED_API_KEY or not EMBED_BASE_URL:
        return None
    try:
        url = EMBED_BASE_URL.rstrip("/") + "/embeddings"
        headers = {
            "Authorization": f"Bearer {EMBED_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"model": EMBED_MODEL, "input": text}
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        emb = data.get("data", [{}])[0].get("embedding")
        return emb
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return None

def cosine(a: List[float], b: List[float]) -> float:
    try:
        va = np.array(a, dtype=np.float32)
        vb = np.array(b, dtype=np.float32)
        denom = (np.linalg.norm(va) * np.linalg.norm(vb))
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)
    except Exception:
        return 0.0

app = FastAPI(title="Haystack Service", version="1.0.0")

# Initialize Document Store (optional FAISS for persistence)
USE_FAISS = (os.getenv("USE_FAISS", "false").lower() in ["1", "true", "yes"]) and (FAISSDocumentStore is not None)

def ensure_faiss_dirs():
    try:
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    except Exception:
        pass

def init_faiss_store():
    ensure_faiss_dirs()
    has_index = os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_CONFIG_PATH)
    if has_index:
        logger.info("Loading existing FAISS index from disk")
        return FAISSDocumentStore(
            faiss_index_path=FAISS_INDEX_PATH,
            faiss_config_path=FAISS_CONFIG_PATH,
            sql_url=f"sqlite:///{FAISS_DOC_PATH}",
            faiss_index_factory_str="Flat"
        )
    logger.info("Creating new FAISS index")
    return FAISSDocumentStore(
        sql_url=f"sqlite:///{FAISS_DOC_PATH}",
        faiss_index_factory_str="Flat"
    )

if USE_FAISS:
    try:
        document_store = init_faiss_store()
        logger.info("Using FAISSDocumentStore (Flat)")
    except Exception as e:
        logger.warning(f"FAISS init failed, falling back to InMemoryDocumentStore: {e}")
        document_store = InMemoryDocumentStore()
else:
    document_store = InMemoryDocumentStore()

def persist_document_store():
    if not USE_FAISS:
        return
    try:
        ensure_faiss_dirs()
        document_store.save(index_path=FAISS_INDEX_PATH, config_path=FAISS_CONFIG_PATH)
        logger.info("FAISS index persisted to disk")
    except Exception as e:
        logger.warning(f"Failed to persist FAISS index: {e}")

# Global storage for documents (for listing)
documents_db = {}

def hydrate_documents_from_store():
    """Populate documents_db from persistent store on startup."""
    try:
        existing_docs = document_store.filter_documents()
        for doc in existing_docs:
            meta = doc.meta or {}
            doc_id = meta.get("document_id")
            filename = meta.get("filename", "unknown")
            if doc_id and doc_id not in documents_db:
                documents_db[doc_id] = {"filename": filename}
        if documents_db:
            logger.info(f"Hydrated {len(documents_db)} documents from FAISS store")
    except Exception as e:
        logger.warning(f"Failed to hydrate documents from store: {e}")

hydrate_documents_from_store()

# Small-talk KB (loaded from Postgres knowledge_base)
DATABASE_URL = os.getenv("DATABASE_URL")
db_engine = create_engine(DATABASE_URL) if DATABASE_URL else None
smalltalk_kb: List[dict] = []

def load_smalltalk_kb() -> None:
    global smalltalk_kb
    if not db_engine:
        smalltalk_kb = []
        return
    try:
        with db_engine.connect() as conn:
            rows = conn.execute(sql_text(
                """
                select question, answer, coalesce(lower(category), '') as category
                from knowledge_base
                where lower(category) in ('greeting','smalltalk')
                order by id asc
                """
            )).mappings().all()
            smalltalk_kb = [
                {
                    "q": (r["question"] or "").strip().lower(),
                    "a": (r["answer"] or "").strip(),
                    "c": r["category"] or ""
                }
                for r in rows
                if (r["question"] or "").strip()
            ]
            logger.info(f"Loaded smalltalk KB items: {len(smalltalk_kb)}")
    except Exception as e:
        logger.warning(f"Failed loading smalltalk KB: {e}")

# load at startup
load_smalltalk_kb()

def has_any_indexed_document() -> bool:
    """Return True if there is at least one uploaded/indexed document in DB or in-memory store."""
    try:
        if document_store.count_documents() > 0:
            return True
    except Exception:
        pass
    # check postgres documents table as source of truth
    if db_engine is not None:
        try:
            with db_engine.connect() as conn:
                row = conn.execute(sql_text("select count(1) as c from documents"));
                c = list(row)[0][0]
                return int(c) > 0
        except Exception as e:
            logger.warning(f"documents count check failed: {e}")
    return False

# Pydantic models
class HistoryItem(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    history: Optional[List[HistoryItem]] = None

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
        "documents_count": document_store.count_documents(),
        "smalltalk_kb": len(smalltalk_kb)
    }

@app.post("/api/reload_kb")
def reload_kb():
    """Reload smalltalk/greeting knowledge base from Postgres without restart."""
    load_smalltalk_kb()
    return {"status": "ok", "smalltalk_kb": len(smalltalk_kb)}

def build_llm_prompt(query: str, contexts: List[Document], history: Optional[List[HistoryItem]] = None) -> List[dict]:
    ctx_texts = []
    # Increased context window: use top 5 documents with more text per doc
    for d in contexts[:5]:
        name = d.meta.get("filename", "dokuman") if hasattr(d, "meta") else "dokuman"
        snippet = d.content.strip()
        if len(snippet) > 2000:  # Increased from 1200 to 2000
            snippet = snippet[:2000] + "..."
        ctx_texts.append(f"[Kaynak: {name}]\n{snippet}")
    ctx_block = "\n\n---\n\n".join(ctx_texts) if ctx_texts else "Bağlam yok."
    
    # Build conversation history context
    history_text = ""
    if history and len(history) > 0:
        history_lines = []
        for h in history[-4:]:  # Last 4 messages for context
            role_label = "Kullanıcı" if h.role == "user" else "Asistan"
            history_lines.append(f"{role_label}: {h.content}")
        history_text = "\n\nÖNCEKİ KONUŞMA:\n" + "\n".join(history_lines)
    
    system = (
        "Sen yardımcı bir asistansın. Aşağıdaki KURAL SETİNE harfiyen uy:\n"
        "1. Sadece verilen BAĞLAM (context) içindeki bilgileri kullan.\n"
        "2. Asla 'Merhaba', 'Size nasıl yardımcı olabilirim' gibi giriş cümleleri kurma. DOĞRUDAN cevabı ver.\n"
        "3. Bağlamda cevabı bulamazsan sadece 'Bu konuda dokümanda bilgi bulunamadı.' de.\n"
        "4. Cevabın net, kısa ve Türkçe olsun.\n"
        "5. Asla kendi kendine soru üretme veya kullanıcıya ne sorması gerektiğini söyleme.\n"
        "6. Önceki konuşmayı dikkate al ve tutarlı cevaplar ver."
    )
    
    user = f"BAĞLAM:\n{ctx_block}{history_text}\n\nSORU: {query}\n\nCEVAP:"
    
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

def try_generate_with_llm(query: str, docs: List[Document], history: Optional[List[HistoryItem]] = None) -> Tuple[Optional[str], float]:
    try:
        messages = build_llm_prompt(query, docs, history)
        text = call_chat_completion(messages, temperature=0.3, max_tokens=600)
        if text and len(text) > 20:  # Ensure meaningful response
            return text, 0.88
    except Exception as e:
        logger.warning(f"LLM generation failed: {e}")
    return None, 0.0

def try_summarize_with_llm(query: str, docs: List[Document]) -> Optional[str]:
    try:
        ctx = docs[:3]
        ctx_texts = []
        for d in ctx:
            name = d.meta.get("filename", "dokuman") if hasattr(d, "meta") else "dokuman"
            text = d.content.strip()
            if len(text) > 1800:
                text = text[:1800] + "..."
            ctx_texts.append(f"[Kaynak: {name}]\n{text}")
        system = (
            "Aşağıdaki bağlamdan hareketle Türkçe kısa (3-5 cümle) öz bir özet ver. Rakamları doğru aktar, uydurma."
        )
        user = f"İstek: {query}\n\nBağlam:\n" + "\n\n".join(ctx_texts)
        return call_chat_completion(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
            max_tokens=300,
        )
    except Exception as e:
        logger.warning(f"LLM summarize failed: {e}")
        return None

def try_generate_question(docs: List[Document]) -> Optional[str]:
    if not docs:
        return None
    try:
        sample = docs[0].content.strip()
        if len(sample) > 1200:
            sample = sample[:1200] + "..."
        system = "Bağlama uygun, tek cümlelik bir sınav sorusu üret. Türkçe ve net olsun."
        user = f"Bağlam:\n{sample}\n\nTalep: Bu bağlama dayalı bir soru üret."
        return call_chat_completion(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.5,
            max_tokens=120,
        )
    except Exception as e:
        logger.warning(f"LLM question-gen failed: {e}")
        return None

def is_small_talk(text: str) -> Tuple[bool, Optional[str]]:
    t = (text or "").strip().lower()
    if not t or len(t) <= 2:
        return True, None
    
    # normalize casual apostrophes
    t = t.replace("'", "").replace("'", "")
    
    # 1) DB-backed patterns first (exact match only)
    for item in smalltalk_kb:
        q = item["q"]
        if not q:
            continue
        if q == t:  # Only exact match, not substring
            return True, item.get("a")
    
    # 2) Greetings and casual chat patterns
    exact_triggers = [
        "merhaba", "selam", "alo", "günaydın", "iyi akşamlar", "iyi geceler",
        "hey", "naber", "nasılsın", "iyi misin", "nasıl gidiyor", "nasilsin",
        "iyi misiniz", "iyimisin", "iyi msiin", "iyimsiin"
    ]
    # Only match if the ENTIRE query is just the greeting (no other words)
    if t in exact_triggers:
        return True, None
    
    # 3) Casual conversation patterns (not document queries)
    casual_patterns = [
        "ben de iyiyim", "bende iyiyim", "ne yapıyorsun", "ne yapıyon", "ne yapiyorsun",
        "teşekkürler", "tesekkurler", "sağol", "sagol", "eyvallah",
        "görüşürüz", "gorusuruz", "hoşçakal", "hoscakal", "bye", "bb",
        "çok düşünüyorsun", "cok dusunuyorsun", "yavaşsın", "yavasin",
        "adam gibi cevap ver", "düzgün cevap ver", "duzgun cevap ver",
        "bu nasıl cevap", "bu nasil cevap", "saçmalama", "sacmalama",
        "anlamadım", "anlamadim", "tekrar söyle", "tekrar soyle",
        "tamam", "ok", "evet", "hayır", "hayir", "peki", "olur", "olmaz",
        "güzel", "guzel", "harika", "süper", "super", "kötü", "kotu",
        "seni seviyorum", "seni sevmiyorum", "aptal", "salak", "mal"
    ]
    if t in casual_patterns or any(t.startswith(p) for p in casual_patterns):
        return True, None
    
    # 4) Check if message looks like casual chat (no technical/document keywords)
    doc_keywords = [
        "pdf", "doküman", "dokuman", "dosya", "belge", "yükle", "yukle",
        "nedir", "nelerdir", "nasıl", "nasil", "ne işe yarar", "ne ise yarar",
        "açıkla", "acikla", "anlat", "özet", "ozet", "tanım", "tanim",
        "örnek", "ornek", "kod", "fonksiyon", "metot", "metod", "method",
        "dizi", "array", "class", "sınıf", "sinif", "değişken", "degisken",
        "length", "sort", "copy", "index", "params", "recursive"
    ]
    has_doc_keyword = any(kw in t for kw in doc_keywords)
    
    # If no document keyword and message is short casual text, treat as small talk
    if not has_doc_keyword and len(t.split()) <= 5:
        # Check if it's just casual words
        casual_words = ["ben", "sen", "biz", "siz", "de", "da", "mi", "mı", "mu", "mü", 
                        "ya", "yaw", "yaa", "hadi", "abi", "lan", "la", "le"]
        words = t.split()
        casual_count = sum(1 for w in words if w in casual_words or len(w) <= 2)
        if casual_count >= len(words) * 0.5:  # More than half are casual words
            return True, None
    
    return False, None

def llm_small_talk_answer(text: str) -> Optional[str]:
    try:
        system = (
            "Kısa ve nazik Türkçe yanıt ver. Kullanıcının doküman sormadığı, selamlaşma ya da basit sohbet"
            " içeriği ise 1-2 cümlelik cevap ver; belirsiz ya da uygunsuz içeriklerde yönlendirici sorular sor."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text.strip()}
        ]
        return call_chat_completion(messages, temperature=0.6, max_tokens=120)
    except Exception as e:
        logger.warning(f"LLM small talk failed: {e}")
        return None

# ---- Lightweight intent detection -------------------------------------------------------------
def detect_intent(text: str) -> str:
    """Return one of: smalltalk, summarize, define, list, numeric, clarify, doc"""
    q = (text or "").strip().lower()
    if not q or len(q) <= 2:
        return "clarify"
    
    st, _ = is_small_talk(q)
    if st:
        return "smalltalk"
    
    # Intent detection: only trigger if query has specific keywords
    if any(k in q for k in ["özet", "ozet", "kısaca", "kisaca", "özetini", "özetler", "summary"]):
        return "summarize"
    if any(k in q for k in ["nedir", "tanımı", "tanim", "açıkla", "acikla", "kimdir", "ne demek", "tanımla"]):
        return "define"
    if any(k in q for k in ["nelerdir", "hangileri", "listesi", "çeşitleri", "turleri", "türleri", "madde madde"]):
        return "list"
    
    # Default: assume it's a document query (most permissive)
    return "doc"

def detect_intent_with_llm(text: str) -> str:
    # Disable LLM-based intent - too aggressive, always returns 'doc' by default now
    return detect_intent(text)

def llm_clarify_followup(text: str) -> Optional[str]:
    try:
        messages = [
            {"role": "system", "content": "Kullanıcıya nazikçe netleştirici kısa bir soru sor. Türkçe sorun. 1 cümle."},
            {"role": "user", "content": f"Kullanıcı girdisi: {text}"}
        ]
        return call_chat_completion(messages, temperature=0.5, max_tokens=60)
    except Exception as e:
        logger.warning(f"LLM clarify failed: {e}")
        return None

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
        # Optional: attach embedding for semantic retrieval
        vec = get_embedding(request.content[:4000])
        if vec is not None:
            doc.meta["embedding"] = vec
        
        # Store in document store
        document_store.write_documents([doc])
        persist_document_store()
        
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
                # C# / Programming terms
                "length": "Length dizinin uzunluğu eleman sayısı",
                "metot": "metot metod method fonksiyon",
                "metod": "metot metod method fonksiyon",
                "dizi": "dizi array diziler",
                "array": "dizi array diziler",
                "aşırı yükleme": "aşırı yükleme overloading overload",
                "asiri yukleme": "aşırı yükleme overloading overload",
                "recursive": "recursive özyinelemeli kendini çağıran",
                "özyinelemeli": "recursive özyinelemeli kendini çağıran",
                "get set": "get set property özellik",
                "params": "params değişken sayıda parametre",
                "copyto": "CopyTo Copy kopyala kopyalama",
                "sort": "Sort sıralama sırala Array.Sort",
            }
            extra = []
            for k, v in synonyms.items():
                if k in base:
                    extra.append(v)
            
            # Extract key terms for better matching
            # Remove question words to focus on actual terms
            question_words = ["ne", "nedir", "nelerdir", "nasıl", "nasil", "hangi", "kaç", "kac", 
                              "işe", "ise", "yarar", "demek", "anlat", "açıkla", "acikla", "özet", "ozet"]
            key_terms = [w for w in base.split() if w not in question_words and len(w) > 2]
            if key_terms:
                extra.extend(key_terms)
            
            # If very short (<=3 words) treat as definition question
            words = base.split()
            if len(words) <= 3:
                extra.append("nedir tanımı açıklama definition kullanımı örnek")
            return (base + " " + " ".join(extra)).strip()

        request.query = normalize(request.query)
        # LLM destekli intent (yoksa kurallı)
        user_intent = detect_intent_with_llm(request.query)
        expanded_query = expand_query(request.query)

        # Early route: handle smalltalk/clarify immediately (regardless of document count)
        if user_intent == "smalltalk":
            _, kb_ans = is_small_talk(request.query)
            st = kb_ans or llm_small_talk_answer(request.query)
            if st:
                return QueryResponse(answer=st, confidence=0.7, source="llm", documents=[])
        if user_intent == "clarify":
            ask = llm_clarify_followup(request.query) or "Tam olarak hangi konudan bahsediyorsunuz? Biraz açar mısınız?"
            return QueryResponse(answer=ask, confidence=0.0, source="none", documents=[])

        if not has_any_indexed_document():
            # Small talk fallback even when there are no documents
            _, kb_ans = is_small_talk(request.query)
            if kb_ans:
                return QueryResponse(answer=kb_ans, confidence=0.7, source="llm", documents=[])
            return QueryResponse(
                answer="Henüz sisteme yüklenmiş doküman bulunmamaktadır.",
                confidence=0.0,
                source="none",
                documents=[]
            )
        
        # Create retriever
        retriever = InMemoryBM25Retriever(document_store=document_store)
        
        # Retrieve relevant documents (lexical) - increased to 15 for better coverage
        results = retriever.run(query=expanded_query, top_k=max(15, request.top_k))

        # Guard: no documents or no retrieval result
        if not results or "documents" not in results or not results["documents"]:
            # If there is an LLM and the user is doing small talk, answer generatively without citing docs
            if user_intent == "smalltalk":
                _, kb_ans = is_small_talk(request.query)
                st = kb_ans or llm_small_talk_answer(request.query)
                if st:
                    return QueryResponse(answer=st, confidence=0.7, source="llm", documents=[])
            if user_intent == "clarify":
                ask = llm_clarify_followup(request.query) or "Tam olarak hangi başlık hakkında konuşmak istersiniz?"
                return QueryResponse(answer=ask, confidence=0.0, source="none", documents=[])
            return QueryResponse(
                answer="Bu konuda ilgili bir bilgi bulunamadı.",
                confidence=0.0,
                source="none",
                documents=[]
            )
        
        # Apply semantic reranking if embeddings available
        docs: List[Document] = results["documents"]
        query_vec = get_embedding(expanded_query)
        combined = []
        for d in docs:
            bm25 = float(d.score) if hasattr(d, "score") and d.score is not None else 0.0
            sem = 0.0
            if query_vec is not None and d.meta and d.meta.get("embedding") is not None:
                sem = cosine(query_vec, d.meta.get("embedding"))  # 0..1
            # Combine: give semantic higher weight if available
            combined_score = (0.6 * sem) + (0.4 * (bm25 if bm25 <= 1 else bm25 / 10.0))
            combined.append((combined_score, d, bm25, sem))
        combined.sort(key=lambda x: x[0], reverse=True)
        docs = [d for _, d, _, _ in combined]

        # Apply a minimal relevance threshold to avoid irrelevant answers
        # Very low threshold to allow more documents through for LLM to evaluate
        score_threshold = 0.02  # very permissive for better recall on short queries
        filtered_docs = []
        for (cs, d, bm, sem) in combined:
            if cs >= score_threshold:
                filtered_docs.append(d)

        if not filtered_docs:
            # Small talk fallback if available
            if user_intent == "smalltalk":
                _, kb_ans = is_small_talk(request.query)
                st = kb_ans or llm_small_talk_answer(request.query)
                if st:
                    return QueryResponse(answer=st, confidence=0.7, source="llm", documents=[])
            if user_intent == "clarify":
                ask = llm_clarify_followup(request.query) or "Hangi detayları öğrenmek istersiniz?"
                return QueryResponse(answer=ask, confidence=0.0, source="none", documents=[])
            return QueryResponse(
                answer="Bu konuda ilgili bir bilgi bulunamadı.",
                confidence=0.0,
                source="none",
                documents=[]
            )

        # Get the best matching document after filtering
        best_doc = filtered_docs[0]
        
        # Build context from retrieved documents
        contexts = []
        for doc in filtered_docs:
            score = doc.score if hasattr(doc, 'score') else 0.5
            contexts.append(DocumentContext(
                content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                document_name=doc.meta.get("filename", "unknown"),
                score=float(score)
            ))
        
        # Intent checks
        ql = request.query.lower()
        wants_summary = any(k in ql for k in ["özet", "ozet", "özeti", "ozeti", "kısaca", "kisaca"])  
        wants_question = "dokümandan soru sor" in ql or "dokumandan soru sor" in ql

        # If intent is summary and we have docs, summarize
        if wants_summary and filtered_docs:
            summary = try_summarize_with_llm(request.query, filtered_docs)
            if summary:
                return QueryResponse(
                    answer=summary,
                    confidence=0.85,
                    source="summary",
                    documents=contexts
                )

        # If intent is question generation
        if wants_question and filtered_docs:
            q = try_generate_question(filtered_docs)
            if q:
                return QueryResponse(
                    answer=q,
                    confidence=0.8,
                    source="question",
                    documents=contexts
                )

        # If LLM is configured AND we have at least one relevant doc, try generative answer
        llm_answer, llm_conf = (None, 0.0)
        if filtered_docs:
            llm_answer, llm_conf = try_generate_with_llm(request.query, filtered_docs, request.history)
        
        if llm_answer:
            contexts = []
            for doc in filtered_docs[:3]: # Return top 3 docs as source
                score = doc.score if hasattr(doc, 'score') else 0.5
                contexts.append(DocumentContext(
                    content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    document_name=doc.meta.get("filename", "unknown"),
                    score=float(score)
                ))
            return QueryResponse(
                answer=llm_answer,
                confidence=float(llm_conf),
                source="document",  # Force source to 'document' if LLM answered from context
                documents=contexts
            )

        # Query-aware answer extraction (extractive fallback)
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

