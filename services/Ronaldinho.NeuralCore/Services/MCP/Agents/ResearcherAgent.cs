using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Ronaldinho.NeuralCore.Services.MCP.Core;

namespace Ronaldinho.NeuralCore.Services.MCP.Agents;

/// <summary>
/// A specialized agent responsible for analyzing logs and performing research across the codebase context.
/// </summary>
public class ResearcherAgent : IMcpAgent
{
    private readonly IMessageBus _messageBus;
    private readonly Kernel _kernel;

    public string Topic => "researcher";

    public string Description => "Pesquisador especialista em vasculhar logs e arquivos para encontrar contexto e sumarizar informações difusas.";

    public ResearcherAgent(IMessageBus messageBus, Kernel kernel)
    {
        _messageBus = messageBus;
        _kernel = kernel;
        // Subscribe to our own topic
        _messageBus.Subscribe(Topic, ProcessMessageAsync);
        Console.WriteLine($"[{Topic}] Agent online (Brain: {_kernel.Plugins.Count} plugins) and waiting for assignments.");
    }

    public async Task ProcessMessageAsync(McpMessage message)
    {
        Console.WriteLine($"[{Topic}] Received task: {message.TaskDescription}");

        // --- TODO: Connect semantic kernel plugins here (TextProcessing, LogAnalyzer) ---
        // Simulate deep reasoning/research time using isolated Kernel brain
        Console.WriteLine($"[{Topic}] Synthesizing research data with dedicated LLM strategy...");
        await Task.Delay(1500);

        var simulatedResearchResult = $"[Contexto Extraído pelo Researcher Agent via LLM] O ResearcherAgent finalizou a análise sobre '{message.TaskDescription}'. Não foram encontrados erros críticos nos logs recentes. A pesquisa retornou dados limpos.";
        var toonResponse = ToonSerializer.Serialize("SUCCESS", Topic, simulatedResearchResult);

        Console.WriteLine($"[{Topic}] Research complete. Sending back to {message.ReplyTo} (Corr: {message.CorrelationId}).");

        // Reply back to the original caller
        var reply = new McpMessage
        {
            Sender = Topic,
            TargetTopic = message.ReplyTo, // Send it back to whoever asked (e.g. Orchestrator)
            CorrelationId = message.CorrelationId,
            TaskDescription = "Research Results",
            Payload = toonResponse
        };

        await _messageBus.PublishAsync(reply);
    }
}

