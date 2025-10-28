using ChatbotAPI.Models.DTOs;
using System.Text;
using System.Text.Json;

namespace ChatbotAPI.Services;

public class HaystackService : IHaystackService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<HaystackService> _logger;

    public HaystackService(HttpClient httpClient, ILogger<HaystackService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<HaystackResponse?> QueryAsync(HaystackRequest request)
    {
        try
        {
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            var response = await _httpClient.PostAsync("/api/query", content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<HaystackResponse>(responseContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
            }
            
            _logger.LogWarning($"Haystack query failed: {response.StatusCode}");
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error querying Haystack: {ex.Message}");
            return null;
        }
    }

    public async Task<bool> IndexDocumentAsync(int documentId, string filename, string content)
    {
        try
        {
            var request = new
            {
                document_id = documentId,
                filename = filename,
                content = content
            };

            var json = JsonSerializer.Serialize(request);
            var httpContent = new StringContent(json, Encoding.UTF8, "application/json");
            
            var response = await _httpClient.PostAsync("/api/index", httpContent);
            
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation($"Document {documentId} indexed successfully in Haystack");
                return true;
            }
            
            _logger.LogWarning($"Haystack indexing failed: {response.StatusCode}");
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error indexing document in Haystack: {ex.Message}");
            return false;
        }
    }
}

