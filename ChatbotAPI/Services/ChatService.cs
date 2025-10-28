using ChatbotAPI.Data;
using ChatbotAPI.Models;
using ChatbotAPI.Models.DTOs;
using Microsoft.EntityFrameworkCore;

namespace ChatbotAPI.Services;

public class ChatService : IChatService
{
    private readonly ChatbotDbContext _context;
    private readonly IHaystackService _haystackService;
    private readonly ILogger<ChatService> _logger;

    public ChatService(
        ChatbotDbContext context,
        IHaystackService haystackService,
        ILogger<ChatService> logger)
    {
        _context = context;
        _haystackService = haystackService;
        _logger = logger;
    }

    public async Task<ChatResponse> ProcessMessageAsync(ChatRequest request)
    {
        try
        {
            // Get or create session
            Guid sessionId = request.SessionId ?? Guid.NewGuid();
            var session = await _context.ChatSessions
                .FirstOrDefaultAsync(s => s.SessionId == sessionId);

            if (session == null)
            {
                session = new ChatSession { SessionId = sessionId };
                _context.ChatSessions.Add(session);
                // Save session first to avoid foreign key constraint
                await _context.SaveChangesAsync();
            }
            else
            {
                session.LastActivity = DateTime.UtcNow;
                await _context.SaveChangesAsync();
            }

            // Save user message
            var userMessage = new ChatMessage
            {
                SessionId = sessionId,
                MessageType = "user",
                Message = request.Message
            };
            _context.ChatMessages.Add(userMessage);
            await _context.SaveChangesAsync();

            // Try to find answer in knowledge base first
            var knowledgeAnswer = await SearchKnowledgeBaseAsync(request.Message);
            
            if (knowledgeAnswer != null)
            {
                var botMessage = new ChatMessage
                {
                    SessionId = sessionId,
                    MessageType = "bot",
                    Message = knowledgeAnswer.Answer,
                    Source = "database",
                    Confidence = 95.0m
                };
                _context.ChatMessages.Add(botMessage);
                await _context.SaveChangesAsync();

                return new ChatResponse
                {
                    SessionId = sessionId,
                    Message = knowledgeAnswer.Answer,
                    Source = "database",
                    Confidence = 95.0m
                };
            }

            // Try Haystack for document search
            try
            {
                var haystackResponse = await _haystackService.QueryAsync(new HaystackRequest
                {
                    Query = request.Message,
                    TopK = 3
                });

                if (haystackResponse != null && haystackResponse.Confidence > 0.5m)
                {
                    var botMessage = new ChatMessage
                    {
                        SessionId = sessionId,
                        MessageType = "bot",
                        Message = haystackResponse.Answer,
                        Source = "document",
                        Confidence = haystackResponse.Confidence * 100
                    };
                    _context.ChatMessages.Add(botMessage);
                    await _context.SaveChangesAsync();

                    return new ChatResponse
                    {
                        SessionId = sessionId,
                        Message = haystackResponse.Answer,
                        Source = "document",
                        Confidence = haystackResponse.Confidence * 100
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning($"Haystack service error: {ex.Message}");
            }

            // Default response if no answer found
            var defaultResponse = "Üzgünüm, bu konuda yeterli bilgiye sahip değilim. Lütfen sorunuzu farklı bir şekilde sorar mısınız veya daha fazla bilgi sağlayabilir misiniz?";
            var defaultMessage = new ChatMessage
            {
                SessionId = sessionId,
                MessageType = "bot",
                Message = defaultResponse,
                Source = "none",
                Confidence = 0
            };
            _context.ChatMessages.Add(defaultMessage);
            await _context.SaveChangesAsync();

            return new ChatResponse
            {
                SessionId = sessionId,
                Message = defaultResponse,
                Source = "none",
                Confidence = 0
            };
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error processing message: {ex.Message}");
            throw;
        }
    }

    private async Task<KnowledgeBase?> SearchKnowledgeBaseAsync(string query)
    {
        query = query.ToLower().Trim();
        
        // Simple keyword matching
        var knowledge = await _context.KnowledgeBase
            .Where(k => k.Keywords != null && k.Keywords.Any(kw => query.Contains(kw.ToLower())))
            .FirstOrDefaultAsync();

        return knowledge;
    }
}

