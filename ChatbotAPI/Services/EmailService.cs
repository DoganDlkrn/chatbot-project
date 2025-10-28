using MailKit.Net.Smtp;
using MimeKit;

namespace ChatbotAPI.Services;

public class EmailService : IEmailService
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<EmailService> _logger;

    public EmailService(IConfiguration configuration, ILogger<EmailService> logger)
    {
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<bool> SendEmailAsync(string to, string subject, string body)
    {
        try
        {
            var smtpHost = _configuration["SMTP:Host"];
            var smtpPort = _configuration.GetValue<int>("SMTP:Port", 587);
            var smtpUsername = _configuration["SMTP:Username"];
            var smtpPassword = _configuration["SMTP:Password"];
            var fromEmail = _configuration["SMTP:FromEmail"] ?? smtpUsername;
            var fromName = _configuration["SMTP:FromName"] ?? "Chatbot System";

            if (string.IsNullOrEmpty(smtpHost) || string.IsNullOrEmpty(smtpUsername))
            {
                _logger.LogWarning("SMTP configuration is missing");
                return false;
            }

            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(fromName, fromEmail));
            message.To.Add(new MailboxAddress("", to));
            message.Subject = subject;

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = body
            };
            message.Body = bodyBuilder.ToMessageBody();

            using (var client = new SmtpClient())
            {
                await client.ConnectAsync(smtpHost, smtpPort, MailKit.Security.SecureSocketOptions.StartTls);
                await client.AuthenticateAsync(smtpUsername, smtpPassword);
                await client.SendAsync(message);
                await client.DisconnectAsync(true);
            }

            _logger.LogInformation($"Email sent successfully to {to}");
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Error sending email: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> SendDeploymentFailureNotificationAsync(string errorMessage, string branchName)
    {
        var notificationEmail = _configuration["SMTP:NotificationEmail"];
        if (string.IsNullOrEmpty(notificationEmail))
        {
            _logger.LogWarning("Notification email is not configured");
            return false;
        }

        var subject = $"🚨 Deployment Failed - Chatbot System ({branchName})";
        var body = $@"
            <html>
            <body style='font-family: Arial, sans-serif;'>
                <h2 style='color: #d32f2f;'>Deployment Failed</h2>
                <p><strong>Branch:</strong> {branchName}</p>
                <p><strong>Time:</strong> {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC</p>
                <hr/>
                <h3>Error Details:</h3>
                <pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px;'>{errorMessage}</pre>
                <hr/>
                <p>Please check the Jenkins logs for more details.</p>
                <p style='color: #666; font-size: 12px;'>This is an automated notification from the Chatbot CI/CD pipeline.</p>
            </body>
            </html>
        ";

        return await SendEmailAsync(notificationEmail, subject, body);
    }
}

