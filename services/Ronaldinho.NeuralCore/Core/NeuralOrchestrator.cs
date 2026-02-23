// Suppress experimental warnings for Google Connector
#pragma warning disable SKEXP0070

using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration; // Added for IConfiguration
using Microsoft.Extensions.DependencyInjection; // Added for AddSingleton/AddTransient
using Ronaldinho.NeuralCore.Services.Strategies; // Added for Strategy
using Ronaldinho.NeuralCore.Services.Skills; // Added for SkillLoader, FindingsSkill
using Ronaldinho.NeuralCore.Services.MCP.Core; // Added for MCP Protocol
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Ronaldinho.Contracts;
using Ronaldinho.Blockchain;

namespace Ronaldinho.NeuralCore.Core;

public class NeuralOrchestrator : IMessageProcessor
{
    private readonly IConfiguration _configuration;
    private readonly string _rootPath;
    private readonly Services.SuperToolbox.FileSystemSkill _fileSystemSkill;
    private readonly Services.SuperToolbox.TextProcessingSkill _textProcessingSkill;
    private readonly Services.SuperToolbox.LogAnalyzerSkill _logAnalyzerSkill;
    private readonly Services.SuperToolbox.CodebaseDiffSkill _codebaseDiffSkill;
    private readonly Kernel _kernel;
    private readonly string _soul;
    private readonly IMessageBus _messageBus;
    private readonly Ronaldinho.MemoryDiff.MemoryDiffService? _memoryDiff;
    private readonly Chain? _blockchain;

    public Core.Memory.SessionRouter Router { get; }
    public Core.Memory.MemoryStore Memory { get; }

    public NeuralOrchestrator(
        IConfiguration configuration,
        string soul,
        string rootPath,
        Services.SuperToolbox.FileSystemSkill fileSystemSkill,
        Services.SuperToolbox.TextProcessingSkill textProcessingSkill,
        Services.SuperToolbox.LogAnalyzerSkill logAnalyzerSkill,
        Services.SuperToolbox.CodebaseDiffSkill codebaseDiffSkill,
        Memory.SessionRouter router,
        Memory.MemoryStore memory,
        IMessageBus messageBus,
        Ronaldinho.MemoryDiff.MemoryDiffService? memoryDiff = null,
        Chain? blockchain = null)
    {
        _configuration = configuration;
        _soul = soul;
        _rootPath = rootPath;
        _fileSystemSkill = fileSystemSkill;
        _textProcessingSkill = textProcessingSkill;
        _logAnalyzerSkill = logAnalyzerSkill;
        _codebaseDiffSkill = codebaseDiffSkill;
        Router = router;
        Memory = memory;
        _messageBus = messageBus;
        _memoryDiff = memoryDiff;
        _blockchain = blockchain;

        _kernel = BuildKernel(LLMStrategyFactory.Create(configuration));
    }

    private Kernel BuildKernel(ILLMStrategy strategy)
    {
        var builder = Kernel.CreateBuilder();
        builder.Services.AddSingleton(_configuration);
        builder.Services.AddSingleton<Ronaldinho.NeuralCore.Services.LocalKeyVault>();

        strategy.Configure(builder, _configuration);

        builder.Plugins.AddFromObject(new FindingsSkill(_rootPath), "findings");
        builder.Plugins.AddFromObject(_fileSystemSkill, "SuperToolbox_Files");
        builder.Plugins.AddFromObject(_textProcessingSkill, "SuperToolbox_Text");
        builder.Plugins.AddFromObject(_logAnalyzerSkill, "SuperToolbox_Logs");
        builder.Plugins.AddFromObject(_codebaseDiffSkill, "SuperToolbox_Diffs");

        var kernel = builder.Build();
        new SkillLoader(kernel, _rootPath).LoadSkills();
        kernel.Plugins.AddFromObject(new Skills.RoslynEvolutionSkill(kernel, _rootPath), "evolution");

        return kernel;
    }

    public async Task<string> ProcessAsync(string platform, string channelId, string userId, string input)
    {
        var context = Router.Route(platform, channelId, userId);
        return await ProcessMessageAsync(context, input);
    }

