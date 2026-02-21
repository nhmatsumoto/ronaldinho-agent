// Suppress experimental warnings for Google Connector
#pragma warning disable SKEXP0070

using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration; // Added for IConfiguration
using Microsoft.Extensions.DependencyInjection; // Added for AddSingleton/AddTransient
using Ronaldinho.NeuralCore.Services.Strategies; // Added for Strategy
using Ronaldinho.NeuralCore.Services.Skills; // Added for SkillLoader, FindingsSkill
using Ronaldinho.NeuralCore.Services.MCP.Core; // Added for MCP Protocol
using System.Text.Json;

namespace Ronaldinho.NeuralCore.Core;

public class NeuralOrchestrator
{
    private readonly Kernel _kernel;
    private readonly string _soul;
    private readonly IMessageBus _messageBus; // New MCP Bus

    public Core.Memory.SessionRouter Router { get; }
    public Core.Memory.MemoryStore Memory { get; }

    // Modified Constructor to accept Plugins, Router, Memory, and the MCP Bus
    public NeuralOrchestrator(
        IConfiguration configuration, 
        string soul, 
        string rootPath, 
        Services.SuperToolbox.FileSystemSkill fileSystemSkill,
        Services.SuperToolbox.TextProcessingSkill textProcessingSkill,
        Services.SuperToolbox.LogAnalyzerSkill logAnalyzerSkill,
        Services.SuperToolbox.CodebaseDiffSkill codebaseDiffSkill,
        Core.Memory.SessionRouter router,
        Core.Memory.MemoryStore memory,
        IMessageBus messageBus) // Injected Bus
    {
        _soul = soul;
        Router = router;
        Memory = memory;
        _messageBus = messageBus;
        
        var builder = Kernel.CreateBuilder();
        
        // 1. Register Resilience Services
        builder.Services.AddSingleton(configuration); // configuration is needed by KeyVaultService
        builder.Services.AddSingleton<Ronaldinho.NeuralCore.Services.LocalKeyVault>();

        // 2. Select and Configure Strategy
        var strategy = LLMStrategyFactory.Create(configuration);
        strategy.Configure(builder, configuration);

        // 2. Register Native Plugins
        // Core skills always loaded
        builder.Plugins.AddFromObject(new FindingsSkill(rootPath), "findings");
        
        // SuperToolbox Skills
        builder.Plugins.AddFromObject(fileSystemSkill, "SuperToolbox_Files");
        builder.Plugins.AddFromObject(textProcessingSkill, "SuperToolbox_Text");
        builder.Plugins.AddFromObject(logAnalyzerSkill, "SuperToolbox_Logs");
        builder.Plugins.AddFromObject(codebaseDiffSkill, "SuperToolbox_Diffs");

        _kernel = builder.Build();

        // 3. Dynamic Skill Loading (Antigravity Ecosystem)
        var skillLoader = new SkillLoader(_kernel, rootPath);
        skillLoader.LoadSkills();

        // 4. Register Evolution Skill (needs kernel reference)
        _kernel.Plugins.AddFromObject(new Skills.RoslynEvolutionSkill(_kernel, rootPath), "evolution");
    }

    public async Task<string> ProcessMessageAsync(Core.Memory.SessionContext context, string input)
    {
        Console.WriteLine($"[NeuralCore] Reasoning for {context.UserId} on {context.PlatformId} (Session: {context.SessionId})");

        string mcpContext = string.Empty;

        // MULTI-AGENT PROTOCOL (MCP) INTERCEPTION
        // Heuristic: If the user asks something related to "código", "refatorar", or "diff", delegate to CodeSpecialistAgent
        if (input.Contains("código", StringComparison.OrdinalIgnoreCase) || input.Contains("refatorar", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine("[NeuralCore] Delegating to CodeSpecialistAgent via MCP...");
            var mcpMsg = new McpMessage 
            {
                Sender = "orchestrator",
                TargetTopic = "coder",
                ReplyTo = "orchestrator_reply_" + context.SessionId,
                CorrelationId = context.SessionId,
                TaskDescription = input
            };
            
            await _messageBus.PublishAsync(mcpMsg);
            
            // Wait for the agent to finish its execution and reply
            var reply = await _messageBus.WaitForReplyAsync(mcpMsg.ReplyTo, TimeSpan.FromSeconds(30));
            mcpContext = $"\n\nRELATÓRIO DO AGENTE ESPECIALISTA EM CÓDIGO:\n{reply.Payload}";
        }
        // Heuristic: If the user asks something related to "pesquisa", "logs", or "procurar", delegate to ResearcherAgent
        else if (input.Contains("pesquisa", StringComparison.OrdinalIgnoreCase) || input.Contains("logs", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine("[NeuralCore] Delegating to ResearcherAgent via MCP...");
            var mcpMsg = new McpMessage 
            {
                Sender = "orchestrator",
                TargetTopic = "researcher",
                ReplyTo = "orchestrator_reply_" + context.SessionId,
                CorrelationId = context.SessionId,
                TaskDescription = input
            };
            
            await _messageBus.PublishAsync(mcpMsg);
            
            // Wait for the agent to finish its execution and reply
            var reply = await _messageBus.WaitForReplyAsync(mcpMsg.ReplyTo, TimeSpan.FromSeconds(30));
            mcpContext = $"\n\nRELATÓRIO DO AGENTE PESQUISADOR:\n{reply.Payload}";
        }

        // 1. Retrieve Decayed Memory Context
        var history = await Memory.RetrieveRelevantContextAsync(context.SessionId);
        var memoryBlock = string.Join("\n", history.Select(h => $"{h.Role.ToUpper()}: {h.Content}"));

        var promptTemplate = $@"
        {_soul}

        ESTRATÉGIA DE EXECUÇÃO NEURAL:
        1. Use as ferramentas nativas (file, context) para entender o campo.
        2. Considere seriamente os relatórios dos Agentes Especialistas (MCP) fornecidos abaixo, se houver.
        3. Fale com o usuário via chat consolidando as informações.

        MEMÓRIA RECENTE (Temporal Decay):
        {memoryBlock}

        {mcpContext}

        CONDIÇÃO ATUAL:
        O usuário enviou: {input}
        ";

        try 
        {
            // Simplified settings 
            var settings = new PromptExecutionSettings(); 
            
            var response = await _kernel.InvokePromptAsync(promptTemplate, new KernelArguments(settings));
            return response.ToString();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Error] {ex}");
            // Handle specific strategy errors if needed
            return $"💥 Ronaldinho teve uma falha de coordenação multi-agente ({ex.GetType().Name}): {ex.Message}";
        }
    }
}

