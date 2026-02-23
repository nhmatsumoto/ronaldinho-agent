using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Ronaldinho.NeuralCore.Services.Strategies;
using System.ComponentModel;

namespace Ronaldinho.NeuralCore.Services.Skills;

public class ResilienceSkill
{
    private readonly IConfiguration _configuration;
    private readonly Kernel _kernel;

    public ResilienceSkill(Kernel kernel, IConfiguration configuration)
    {
        _kernel = kernel;
        _configuration = configuration;
    }

    [KernelFunction, Description("Invoca um prompt usando a cadeia de fallback configurada para máxima resiliência.")]
    public async Task<string> InvokeWithResilienceAsync(
        [Description("O prompt a ser enviado para o modelo")] string prompt)
    {
        var strategies = LLMStrategyFactory.GetFallbackChain(_configuration);
        bool simultaneousMode = _configuration["ENABLE_SIMULTANEOUS_LLM"] == "true";

        if (simultaneousMode && strategies.Count > 1)
        {
            return await InvokeSimultaneouslyAsync(prompt, strategies);
        }

        foreach (var strategy in strategies)
        {
            try
            {
                // Note: In a real implementation, we'd need to switch the kernel's completion service
                // For this skill, we'll assume the kernel passed already has the primary strategy.
                // If it fails, we recursively or iteratively try others.
                var result = await _kernel.InvokePromptAsync(prompt);
                return result.ToString();
            }
            catch (Exception ex) when (ex.Message.Contains("429") || ex.Message.Contains("quota"))
            {
                Console.WriteLine($"[ResilienceSkill] {strategy.ProviderName} failed, rotating...");
                continue;
            }
        }

        return "Falha total na resiliência neural.";
    }

    private async Task<string> InvokeSimultaneouslyAsync(string prompt, List<ILLMStrategy> strategies)
    {
        var tasks = strategies.Select(async s =>
        {
            try { return await _kernel.InvokePromptAsync(prompt); }
            catch { return null; }
        });

        var completed = await Task.WhenAny(tasks);
        var result = await completed;
        return result?.ToString() ?? "Falha na corrida simultânea.";
    }
}
