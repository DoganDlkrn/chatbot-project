namespace ChatbotAPI.Models.DTOs;

public class ChatResponse
{
    public Guid SessionId { get; set; }
    public string Message { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
    public decimal? Confidence { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

