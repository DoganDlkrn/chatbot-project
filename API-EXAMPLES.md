# API Kullanım Örnekleri

## Base URL

```
Local: http://localhost:5000
Haystack: http://localhost:8001
```

## Chat API

### 1. Health Check

**Request:**
```bash
curl http://localhost:5000/api/chat/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00Z"
}
```

### 2. Yeni Sohbet Başlat

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Merhaba, nasılsın?"
  }'
```

**Response:**
```json
{
  "sessionId": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Merhaba! Ben bir yapay zeka asistanıyım ve her zaman hazırım! Size nasıl yardımcı olabilirim?",
  "source": "database",
  "confidence": 95.0,
  "timestamp": "2025-10-22T10:30:00Z"
}
```

### 3. Mevcut Session ile Devam Et

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "123e4567-e89b-12d3-a456-426614174000",
    "message": "Yüklediğim PDF hakkında soru sorabilir miyim?"
  }'
```

**Response:**
```json
{
  "sessionId": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Evet, yüklediğiniz PDF dokümanlar hakkında sorular sorabilirsiniz...",
  "source": "document",
  "confidence": 87.5,
  "timestamp": "2025-10-22T10:31:00Z"
}
```

## Document API

### 1. Doküman Yükle (PDF)

**Request:**
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "size": 245678,
  "uploaded_at": "2025-10-22T10:35:00Z",
  "indexed": false
}
```

### 2. Doküman Yükle (TXT)

**Request:**
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/notes.txt"
```

**Response:**
```json
{
  "id": 2,
  "filename": "notes.txt",
  "size": 1234,
  "uploaded_at": "2025-10-22T10:36:00Z",
  "indexed": false
}
```

### 3. Tüm Dokümanları Listele

**Request:**
```bash
curl http://localhost:5000/api/documents
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "file_type": ".pdf",
    "size": 245678,
    "uploaded_at": "2025-10-22T10:35:00Z",
    "indexed": true
  },
  {
    "id": 2,
    "filename": "notes.txt",
    "file_type": ".txt",
    "size": 1234,
    "uploaded_at": "2025-10-22T10:36:00Z",
    "indexed": true
  }
]
```

### 4. Belirli Doküman Detayı

**Request:**
```bash
curl http://localhost:5000/api/documents/1
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_type": ".pdf",
  "size": 245678,
  "uploaded_at": "2025-10-22T10:35:00Z",
  "indexed": true
}
```

### 5. Doküman Sil

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/documents/1
```

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

## Haystack Service API

### 1. Health Check

**Request:**
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "documents_count": 5
}
```

### 2. Doküman Sorgula

**Request:**
```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PDF içindeki önemli bilgiler neler?",
    "top_k": 3
  }'
```

**Response:**
```json
{
  "answer": "PDF dosyasında şu önemli bilgiler bulunmaktadır: ...",
  "confidence": 0.85,
  "source": "document",
  "documents": [
    {
      "content": "İlgili metin parçası 1...",
      "document_name": "document.pdf",
      "score": 0.92
    },
    {
      "content": "İlgili metin parçası 2...",
      "document_name": "document.pdf",
      "score": 0.87
    }
  ]
}
```

### 3. Doküman İndeksle (Direct)

**Request:**
```bash
curl -X POST http://localhost:8001/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "filename": "test.pdf",
    "content": "Bu bir test dokümanıdır..."
  }'
```

**Response:**
```json
{
  "status": "success",
  "document_id": 1,
  "filename": "test.pdf",
  "total_documents": 6
}
```

### 4. İndeksli Dokümanları Listele

**Request:**
```bash
curl http://localhost:8001/api/documents
```

**Response:**
```json
{
  "total": 5,
  "documents": [
    {
      "document_id": 1,
      "filename": "document.pdf"
    },
    {
      "document_id": 2,
      "filename": "notes.txt"
    }
  ]
}
```

## Postman Collection

