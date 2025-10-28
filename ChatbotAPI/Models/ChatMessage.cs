namespace ChatbotAPI.Models;

public class ChatMessage
{
    public int Id { get; set; }
    public Guid SessionId { get; set; }
    public string MessageType { get; set; } = string.Empty; // "user" or "bot"
    public string Message { get; set; } = string.Empty;
    public string? Source { get; set; } // "database", "document", "none"
    public decimal? Confidence { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

