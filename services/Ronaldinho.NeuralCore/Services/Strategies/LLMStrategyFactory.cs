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
            "gemini" => new GeminiStrategy(),
            _ => new GeminiStrategy() // Default
        };
    }

    public static List<ILLMStrategy> GetFallbackChain(IConfiguration configuration)
    {
        var chain = new List<ILLMStrategy>();

        // Add all providers that have keys configured
        if (!string.IsNullOrEmpty(configuration["GEMINI_API_KEY"]))
            chain.Add(new GeminiStrategy());

        if (!string.IsNullOrEmpty(configuration["OPENAI_API_KEY"]))
            chain.Add(new OpenAIStrategy());

        if (!string.IsNullOrEmpty(configuration["ANTHROPIC_API_KEY"]))
            chain.Add(new ClaudeStrategy());

        if (!string.IsNullOrEmpty(configuration["NVIDIA_API_KEY"]))
            chain.Add(new NvidiaStrategy());

        // Ensure the preferred one is FIRST if it's in the list
        string preferred = configuration["LLM_PROVIDER"]?.ToLower() ?? "gemini";
        var preferredStrategy = chain.FirstOrDefault(s => s.ProviderName.ToLower() == preferred);

        if (preferredStrategy != null)
        {
            chain.Remove(preferredStrategy);
            chain.Insert(0, preferredStrategy);
        }

        // Default to Gemini if nothing else is available
        if (chain.Count == 0)
            chain.Add(new GeminiStrategy());

        Console.WriteLine($"[Resilience] Final Fallback Chain: {string.Join(" -> ", chain.Select(s => s.ProviderName))}");
        return chain;
    }
}
