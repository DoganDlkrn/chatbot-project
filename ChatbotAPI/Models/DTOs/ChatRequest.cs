namespace ChatbotAPI.Models.DTOs;

public class ChatHistoryItem
{
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}

public class ChatRequest
{
    public Guid? SessionId { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ChatHistoryItem>? History { get; set; }
}

