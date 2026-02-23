using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
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
        Console.WriteLine("[Gateway] Stopped listening for Telegram.");
        return Task.CompletedTask;
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        try
        {
            if (update.Message is not { Text: { } messageText } message)
                return;

            var chatId = message.Chat.Id;

            await botClient.SendChatActionAsync(chatId, ChatAction.Typing, cancellationToken: cancellationToken);

            var context = _orchestrator.Router.Route("Telegram", chatId.ToString(), message.From?.Id.ToString() ?? "Unknown");

            await _orchestrator.Memory.SaveMemoryAsync(context.SessionId, "user", messageText);

            var response = await _orchestrator.ProcessMessageAsync(context, messageText);

            await _orchestrator.Memory.SaveMemoryAsync(context.SessionId, "assistant", response);

            await botClient.SendTextMessageAsync(
                chatId: chatId,
                text: response,
                cancellationToken: cancellationToken);
        }
        catch (Exception ex)
        {
            var correlationId = Guid.NewGuid().ToString("N")[..8];
            Console.WriteLine($"[Gateway] Error [{correlationId}] {ex.GetType().Name}: {ex.Message}");
            Console.WriteLine($"[Gateway] Trace [{correlationId}] {ex.StackTrace}");

            if (update.Message != null)
            {
                try
                {
                    await botClient.SendTextMessageAsync(
                        chatId: update.Message.Chat.Id,
                        text: BuildUserMessage(ex, correlationId),
                        cancellationToken: cancellationToken);
                }
                catch
                {
                    // ignore inner send errors
                }
            }
        }
    }

    private static string BuildUserMessage(Exception ex, string correlationId)
    {
        var message = ex.Message.ToLowerInvariant();

        if (message.Contains("apikey") || message.Contains("api key") || message.Contains("invalidoperationexception"))
        {
            return $"⚠️ O agente está com configuração de provedor inválida no momento. Tente novamente em instantes. Código: {correlationId}";
        }

        if (message.Contains("429") || message.Contains("too many requests") || message.Contains("quota"))
        {
            return $"⚠️ O serviço de IA atingiu limite temporário. Tente novamente em alguns segundos. Código: {correlationId}";
        }

        return $"🚨 Ocorreu uma falha temporária no processamento. Tente novamente. Código: {correlationId}";
    }

    private Task HandlePollingErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
    {
        Console.WriteLine($"[Gateway] Polling error: {exception.Message}");
        return Task.CompletedTask;
    }
}
