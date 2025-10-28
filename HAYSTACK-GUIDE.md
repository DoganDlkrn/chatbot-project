# Haystack Framework Rehberi

## Haystack Nedir?

Haystack, doküman tabanlı soru-cevap (Question Answering) sistemleri oluşturmak için açık kaynaklı bir framework'tür. NLP (Natural Language Processing) ve arama teknolojilerini birleştirerek akıllı chatbot'lar oluşturmanıza olanak tanır.

## Temel Kavramlar

### 1. Document Store (Doküman Deposu)

Dokümanların saklandığı yer. Farklı backend'ler desteklenir:

- **InMemoryDocumentStore** - Basit, hafızada saklama (geliştirme için)
- **ElasticsearchDocumentStore** - Production için önerilen
- **PostgreSQL, MongoDB, Weaviate** - Diğer alternatifler

### 2. Retriever (Bilgi Getirici)

Sorguya en alakalı dokümanları bulan bileşen:

- **BM25Retriever** - Keyword tabanlı (hızlı, basit)
- **DenseRetriever** - Semantic arama (daha akıllı)
- **EmbeddingRetriever** - Vector tabanlı

### 3. Reader (Okuyucu)

Dokümanlardan cevap çıkaran bileşen:

- **TransformersReader** - BERT, RoBERTa gibi modeller
- **FARMReader** - Özelleştirilmiş modeller için

### 4. Pipeline (Boru Hattı)

Retriever ve Reader'ı birleştiren workflow:

```python
Pipeline:
Query → Retriever → Reader → Answer
```

## Projede Kullanım

### Mevcut Implementasyon

Bu projede **InMemoryDocumentStore** + **BM25Retriever** kullanılıyor:

```python
# Document Store
document_store = InMemoryDocumentStore()

# Document ekleme
document = Document(
    content="PDF içeriği buraya gelir",
    meta={"filename": "document.pdf"}
)
document_store.write_documents([document])

# Sorgulama
retriever = InMemoryBM25Retriever(document_store=document_store)
results = retriever.run(query="Kullanıcı sorusu", top_k=3)
```

### İleri Seviye: Elasticsearch ile Kullanım

Production ortamı için Elasticsearch önerilir:

```python
from haystack.document_stores import ElasticsearchDocumentStore

# Elasticsearch bağlantısı
document_store = ElasticsearchDocumentStore(
    host="elasticsearch",
    port=9200,
    index="chatbot_documents"
)

# Document indexleme
documents = [
    Document(content="...", meta={"source": "doc1.pdf"}),
    Document(content="...", meta={"source": "doc2.pdf"})
]
document_store.write_documents(documents)

# Elasticsearch üzerinden arama
from haystack.components.retrievers import ElasticsearchBM25Retriever
retriever = ElasticsearchBM25Retriever(document_store=document_store)
```

## Gelişmiş Özellikler

### 1. Semantic Search (Anlamsal Arama)

Keyword'ler yerine anlam bazlı arama:

```python
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever

# Embedder oluştur
embedder = SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

# Dokümanları embed et
docs_with_embeddings = embedder.run(documents)
document_store.write_documents(docs_with_embeddings.documents)

# Semantic retrieval
retriever = InMemoryEmbeddingRetriever(document_store=document_store)
```

### 2. Generative QA (GPT ile Cevap Üretme)

LLM kullanarak doğal cevaplar üretme:

```python
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

# Prompt template
template = """
Aşağıdaki dokümanları kullanarak soruyu cevapla.

Dokümanlar:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Soru: {{ query }}
Cevap:
"""

# Pipeline oluştur
prompt_builder = PromptBuilder(template=template)
generator = OpenAIGenerator(api_key="your-api-key")

# Pipeline çalıştır
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", generator)
```

### 3. Multi-Modal Search (Resim + Metin)

Hem metin hem resim içeren dokümanlar:

```python
from haystack.components.preprocessors import ImageTextProcessor

processor = ImageTextProcessor()
# PDF'den hem metin hem görseller çıkar
```

## Performans İyileştirme

