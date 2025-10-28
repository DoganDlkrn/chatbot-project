using ChatbotAPI.Models.DTOs;

namespace ChatbotAPI.Services;

public interface IChatService
{
    Task<ChatResponse> ProcessMessageAsync(ChatRequest request);
}

