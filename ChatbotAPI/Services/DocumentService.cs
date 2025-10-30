using ChatbotAPI.Data;
using ChatbotAPI.Models;
using Microsoft.EntityFrameworkCore;
using System.Security.Cryptography;
using System.Text;
using UglyToad.PdfPig;

namespace ChatbotAPI.Services;

public class DocumentService : IDocumentService
{
    private readonly ChatbotDbContext _context;
    private readonly IHaystackService _haystackService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<DocumentService> _logger;
    private readonly string _uploadPath;

    public DocumentService(
        ChatbotDbContext context,
        IHaystackService haystackService,
        IConfiguration configuration,
        ILogger<DocumentService> logger)
    {
        _context = context;
        _haystackService = haystackService;
        _configuration = configuration;
        _logger = logger;
        _uploadPath = configuration["Upload:UploadPath"] ?? "uploads";
        
        if (!Directory.Exists(_uploadPath))
        {
            Directory.CreateDirectory(_uploadPath);
        }
    }

    public async Task<Document> UploadDocumentAsync(IFormFile file)
    {
        try
        {
            // Validate file
            var maxSize = (_configuration.GetValue<int>("Upload:MaxFileSizeMB", 10)) * 1024 * 1024;
            if (file.Length > maxSize)
            {
                throw new Exception($"File size exceeds maximum allowed size of {maxSize / (1024 * 1024)}MB");
            }

            var allowedExtensions = _configuration.GetSection("Upload:AllowedExtensions").Get<string[]>() 
                ?? new[] { ".pdf", ".txt", ".doc", ".docx" };
            var extension = System.IO.Path.GetExtension(file.FileName).ToLower();
            if (!allowedExtensions.Contains(extension))
            {
                throw new Exception($"File type {extension} is not allowed");
            }

            // Generate unique filename
            var uniqueFileName = $"{Guid.NewGuid()}{extension}";
            var filePath = System.IO.Path.Combine(_uploadPath, uniqueFileName);

            // Save file
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            // Calculate hash
            var hash = await CalculateFileHashAsync(filePath);

            // Create document record
            var document = new Document
            {
                Filename = uniqueFileName,
                OriginalFilename = file.FileName,
                FilePath = filePath,
                FileType = extension,
                FileSize = file.Length,
                ContentHash = hash,
                UploadedAt = DateTime.UtcNow,
                Indexed = false
            };

            _context.Documents.Add(document);
            await _context.SaveChangesAsync();

            // Index document asynchronously
            _ = Task.Run(async () => await IndexDocumentAsync(document.Id));

            return document;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error uploading document: {ex.Message}");
            throw;
        }
    }

    public async Task<List<Document>> GetAllDocumentsAsync()
    {
        return await _context.Documents
            .OrderByDescending(d => d.UploadedAt)
            .ToListAsync();
    }

    public async Task<Document?> GetDocumentByIdAsync(int id)
    {
        return await _context.Documents.FindAsync(id);
    }

    public async Task<bool> DeleteDocumentAsync(int id)
    {
        try
        {
            var document = await _context.Documents.FindAsync(id);
            if (document == null)
                return false;

            // Delete physical file
            if (File.Exists(document.FilePath))
            {
                File.Delete(document.FilePath);
            }

            // Delete from database
            _context.Documents.Remove(document);
            await _context.SaveChangesAsync();

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error deleting document: {ex.Message}");
            return false;
        }
    }

    public async Task<string> ExtractTextFromPdfAsync(string filePath)
    {
        try
        {
            var text = new StringBuilder();
            
            using (var document = PdfDocument.Open(filePath))
            {
                foreach (var page in document.GetPages())
                {
                    text.AppendLine(page.Text);
                }
            }

            var extractedText = text.ToString();
            if (string.IsNullOrWhiteSpace(extractedText))
            {
                return "PDF yüklendi ancak metin çıkarılamadı. Belge sadece görsel içerebilir.";
            }

            return await Task.FromResult(extractedText);
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error extracting text from PDF: {ex.Message}");
            return await Task.FromResult($"PDF metin çıkarma hatası: {ex.Message}");
        }
    }

    private async Task<string> CalculateFileHashAsync(string filePath)
    {
        using (var md5 = MD5.Create())
        {
            using (var stream = File.OpenRead(filePath))
            {
                var hash = await md5.ComputeHashAsync(stream);
                return BitConverter.ToString(hash).Replace("-", "").ToLower();
            }
        }
    }

        private async Task IndexDocumentAsync(int documentId)
        {
            try
            {
                var document = await _context.Documents.FindAsync(documentId);
                if (document == null)
                    return;

                // Extract text based on file type
                string text = string.Empty;
                if (document.FileType?.ToLower() == ".pdf")
                {
                    text = await ExtractTextFromPdfAsync(document.FilePath);
                }
                else if (document.FileType?.ToLower() == ".txt")
                {
                    text = await File.ReadAllTextAsync(document.FilePath);
                }

                if (!string.IsNullOrWhiteSpace(text))
                {
                    // Send to Haystack for indexing
                    await _haystackService.IndexDocumentAsync(document.Id, document.OriginalFilename, text);
                    
                    document.Indexed = true;
                    await _context.SaveChangesAsync();
                    
                    _logger.LogInformation($"Document {document.Id} indexed successfully");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error indexing document: {ex.Message}");
            }
        }
    }

