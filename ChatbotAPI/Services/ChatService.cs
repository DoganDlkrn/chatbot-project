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
                        Confidence = 0.95m
                };
                _context.ChatMessages.Add(botMessage);
                await _context.SaveChangesAsync();

                    return new ChatResponse
                {
                    SessionId = sessionId,
                    Message = knowledgeAnswer.Answer,
                    Source = "database",
                        Confidence = 0.95m
                };
            }

            // Try Haystack for document search
            try
            {
                var haystackHistory = request.History?.Select(h => new HaystackHistoryItem
                {
                    Role = h.Role,
                    Content = h.Content
                }).ToList();

                var haystackResponse = await _haystackService.QueryAsync(new HaystackRequest
                {
                    Query = request.Message,
                    TopK = 5,
                    History = haystackHistory
                });

                if (haystackResponse != null && !string.IsNullOrWhiteSpace(haystackResponse.Answer))
                {
                    var botMessage = new ChatMessage
                    {
                        SessionId = sessionId,
                        MessageType = "bot",
                        Message = haystackResponse.Answer,
                        Source = string.IsNullOrWhiteSpace(haystackResponse.Source) ? "document" : haystackResponse.Source,
                        Confidence = Math.Clamp((decimal)haystackResponse.Confidence, 0m, 1m)
                    };
                    _context.ChatMessages.Add(botMessage);
                    await _context.SaveChangesAsync();

                    return new ChatResponse
                    {
                        SessionId = sessionId,
                        Message = haystackResponse.Answer,
                        Source = string.IsNullOrWhiteSpace(haystackResponse.Source) ? "document" : haystackResponse.Source,
                        Confidence = Math.Clamp((decimal)haystackResponse.Confidence, 0m, 1m)
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
                Confidence = 0m
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

    public async Task<bool> TeachAsync(TeachRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Question) || string.IsNullOrWhiteSpace(request.Answer))
            {
                return false;
            }

            var kb = new KnowledgeBase
            {
                Question = request.Question.Trim(),
                Answer = request.Answer.Trim(),
                Category = request.Category,
                Keywords = request.Keywords,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };
            _context.KnowledgeBase.Add(kb);
            await _context.SaveChangesAsync();

            // Also index into Haystack as a lightweight synthetic document so retriever/LLM görebilsin
            var syntheticId = 100000 + kb.Id; // avoid collision with real docs
            var filename = $"knowledge:{kb.Category ?? "general"}#{kb.Id}";
            var content = $"Soru: {kb.Question}\nCevap: {kb.Answer}";
            try
            {
                await _haystackService.IndexDocumentAsync(syntheticId, filename, content);
            }
            catch (Exception ex)
            {
                _logger.LogWarning($"Failed to index KB item {kb.Id} into Haystack: {ex.Message}");
            }

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError($"TeachAsync failed: {ex.Message}");
            return false;
        }
    }
}

