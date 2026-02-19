using Telegram.Bot;
using Telegram.Bot.Requests;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;

namespace Ronaldinho.Bridge;

public class TelegramJob
{
    private readonly ITelegramBotClient _botClient;
    private readonly IExchangeService _exchangeService;
    private readonly ILogger<TelegramJob> _logger;
    private static int _lastUpdateId = 0;

    public TelegramJob(ITelegramBotClient botClient, IExchangeService exchangeService, ILogger<TelegramJob> logger)
    {
        _botClient = botClient;
        _exchangeService = exchangeService;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        _logger.LogInformation("Running Telegram Polling Job at {time}", DateTimeOffset.Now);

        try
        {
            // 1. Poll Telegram for new messages
            var updates = await _botClient.SendRequest(new GetUpdatesRequest 
            { 
                Offset = _lastUpdateId + 1, 
                Limit = 100,
                Timeout = 10 
            });

            foreach (var update in updates)
            {
                _lastUpdateId = update.Id;
                if (update.Message?.Text != null)
                {
                    var userId = update.Message.From!.Id;
                    var text = update.Message.Text;
                    
                    _logger.LogInformation("New message from {userId}: {text}", userId, text);
                    await _exchangeService.WriteToInboxAsync(userId, text);
                }
            }

            // 2. Check Outbox and send responses
            var pendingResponses = await _exchangeService.ReadNewOutboxMessagesAsync();
            foreach (var response in pendingResponses)
            {
                try
                {
                    if (!string.IsNullOrEmpty(response.action))
                    {
                        if (response.action == "typing")
                        {
                            _logger.LogInformation("Sending typing action to {userId}", response.user_id);
                            await _botClient.SendRequest(new SendChatActionRequest 
                            { 
                                ChatId = response.user_id, 
                                Action = ChatAction.Typing 
                            });
                        }
                        // Mark as sent even if it was just an action
                        await _exchangeService.MarkAsSentAsync(response.ts);
                    }
                    
                    if (!string.IsNullOrEmpty(response.text))
                    {
                        _logger.LogInformation("Sending response to {userId}", response.user_id);
                        await _botClient.SendRequest(new SendMessageRequest 
                        { 
                            ChatId = response.user_id, 
                            Text = response.text 
                        });
                        await _exchangeService.MarkAsSentAsync(response.ts);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to send response or action to {userId}", response.user_id);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Telegram Polling Job");
        }
    }
}
