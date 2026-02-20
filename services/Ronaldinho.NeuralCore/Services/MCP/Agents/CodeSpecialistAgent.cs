using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Ronaldinho.NeuralCore.Services.MCP.Core;

namespace Ronaldinho.NeuralCore.Services.MCP.Agents;

/// <summary>
/// A specialized agent focused solely on code parsing, diffing, and writing via SuperToolbox plugins.
/// </summary>
public class CodeSpecialistAgent : IMcpAgent
{
    private readonly IMessageBus _messageBus;
    private readonly Kernel _kernel;

    public string Topic => "coder";
    
    public string Description => "Especialista em escrever, modificar e validar código fonte C# e regras de arquitetura pesadas.";

    public CodeSpecialistAgent(IMessageBus messageBus, Kernel kernel)
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
        
        // --- TODO: Connect semantic kernel here (FileSystemSkill, CodebaseDiffSkill) ---
        // Simulate heavy coding task using the isolated Kernel brain
        Console.WriteLine($"[{Topic}] Analyzing code intent with dedicated LLM strategy...");
        await Task.Delay(2000); 
        
        var simulatedCodeResult = $"[Diff Gerado pelo Code Agent usando LLM Dedicado] O CodeSpecialistAgent ajustou as linhas relacionadas a '{message.TaskDescription}'. A injeção de dependência foi normalizada de acordo com as diretrizes do C#.";
        
        Console.WriteLine($"[{Topic}] Code adjustments complete. Sending back to {message.ReplyTo} (Corr: {message.CorrelationId}).");

        // Reply back to the original caller
        var reply = new McpMessage
        {
            Sender = Topic,
            TargetTopic = message.ReplyTo, // Send it back to whoever asked (e.g. Orchestrator)
            CorrelationId = message.CorrelationId,
            TaskDescription = "Code Execution Results",
            Payload = simulatedCodeResult
        };

        await _messageBus.PublishAsync(reply);
    }
}

