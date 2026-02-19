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
}
