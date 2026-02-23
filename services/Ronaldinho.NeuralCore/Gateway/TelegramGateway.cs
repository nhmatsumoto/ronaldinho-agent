using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
using System.Threading;
using System.Threading.Tasks;
using Ronaldinho.NeuralCore.Core;
using Ronaldinho.Contracts;

namespace Ronaldinho.NeuralCore.Gateway;

public class TelegramGateway : IGateway
{
    private readonly ITelegramBotClient _botClient;
    private readonly NeuralOrchestrator _orchestrator;
    private CancellationTokenSource? _cts;

    public string Name => "Telegram";

    public TelegramGateway(string token, NeuralOrchestrator orchestrator)
    {
        _botClient = new TelegramBotClient(token);
        _orchestrator = orchestrator;
    }

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        _cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);

        var me = await _botClient.GetMeAsync(_cts.Token);
        Console.WriteLine($"[Gateway] Ronaldinho NeuralCore online as @{me.Username}");

        var receiverOptions = new ReceiverOptions
        {
            AllowedUpdates = Array.Empty<UpdateType>()
        };

        _botClient.StartReceiving(
            updateHandler: HandleUpdateAsync,
            pollingErrorHandler: HandlePollingErrorAsync,
            receiverOptions: receiverOptions,
            cancellationToken: _cts.Token
        );
    }

    public Task StopAsync(CancellationToken cancellationToken = default)
    {
        _cts?.Cancel();
        Console.WriteLine($"[Gateway] Stopped listening for Telegram.");
        return Task.CompletedTask;
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        try
        {
            if (update.Message is not { Text: { } messageText } message)
                return;

            var chatId = message.Chat.Id;

            // Indicate typing
            await botClient.SendChatActionAsync(chatId, ChatAction.Typing, cancellationToken: cancellationToken);

            // Process via Neural Core (Injecting Context & Memory)
            var context = _orchestrator.Router.Route("Telegram", chatId.ToString(), message.From?.Id.ToString() ?? "Unknown");

            // 1. Save user's fresh input to memory
            await _orchestrator.Memory.SaveMemoryAsync(context.SessionId, "user", messageText);

            // 2. Process via AI
            var response = await _orchestrator.ProcessMessageAsync(context, messageText);

            // 3. Save AI's response to memory
            await _orchestrator.Memory.SaveMemoryAsync(context.SessionId, "assistant", response);

            // Send response
            await botClient.SendTextMessageAsync(
                chatId: chatId,
                text: response,
                cancellationToken: cancellationToken);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Gateway] Unhandled Exception: {ex.Message}");
            if (update.Message != null)
            {
                try
                {
                    await botClient.SendTextMessageAsync(
                        chatId: update.Message.Chat.Id,
                        text: $"🚨 Falha de operação na infraestrutura HTTP (Google API / Modelos?): {ex.Message}",
                        cancellationToken: cancellationToken);
                }
                catch { /* Ignore inner send errors */ }
            }
        }
    }

    private Task HandlePollingErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
    {
        Console.WriteLine($"[Gateway] Error: {exception.Message}");
        return Task.CompletedTask;
    }
}
