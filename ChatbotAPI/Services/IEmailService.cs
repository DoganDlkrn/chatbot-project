namespace ChatbotAPI.Services;

public interface IEmailService
{
    Task<bool> SendEmailAsync(string to, string subject, string body);
    Task<bool> SendDeploymentFailureNotificationAsync(string errorMessage, string branchName);
}

