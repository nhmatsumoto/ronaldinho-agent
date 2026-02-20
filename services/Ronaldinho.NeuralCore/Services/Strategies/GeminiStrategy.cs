#pragma warning disable SKEXP0070
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel.Connectors.Google;
using Microsoft.Extensions.DependencyInjection;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class GeminiStrategy : ILLMStrategy
{
    public string ProviderName => "Gemini";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        // 1. Resolve Resilience Services
        var services = builder.Services.BuildServiceProvider(); // Temporary provider to get handler
        var handler = services.GetService<Auth.RotationHandler>();
        
        HttpClient httpClient;
        if (handler != null)
        {
             handler.InnerHandler = new HttpClientHandler();
             httpClient = new HttpClient(handler) { Timeout = TimeSpan.FromMinutes(5) };
             Console.WriteLine("[GeminiStrategy] Resilience Layer (RotationHandler) Active 🛡️");
        }
        else
        {
             httpClient = new HttpClient();
             Console.WriteLine("[GeminiStrategy] Warning: RotationHandler not found.");
        }

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

        builder.AddGoogleAIGeminiChatCompletion(
            modelId: modelId,
            apiKey: apiKey,
            apiVersion: GoogleAIVersion.V1_Beta,
            httpClient: httpClient);

        Console.WriteLine($"[Strategy] Configured Gemini ({modelId})");
    }
}
