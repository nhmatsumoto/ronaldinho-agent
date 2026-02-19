using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class OpenAIStrategy : ILLMStrategy
{
    public string ProviderName => "OpenAI";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        string apiKey = configuration["OPENAI_API_KEY"] 
            ?? throw new ArgumentNullException("OPENAI_API_KEY not found in configuration");

        string modelId = configuration["OPENAI_MODEL_ID"] ?? "gpt-4o";

        builder.AddOpenAIChatCompletion(
            modelId: modelId,
            apiKey: apiKey);

        Console.WriteLine($"[Strategy] Configured OpenAI ({modelId})");
    }
}
