namespace ChatbotAPI.Models;

public class Document
{
    public int Id { get; set; }
    public string Filename { get; set; } = string.Empty;
    public string OriginalFilename { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
    public string? FileType { get; set; }
    public long? FileSize { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    public bool Indexed { get; set; } = false;
    public string? ContentHash { get; set; }
}

