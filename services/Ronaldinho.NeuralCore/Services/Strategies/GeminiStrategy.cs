#pragma warning disable SKEXP0070
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel.Connectors.Google;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class GeminiStrategy : ILLMStrategy
{
    public string ProviderName => "Gemini";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        var httpClient = new HttpClient { Timeout = TimeSpan.FromMinutes(5) };
        Console.WriteLine("[GeminiStrategy] Resilience Layer (Default) Active 🛡️");

        string configModelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-2.0-flash";

        string modelId = configModelId.ToLower() switch
        {
            "gemini-3-pro" => "gemini-1.5-pro",
            "gemini-3-pro-high" => "gemini-1.5-pro",
            "gemini-3-pro-low" => "gemini-1.5-flash",
            "gemini-3-flash" => "gemini-2.0-flash",
            _ => configModelId
        };

        string apiKey = ProviderConfigurationValidator.NormalizeSecret(configuration["GEMINI_API_KEY"]);

        if (!ProviderConfigurationValidator.IsValidSecret(apiKey))
        {
            throw new InvalidOperationException(
                "GEMINI_API_KEY ausente, inválida ou placeholder. Configure uma chave válida via .env ou ConfigUI.");
        }

        if (apiKey.Length > 8)
        {
            string maskedKey = $"{apiKey[..4]}...{apiKey[^4..]}";
            Console.WriteLine($"[Strategy] Using API Key: {maskedKey}");
        }

        builder.AddGoogleAIGeminiChatCompletion(
            modelId: modelId,
            apiKey: apiKey,
            apiVersion: GoogleAIVersion.V1_Beta,
            httpClient: httpClient);

        Console.WriteLine($"[Strategy] Configured Gemini ({modelId})");
    }
}
