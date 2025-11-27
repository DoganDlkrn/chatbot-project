namespace ChatbotAPI.Models.DTOs;

public class HaystackHistoryItem
{
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}

public class HaystackRequest
{
    public string Query { get; set; } = string.Empty;
    public int TopK { get; set; } = 3;
    public List<HaystackHistoryItem>? History { get; set; }
}

public class HaystackResponse
{
    public string Answer { get; set; } = string.Empty;
    public decimal Confidence { get; set; }
    public string Source { get; set; } = string.Empty;
    public List<DocumentContext>? Documents { get; set; }
}

public class DocumentContext
{
    public string Content { get; set; } = string.Empty;
    public string DocumentName { get; set; } = string.Empty;
    public decimal Score { get; set; }
}

