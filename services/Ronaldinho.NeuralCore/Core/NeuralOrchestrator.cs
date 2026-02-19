// Suppress experimental warnings for Google Connector
#pragma warning disable SKEXP0070

using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration; // Added for IConfiguration
using Ronaldinho.NeuralCore.Services.Strategies; // Added for Strategy
using System.Text.Json;

namespace Ronaldinho.NeuralCore.Core;

public class NeuralOrchestrator
{
    private readonly Kernel _kernel;
    private readonly string _soul;

    // Modified Constructor to accept IConfiguration
    public NeuralOrchestrator(IConfiguration configuration, string soul, string rootPath)
    {
        _soul = soul;
        
        var builder = Kernel.CreateBuilder();
        
        // 1. Select and Configure Strategy
        var strategy = LLMStrategyFactory.Create(configuration);
        strategy.Configure(builder, configuration);

        // 2. Register Native Plugins
        builder.Plugins.AddFromObject(new Skills.FileSkill(rootPath), "file");
        builder.Plugins.AddFromObject(new Skills.ContextSkill(rootPath), "context");
        
        _kernel = builder.Build();

        // 3. Register Evolution Skill (needs kernel reference)
        _kernel.Plugins.AddFromObject(new Skills.RoslynEvolutionSkill(_kernel, rootPath), "evolution");
    }

    public async Task<string> ProcessMessageAsync(long userId, string input)
    {
        Console.WriteLine($"[NeuralCore] Reasoning for {userId}: {input}");

        var promptTemplate = $@"
        {_soul}

        ESTRATÉGIA DE EXECUÇÃO NEURAL:
        1. Use as ferramentas nativas (file, context) para entender o campo.
        2. Se uma tarefa exigir uma lógica complexa nova, use 'evolution:Evolve' para criar um plugin C# e carregá-lo.
        3. Fale com o usuário via chat se apenas conversa for necessária.

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
            return $"💥 Ronaldinho teve uma cãibra no cérebro ({ex.GetType().Name}): {ex.Message}";
        }
    }
}
