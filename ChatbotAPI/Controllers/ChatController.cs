using ChatbotAPI.Models.DTOs;
using ChatbotAPI.Services;
using Microsoft.AspNetCore.Mvc;

namespace ChatbotAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly IChatService _chatService;
    private readonly ILogger<ChatController> _logger;

    public ChatController(IChatService chatService, ILogger<ChatController> logger)
    {
        _chatService = chatService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<ChatResponse>> Chat([FromBody] ChatRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(new { error = "Message is required" });
            }

            var response = await _chatService.ProcessMessageAsync(request);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error in chat: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpPost("teach")]
    public async Task<IActionResult> Teach([FromBody] TeachRequest request)
    {
        try
        {
            var ok = await _chatService.TeachAsync(request);
            if (!ok) return BadRequest(new { error = "question and answer are required" });
            return Ok(new { status = "ok" });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error in teach: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpGet("health")]
    public IActionResult Health()
    {
        return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
    }
}

