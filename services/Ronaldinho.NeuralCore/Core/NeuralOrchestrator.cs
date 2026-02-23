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

        var bootstrapStrategies = LLMStrategyFactory.GetFallbackChain(configuration);
        _kernel = bootstrapStrategies.Count > 0
            ? BuildKernel(bootstrapStrategies[0])
            : Kernel.CreateBuilder().Build();
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

    private async Task<string> QuerySpecialistAsync(string topic, string label, string sessionId, string input, int timeoutSeconds = 20)
    {
        if (!_messageBus.HasSubscribers(topic))
        {
            return $"\n\n{label} indisponível no momento (sem agentes online).";
        }

        try
        {
            var replyTopic = "orchestrator_reply_" + sessionId + "_" + topic;
            var mcpMsg = new McpMessage
            {
                Sender = "orchestrator",
                TargetTopic = topic,
                ReplyTo = replyTopic,
                CorrelationId = sessionId,
                TaskDescription = input
            };

            await _messageBus.PublishAsync(mcpMsg);
            var reply = await _messageBus.WaitForReplyAsync(replyTopic, TimeSpan.FromSeconds(timeoutSeconds));

            var toon = ToonSerializer.Deserialize(reply.Payload);
            var data = toon.ContainsKey("Data") ? toon["Data"] : reply.Payload;
            return $"\n\n{label}:\n{data}";
        }
        catch (TimeoutException)
        {
            return $"\n\n{label} não respondeu a tempo.";
        }
        catch (Exception ex)
        {
            return $"\n\n{label} indisponível ({ex.GetType().Name}).";
        }
    }

    public async Task<string> ProcessMessageAsync(Core.Memory.SessionContext context, string input)
    {
        Console.WriteLine($"[NeuralCore] Reasoning for {context.UserId} on {context.PlatformId} (Session: {context.SessionId})");

        string mcpContext = string.Empty;

        if (input.Contains("código", StringComparison.OrdinalIgnoreCase) || input.Contains("refatorar", StringComparison.OrdinalIgnoreCase))
        {
            mcpContext += await QuerySpecialistAsync("coder", "RELATÓRIO DO AGENTE ESPECIALISTA EM CÓDIGO", context.SessionId, input);
        }
        else if (input.Contains("pesquisa", StringComparison.OrdinalIgnoreCase) || input.Contains("logs", StringComparison.OrdinalIgnoreCase))
        {
            mcpContext += await QuerySpecialistAsync("researcher", "RELATÓRIO DO AGENTE PESQUISADOR", context.SessionId, input);
        }

        if (input.Contains("diagnóstico", StringComparison.OrdinalIgnoreCase) || input.Contains("diagnostico", StringComparison.OrdinalIgnoreCase) || input.Contains("provider", StringComparison.OrdinalIgnoreCase))
        {
            mcpContext += await QuerySpecialistAsync("configops", "RELATÓRIO DO AGENTE DE CONFIGURAÇÃO", context.SessionId, input);
        }

        if (input.Contains("segurança", StringComparison.OrdinalIgnoreCase) || input.Contains("vulnerabilidade", StringComparison.OrdinalIgnoreCase) || input.Contains("api key", StringComparison.OrdinalIgnoreCase))
        {
            mcpContext += await QuerySpecialistAsync("security", "RELATÓRIO DE SEGURANÇA", context.SessionId, input);
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
        if (strategies.Count == 0)
        {
            return "⚠️ Nenhum provedor de IA válido está configurado no momento. Configure uma chave válida no ConfigUI e tente novamente.";
        }

        var settings = new PromptExecutionSettings();
        bool autoFallback = _configuration["ENABLE_AUTO_FALLBACK"] == "true";
        bool simultaneousMode = _configuration["ENABLE_SIMULTANEOUS_LLM"] == "true";

        if (simultaneousMode && strategies.Count > 1)
        {
            return await InvokeSimultaneouslyAsync(prompt, strategies, settings);
        }

        foreach (var strategy in strategies)
        {
            try
            {
                Console.WriteLine($"[Resilience] Attempting reasoning with {strategy.ProviderName}...");

                // Reuse kernel if it's the primary one, otherwise build a fresh one with the strategy
                var currentKernel = strategy.ProviderName == strategies[0].ProviderName ? _kernel : BuildKernel(strategy);

                var response = await currentKernel.InvokePromptAsync(prompt, new KernelArguments(settings));
                var result = response.ToString();

                await PostProcessResponseAsync(result, strategy.ProviderName);

                return result;
            }
            catch (Exception ex) when (ex.ToString().Contains("429") || ex.Message.Contains("Too Many Requests") || ex.Message.Contains("quota"))
            {
                if (!autoFallback)
                {
                    Console.WriteLine($"[Resilience] {strategy.ProviderName} rate limited (429) but Auto-Fallback is DISABLED.");
                    throw;
                }

                Console.WriteLine($"[Resilience] {strategy.ProviderName} rate limited (429). Rotating to next provider...");
                continue;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Error] {ex.GetType().Name} in {strategy.ProviderName}: {ex.Message}");
                Console.WriteLine($"[Trace] {ex.StackTrace}");
                if (strategy == strategies.Last()) throw;
            }
        }

        return "🛑 **Ronaldinho está temporariamente fora de combate.** Todos os modelos configurados falharam ou atingiram o limite de taxa. Por favor, aguarde alguns minutos.";
    }

    private async Task<string> InvokeSimultaneouslyAsync(string prompt, List<ILLMStrategy> strategies, PromptExecutionSettings settings)
    {
        Console.WriteLine($"[Resilience] Entering SIMULTANEOUS MODE (Racing {strategies.Count} models) ⚡");

        var tasks = strategies.Select(async strategy =>
        {
            try
            {
                var kernel = strategy.ProviderName == strategies[0].ProviderName ? _kernel : BuildKernel(strategy);
                var response = await kernel.InvokePromptAsync(prompt, new KernelArguments(settings));
                return new { Strategy = strategy, Result = response.ToString(), Success = true };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Resilience] Racing error in {strategy.ProviderName}: {ex.Message}");
                return new { Strategy = strategy, Result = string.Empty, Success = false };
            }
        }).ToList();

        while (tasks.Count > 0)
        {
            var completedTask = await Task.WhenAny(tasks);
            tasks.Remove(completedTask);
            var result = await completedTask;

            if (result.Success)
            {
                Console.WriteLine($"[Resilience] Racing winner: {result.Strategy.ProviderName} 🏆");
                await PostProcessResponseAsync(result.Result, result.Strategy.ProviderName);
                return result.Result;
            }
        }

        return "🛑 **Ronaldinho está temporariamente fora de combate.** Todos os modelos configurados na corrida simultânea falharam.";
    }

    private async Task PostProcessResponseAsync(string result, string providerName)
    {
        try
        {
            if (_memoryDiff is not null)
            {
                var commitId = _memoryDiff.SaveCommit(new { LastResponse = result, Provider = providerName });
                Console.WriteLine($"[NeuralCore] Memory snapshot saved ({providerName}): {commitId}");
            }

            if (_blockchain is not null && result.Contains("FINDING:", StringComparison.OrdinalIgnoreCase))
            {
                var tx = new KnowledgeTransaction
                {
                    Data = result,
                    Author = providerName
                };
                _blockchain.AddBlock(new[] { tx });
                Console.WriteLine($"[NeuralCore] Significant finding recorded to blockchain by {providerName}.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[NeuralCore] Post-processing error: {ex.Message}");
        }
    }
}