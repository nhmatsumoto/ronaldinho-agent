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
        
        // 1. Current preferred
        chain.Add(Create(configuration));

        // 2. Add others if keys exist
        if (!string.IsNullOrEmpty(configuration["OPENAI_API_KEY"]) && configuration["LLM_PROVIDER"] != "openai")
            chain.Add(new OpenAIStrategy());
            
        if (!string.IsNullOrEmpty(configuration["ANTHROPIC_API_KEY"]) && configuration["LLM_PROVIDER"] != "claude")
            chain.Add(new ClaudeStrategy());

        if (configuration["LLM_PROVIDER"] != "gemini")
            chain.Add(new GeminiStrategy());

        return chain;
    }
}
