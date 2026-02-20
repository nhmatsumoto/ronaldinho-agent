using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class OpenAIStrategy : ILLMStrategy
{
    public string ProviderName => "OpenAI";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        // 1. Resolve Resilience Services
        // OpenAI rotation handler logic is similar but endpoints differ.
        // For now, let's use the default client but check if we need rotation logic later.
        // If we want rotation, we need a RotationHandler that understands OpenAI error codes.
        
        // Let's reuse RotationHandler but note it's currently hardcoded for Gemini query params?
        // Wait, RotationHandler rewrites `?key=`. OpenAI uses `Authorization: Bearer`.
        // So RotationHandler needs update for OpenAI, or we need a new one.
        // For Phase 26 MVP, let's stick to standard client, assuming user has a paid key that doesn't 429 easily.
        // Or implement a simple rotation if multiple keys exist.
        
        string modelId = configuration["OPENAI_MODEL_ID"] ?? "gpt-4o";
        string apiKey = configuration["OPENAI_API_KEY"] ?? "placeholder_key";

        builder.AddOpenAIChatCompletion(
            modelId: modelId,
            apiKey: apiKey);

        Console.WriteLine($"[Strategy] Configured OpenAI ({modelId})");
    }
}
