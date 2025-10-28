namespace ChatbotAPI.Models;

public class ChatSession
{
    public int Id { get; set; }
    public Guid SessionId { get; set; } = Guid.NewGuid();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime LastActivity { get; set; } = DateTime.UtcNow;
}

