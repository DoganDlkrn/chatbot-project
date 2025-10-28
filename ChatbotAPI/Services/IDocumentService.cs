using ChatbotAPI.Models;
using Microsoft.AspNetCore.Http;

namespace ChatbotAPI.Services;

public interface IDocumentService
{
    Task<Document> UploadDocumentAsync(IFormFile file);
    Task<List<Document>> GetAllDocumentsAsync();
    Task<Document?> GetDocumentByIdAsync(int id);
    Task<bool> DeleteDocumentAsync(int id);
    Task<string> ExtractTextFromPdfAsync(string filePath);
}

