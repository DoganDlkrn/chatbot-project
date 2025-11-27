namespace ChatbotAPI.Models.DTOs;

public class TeachRequest
{
    public string Question { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public string? Category { get; set; }
    public string[]? Keywords { get; set; }
}




