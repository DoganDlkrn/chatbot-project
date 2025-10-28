using ChatbotAPI.Services;
using Microsoft.AspNetCore.Mvc;

namespace ChatbotAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DocumentsController : ControllerBase
{
    private readonly IDocumentService _documentService;
    private readonly ILogger<DocumentsController> _logger;

    public DocumentsController(IDocumentService documentService, ILogger<DocumentsController> logger)
    {
        _documentService = documentService;
        _logger = logger;
    }

    [HttpPost("upload")]
    public async Task<IActionResult> Upload(IFormFile file)
    {
        try
        {
            if (file == null || file.Length == 0)
            {
                return BadRequest(new { error = "No file uploaded" });
            }

            var document = await _documentService.UploadDocumentAsync(file);
            return Ok(new
            {
                id = document.Id,
                filename = document.OriginalFilename,
                size = document.FileSize,
                uploaded_at = document.UploadedAt,
                indexed = document.Indexed
            });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error uploading file: {ex.Message}");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        try
        {
            var documents = await _documentService.GetAllDocumentsAsync();
            return Ok(documents.Select(d => new
            {
                id = d.Id,
                filename = d.OriginalFilename,
                file_type = d.FileType,
                size = d.FileSize,
                uploaded_at = d.UploadedAt,
                indexed = d.Indexed
            }));
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error getting documents: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        try
        {
            var document = await _documentService.GetDocumentByIdAsync(id);
            if (document == null)
            {
                return NotFound(new { error = "Document not found" });
            }

            return Ok(new
            {
                id = document.Id,
                filename = document.OriginalFilename,
                file_type = document.FileType,
                size = document.FileSize,
                uploaded_at = document.UploadedAt,
                indexed = document.Indexed
            });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error getting document: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        try
        {
            var result = await _documentService.DeleteDocumentAsync(id);
            if (!result)
            {
                return NotFound(new { error = "Document not found" });
            }

            return Ok(new { message = "Document deleted successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error deleting document: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }
}

