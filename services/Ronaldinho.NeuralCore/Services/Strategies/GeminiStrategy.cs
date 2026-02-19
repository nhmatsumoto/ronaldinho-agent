#pragma warning disable SKEXP0070
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.Google;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class GeminiStrategy : ILLMStrategy
{
    public string ProviderName => "Gemini";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        string apiKey = configuration["GEMINI_API_KEY"] 
            ?? throw new ArgumentNullException("GEMINI_API_KEY not found in configuration");
        
        string modelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-1.5-flash";

        builder.AddGoogleAIGeminiChatCompletion(
            modelId: modelId,
            apiKey: apiKey);

        Console.WriteLine($"[Strategy] Configured Gemini ({modelId})");
    }
}