### 1. Chunking (Dokümanları Parçalama)

Büyük dokümanları küçük parçalara bölme:

```python
from haystack.components.preprocessors import DocumentSplitter

splitter = DocumentSplitter(
    split_by="word",
    split_length=200,
    split_overlap=50
)

split_docs = splitter.run(documents=documents)
```

### 2. Filtering (Filtreleme)

Meta data ile filtreleme:

```python
# Sadece belirli dosya tiplerinde ara
results = retriever.run(
    query="soru",
    filters={"file_type": "pdf"}
)
```

### 3. Hybrid Search

BM25 + Semantic search birlikte:

```python
# Hem keyword hem semantic arama
from haystack.components.joiners import DocumentJoiner

joiner = DocumentJoiner()
# BM25 ve Embedding sonuçlarını birleştir
```

## Haystack ile Türkçe Desteği

### Türkçe Model Kullanımı

```python
# Türkçe BERT modeli
from haystack.nodes import FARMReader

reader = FARMReader(
    model_name_or_path="dbmdz/bert-base-turkish-cased",
    use_gpu=False
)

# Türkçe embedding modeli
embedder = SentenceTransformersDocumentEmbedder(
    model="emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
)
```

## Projeyi Geliştirme

### Mevcut Sistemden Elasticsearch'e Geçiş

1. **docker-compose.yml** - Elasticsearch zaten mevcut
2. **HaystackService/app.py** - Değiştir:

```python
# InMemoryDocumentStore yerine
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(
    hosts="http://elasticsearch:9200"
)
```

### LLM Entegrasyonu (OpenAI/Local)

**OpenAI ile:**

```python
from haystack.components.generators import OpenAIGenerator

generator = OpenAIGenerator(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4"
)
```

**Local LLM ile (Ollama):**

```python
from haystack.components.generators import HuggingFaceLocalGenerator

generator = HuggingFaceLocalGenerator(
    model="google/flan-t5-base"
)
```

### RAG (Retrieval-Augmented Generation)

Tam RAG pipeline:

```python
from haystack import Pipeline

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", generator)

rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")

# Çalıştır
result = rag_pipeline.run({
    "retriever": {"query": "Kullanıcı sorusu"},
    "prompt_builder": {"query": "Kullanıcı sorusu"}
})
```

## Monitoring ve Debug

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("haystack")
```

### Metrics

```python
# Retrieval performansı
from haystack.components.evaluators import DocumentMRREvaluator

evaluator = DocumentMRREvaluator()
# Precision, Recall, F1 hesapla
```

## Faydalı Kaynaklar

- **Resmi Dokümantasyon:** https://docs.haystack.deepset.ai/
- **GitHub:** https://github.com/deepset-ai/haystack
- **Tutorials:** https://haystack.deepset.ai/tutorials
- **Community:** https://discord.gg/VBpFzsgRVF

## Örnek Use Case'ler

1. **Customer Support Bot** - SSS dokümanlarından cevap bulma
2. **Legal Document Search** - Yasal doküman analizi
3. **Research Assistant** - Akademik makalelerden bilgi çıkarma
4. **Knowledge Base** - Şirket içi bilgi bankası
5. **E-commerce** - Ürün kataloğu arama

## Best Practices

1. ✅ Production'da Elasticsearch kullanın
2. ✅ Büyük dokümanları chunk'lara bölün
3. ✅ Meta data ile filtreleme yapın
4. ✅ Semantic search için embedding kullanın
5. ✅ Cache mekanizması ekleyin
6. ✅ Error handling yapın
7. ✅ Monitoring ekleyin
8. ✅ Regular index güncellemeleri yapın

## Sorun Giderme

**Slow queries:**
- Index boyutunu kontrol edin
- top_k değerini düşürün
- Cache kullanın

**Low accuracy:**
- Daha iyi embedding modeli kullanın
- Chunk size'ı optimize edin
- Hybrid search deneyin

**Memory issues:**
- InMemoryDocumentStore yerine Elasticsearch
- Lazy loading kullanın
- Batch processing yapın

