using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class NvidiaStrategy : ILLMStrategy
{
    public string ProviderName => "Nvidia";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        string modelId = configuration["NVIDIA_MODEL_ID"] ?? "meta/llama-3.1-8b-instruct";
        string apiKey = configuration["NVIDIA_API_KEY"] ?? string.Empty;
        string endpoint = configuration["NVIDIA_ENDPOINT"] ?? "https://integrate.api.nvidia.com/v1";

        if (string.IsNullOrWhiteSpace(apiKey) || apiKey == "placeholder")
        {
            Console.WriteLine($"[Strategy] NVIDIA key missing or placeholder. Skipping. (Length: {apiKey?.Length ?? 0})");
            return;
        }

        if (!string.IsNullOrWhiteSpace(apiKey) && apiKey != "placeholder" && apiKey.Length > 8)
        {
            string maskedKey = $"{apiKey[..4]}...{apiKey[^4..]}";
            Console.WriteLine($"[Strategy] Using NVIDIA API Key: {maskedKey} (Length: {apiKey.Length})");
        }
        else
        {
            Console.WriteLine($"[Strategy] WARNING: Gemini API Key invalid or missing (Length: {apiKey?.Length ?? 0})");
        }

        // NVIDIA NIM is OpenAI compatible
        builder.AddOpenAIChatCompletion(
            modelId: modelId,
            apiKey: apiKey,
            endpoint: new Uri(endpoint));

        Console.WriteLine($"[Strategy] Configured NVIDIA NIM ({modelId})");
    }
}
