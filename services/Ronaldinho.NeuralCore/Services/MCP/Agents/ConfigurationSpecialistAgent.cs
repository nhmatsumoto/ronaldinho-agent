using Ronaldinho.NeuralCore.Services.MCP.Core;
using Ronaldinho.NeuralCore.Services.Strategies;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.MCP.Agents;

/// <summary>
/// Agent specialized in provider readiness diagnostics (credentials + preference coherence).
/// </summary>
public class ConfigurationSpecialistAgent : IMcpAgent
{
    private readonly IMessageBus _messageBus;
    private readonly IConfiguration _configuration;

    public string Topic => "configops";
    public string Description => "Especialista em configuração operacional e prontidão de providers.";

    public ConfigurationSpecialistAgent(IMessageBus messageBus, IConfiguration configuration)
    {
        _messageBus = messageBus;
        _configuration = configuration;
        _messageBus.Subscribe(Topic, ProcessMessageAsync);
        Console.WriteLine($"[{Topic}] Agent online. Provider readiness diagnostics active.");
    }

    public async Task ProcessMessageAsync(McpMessage message)
    {
        var diagnostics = ProviderConfigurationValidator.GetDiagnostics(_configuration);
        var preferred = _configuration["LLM_PROVIDER"] ?? "gemini";

        var reportLines = diagnostics.Select(kv =>
            $"- {kv.Key}: configured={kv.Value.Configured}, ready={kv.Value.Ready}, note={kv.Value.Notes}");

        string report = "Diagnóstico de Providers\n"
                      + $"Provider Preferido: {preferred}\n"
                      + string.Join("\n", reportLines);

        var toonResponse = ToonSerializer.Serialize("SUCCESS", Topic, report);

        var reply = new McpMessage
        {
            Sender = Topic,
            TargetTopic = message.ReplyTo,
            CorrelationId = message.CorrelationId,
            TaskDescription = "Configuration Diagnostics",
            Payload = toonResponse
        };

        await _messageBus.PublishAsync(reply);
    }
}