    public async Task<string> ProcessMessageAsync(Core.Memory.SessionContext context, string input)
    {
        Console.WriteLine($"[NeuralCore] Reasoning for {context.UserId} on {context.PlatformId} (Session: {context.SessionId})");

        string mcpContext = string.Empty;

        if (input.Contains("código", StringComparison.OrdinalIgnoreCase) || input.Contains("refatorar", StringComparison.OrdinalIgnoreCase))
        {
            var mcpMsg = new McpMessage { Sender = "orchestrator", TargetTopic = "coder", ReplyTo = "orchestrator_reply_" + context.SessionId, CorrelationId = context.SessionId, TaskDescription = input };
            await _messageBus.PublishAsync(mcpMsg);
            var reply = await _messageBus.WaitForReplyAsync(mcpMsg.ReplyTo, TimeSpan.FromSeconds(30));
            mcpContext = $"\n\nRELATÓRIO DO AGENTE ESPECIALISTA EM CÓDIGO:\n{reply.Payload}";
        }
        else if (input.Contains("pesquisa", StringComparison.OrdinalIgnoreCase) || input.Contains("logs", StringComparison.OrdinalIgnoreCase))
        {
            var mcpMsg = new McpMessage { Sender = "orchestrator", TargetTopic = "researcher", ReplyTo = "orchestrator_reply_" + context.SessionId, CorrelationId = context.SessionId, TaskDescription = input };
            await _messageBus.PublishAsync(mcpMsg);
            var reply = await _messageBus.WaitForReplyAsync(mcpMsg.ReplyTo, TimeSpan.FromSeconds(30));
            mcpContext = $"\n\nRELATÓRIO DO AGENTE PESQUISADOR:\n{reply.Payload}";
        }

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

        return await InvokeWithFallbackAsync(promptTemplate);
    }

    private async Task<string> InvokeWithFallbackAsync(string prompt)
    {
        var strategies = LLMStrategyFactory.GetFallbackChain(_configuration);
        var settings = new PromptExecutionSettings();
        bool autoFallback = _configuration["ENABLE_AUTO_FALLBACK"] == "true";

        foreach (var strategy in strategies)
        {
            try
            {
                Console.WriteLine($"[Resilience] Attempting reasoning with {strategy.ProviderName}...");
                var currentKernel = strategy.ProviderName == strategies[0].ProviderName ? _kernel : BuildKernel(strategy);

                var response = await currentKernel.InvokePromptAsync(prompt, new KernelArguments(settings));
                var result = response.ToString();

                // Post-processing: Memory Snapshotting & Blockchain Ledger
                try
                {
                    if (_memoryDiff is not null)
                    {
                        var commitId = _memoryDiff.SaveCommit(new { LastResponse = result });
                        Console.WriteLine($"[NeuralCore] Memory snapshot saved: {commitId}");
                    }

                    if (_blockchain is not null && result.Contains("FINDING:", StringComparison.OrdinalIgnoreCase))
                    {
                        var tx = new KnowledgeTransaction
                        {
                            Data = result,
                            Author = strategy.ProviderName
                        };
                        _blockchain.AddBlock(new[] { tx });
                        Console.WriteLine("[NeuralCore] Significant finding recorded to blockchain.");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[NeuralCore] Post-processing error: {ex.Message}");
                }

                return result;
            }
            catch (Exception ex) when (ex.ToString().Contains("429") || ex.Message.Contains("Too Many Requests"))
            {
                if (!autoFallback)
                {
                    Console.WriteLine("[Resilience] 429 detected but Auto-Fallback is DISABLED.");
                    throw;
                }

                Console.WriteLine($"[Resilience] {strategy.ProviderName} rate limited (429). Rotating to next provider...");
                continue;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Error] {ex.GetType().Name} in {strategy.ProviderName}: {ex.Message}");
                if (strategy == strategies.Last()) throw;
            }
        }

        return "🛑 **Ronaldinho está temporariamente fora de combate.** Todos os modelos configurados atingiram o limite de taxa. Por favor, aguarde alguns minutos.";
    }
}