using ChatbotAPI.Models.DTOs;

namespace ChatbotAPI.Services;

public interface IHaystackService
{
    Task<HaystackResponse?> QueryAsync(HaystackRequest request);
    Task<bool> IndexDocumentAsync(int documentId, string filename, string content);
}