### İçe Aktarılabilir JSON

```json
{
  "info": {
    "name": "Chatbot API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Chat",
      "item": [
        {
          "name": "Health Check",
          "request": {
            "method": "GET",
            "url": "{{baseUrl}}/api/chat/health"
          }
        },
        {
          "name": "Send Message",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/chat",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"message\": \"Merhaba\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Documents",
      "item": [
        {
          "name": "Upload Document",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/documents/upload",
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "file",
                  "type": "file",
                  "src": ""
                }
              ]
            }
          }
        },
        {
          "name": "List Documents",
          "request": {
            "method": "GET",
            "url": "{{baseUrl}}/api/documents"
          }
        },
        {
          "name": "Get Document",
          "request": {
            "method": "GET",
            "url": "{{baseUrl}}/api/documents/1"
          }
        },
        {
          "name": "Delete Document",
          "request": {
            "method": "DELETE",
            "url": "{{baseUrl}}/api/documents/1"
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:5000"
    }
  ]
}
```

## Python Örneği

```python
import requests

# Chat
def send_message(message, session_id=None):
    url = "http://localhost:5000/api/chat"
    payload = {"message": message}
    if session_id:
        payload["sessionId"] = session_id
    
    response = requests.post(url, json=payload)
    return response.json()

# Document Upload
def upload_document(file_path):
    url = "http://localhost:5000/api/documents/upload"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    return response.json()

# Kullanım
result = send_message("Merhaba!")
print(result)

doc_result = upload_document("/path/to/document.pdf")
print(doc_result)
```

## JavaScript/Node.js Örneği

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Chat
async function sendMessage(message, sessionId = null) {
  const url = 'http://localhost:5000/api/chat';
  const payload = { message };
  if (sessionId) payload.sessionId = sessionId;
  
  const response = await axios.post(url, payload);
  return response.data;
}

// Document Upload
async function uploadDocument(filePath) {
  const url = 'http://localhost:5000/api/documents/upload';
  const formData = new FormData();
  formData.append('file', fs.createReadStream(filePath));
  
  const response = await axios.post(url, formData, {
    headers: formData.getHeaders()
  });
  return response.data;
}

// Kullanım
(async () => {
  const result = await sendMessage('Merhaba!');
  console.log(result);
  
  const docResult = await uploadDocument('/path/to/document.pdf');
  console.log(docResult);
})();
```

## C# Örneği

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class ChatbotClient
{
    private readonly HttpClient _client;
    
    public ChatbotClient()
    {
        _client = new HttpClient
        {
            BaseAddress = new Uri("http://localhost:5000")
        };
    }
    
    public async Task<ChatResponse> SendMessageAsync(string message, Guid? sessionId = null)
    {
        var request = new { message, sessionId };
        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await _client.PostAsync("/api/chat", content);
        var responseJson = await response.Content.ReadAsStringAsync();
        
        return JsonSerializer.Deserialize<ChatResponse>(responseJson);
    }
    
    public async Task<DocumentResponse> UploadDocumentAsync(string filePath)
    {
        using var form = new MultipartFormDataContent();
        var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
        form.Add(fileContent, "file", Path.GetFileName(filePath));
        
        var response = await _client.PostAsync("/api/documents/upload", form);
        var responseJson = await response.Content.ReadAsStringAsync();
        
        return JsonSerializer.Deserialize<DocumentResponse>(responseJson);
    }
}

// Kullanım
var client = new ChatbotClient();
var result = await client.SendMessageAsync("Merhaba!");
Console.WriteLine(result.Message);
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Message is required"
}
```

### 404 Not Found

```json
{
  "error": "Document not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Rate Limiting (Future)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634912400
```

## Swagger/OpenAPI

Swagger UI'a erişmek için:

```
http://localhost:5000/swagger
```

Buradan tüm endpoint'leri test edebilir ve API dokümantasyonunu görebilirsiniz.

