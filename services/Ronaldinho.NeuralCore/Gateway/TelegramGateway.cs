using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
using Ronaldinho.NeuralCore.Core;

namespace Ronaldinho.NeuralCore.Gateway;

public class TelegramGateway
{
    private readonly ITelegramBotClient _botClient;
    private readonly NeuralOrchestrator _orchestrator;

    public TelegramGateway(string token, NeuralOrchestrator orchestrator)
    {
        _botClient = new TelegramBotClient(token);
        _orchestrator = orchestrator;
    }

    public async Task StartAsync()
    {
        var me = await _botClient.GetMeAsync();
        Console.WriteLine($"[Gateway] Ronaldinho NeuralCore online as @{me.Username}");

        using var cts = new CancellationTokenSource();

        var receiverOptions = new ReceiverOptions
        {
            AllowedUpdates = Array.Empty<UpdateType>()
        };

        _botClient.StartReceiving(
            updateHandler: HandleUpdateAsync,
            pollingErrorHandler: HandlePollingErrorAsync,
            receiverOptions: receiverOptions,
            cancellationToken: cts.Token
        );

        // Keep running
        await Task.Delay(-1);
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        if (update.Message is not { Text: { } messageText } message)
            return;

        var chatId = message.Chat.Id;
        
        // Indicate typing
        await botClient.SendChatActionAsync(chatId, ChatAction.Typing, cancellationToken: cancellationToken);

        // Process via Neural Core
        var response = await _orchestrator.ProcessMessageAsync(chatId, messageText);

        // Send response
        await botClient.SendTextMessageAsync(
            chatId: chatId,
            text: response,
            cancellationToken: cancellationToken);
    }

    private Task HandlePollingErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
    {
        Console.WriteLine($"[Gateway] Error: {exception.Message}");
        return Task.CompletedTask;
    }
}
