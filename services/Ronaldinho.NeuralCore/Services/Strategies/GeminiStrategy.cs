#pragma warning disable SKEXP0070
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel.Connectors.Google;
using Microsoft.Extensions.DependencyInjection;
using Google.GenAI;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class GeminiStrategy : ILLMStrategy
{
    public string ProviderName => "Gemini";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        // 1. Configure Resilience (Standard HttpClient for now)
        // Note: RotationHandler was removed to resolve build errors.
        var httpClient = new HttpClient { Timeout = TimeSpan.FromMinutes(5) };
        Console.WriteLine("[GeminiStrategy] Resilience Layer (Default) Active 🛡️");

        // 2. Fetch Initial Config
        // We pass "ignored" as key because RotationHandler will overwrite it.
        // But SK checks for null, so we pass a placeholder.
        string configModelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-2.0-flash";
        
        // Map "Gemini 3" requests to best available models (2.0 / 1.5 Pro)
        string modelId = configModelId.ToLower() switch
        {
            "gemini-3-pro" => "gemini-1.5-pro",
            "gemini-3-pro-high" => "gemini-1.5-pro",
            "gemini-3-pro-low" => "gemini-1.5-flash", // Assuming "Low" means efficient
            "gemini-3-flash" => "gemini-2.0-flash",
            _ => configModelId
        };

        string apiKey = configuration["GEMINI_API_KEY"] ?? "placeholder"; 
        
        if (apiKey != "placeholder" && apiKey.Length > 8)
        {
            string maskedKey = $"{apiKey[..4]}...{apiKey[^4..]}";
            Console.WriteLine($"[Strategy] Using API Key: {maskedKey}");
        }
        else
        {
            Console.WriteLine("[Strategy] WARNING: Using placeholder API Key (Check .env/Vault)");
        }

        builder.AddGoogleAIGeminiChatCompletion(
            modelId: modelId,
            apiKey: apiKey,
            apiVersion: GoogleAIVersion.V1_Beta,
            httpClient: httpClient);

        // 3. Register Native Client for specialized tasks (Demonstration)
        // This allows other services to resolve the official Google.GenAI client
        builder.Services.AddSingleton(new global::Google.GenAI.Client(vertexAI: false, apiKey: apiKey));
        
        Console.WriteLine($"[Strategy] Configured Gemini ({modelId}) and Native SDK (Finalized) ÔÜ¢");
    }
}
