using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class LLMStrategyFactory
{
    public static ILLMStrategy Create(IConfiguration configuration)
    {
        string provider = configuration["LLM_PROVIDER"]?.ToLower() ?? "gemini";

        return provider switch
        {
            "openai" => new OpenAIStrategy(),
            "claude" => new ClaudeStrategy(),
            "openrouter" => new OpenRouterStrategy(),
            "nvidia" => new NvidiaStrategy(),
            "gemini" => new GeminiStrategy(),
            _ => new GeminiStrategy()
        };
    }

    public static List<ILLMStrategy> GetFallbackChain(IConfiguration configuration)
    {
        var chain = new List<ILLMStrategy>();

        if (ProviderConfigurationValidator.IsValidSecret(configuration["GEMINI_API_KEY"]))
            chain.Add(new GeminiStrategy());

        if (ProviderConfigurationValidator.IsValidSecret(configuration["OPENAI_API_KEY"]))
            chain.Add(new OpenAIStrategy());

        if (ProviderConfigurationValidator.IsValidSecret(configuration["ANTHROPIC_API_KEY"]))
            chain.Add(new ClaudeStrategy());

        if (ProviderConfigurationValidator.IsValidSecret(configuration["NVIDIA_API_KEY"]))
            chain.Add(new NvidiaStrategy());

        if (ProviderConfigurationValidator.IsValidSecret(configuration["OPENROUTER_API_KEY"]))
            chain.Add(new OpenRouterStrategy());

        string preferred = configuration["LLM_PROVIDER"]?.ToLower() ?? "gemini";
        var preferredStrategy = chain.FirstOrDefault(s => s.ProviderName.Equals(preferred, StringComparison.OrdinalIgnoreCase));

        if (preferredStrategy != null)
        {
            chain.Remove(preferredStrategy);
            chain.Insert(0, preferredStrategy);
        }

        Console.WriteLine($"[Resilience] Final Fallback Chain: {(chain.Count == 0 ? "<empty>" : string.Join(" -> ", chain.Select(s => s.ProviderName)))}");
        return chain;
    }
}
