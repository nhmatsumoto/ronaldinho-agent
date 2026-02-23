using Microsoft.SemanticKernel;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Services;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class OpenRouterStrategy : ILLMStrategy
{
    public string ProviderName => "OpenRouter";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        string apiKey = configuration["OPENROUTER_API_KEY"] ?? "placeholder_key";
        string modelId = configuration["OPENROUTER_MODEL_ID"] ?? "qwen/qwen3-coder:free";

        if (apiKey != "placeholder_key" && apiKey.Length > 8)
        {
            string maskedKey = $"{apiKey[..4]}...{apiKey[^4..]}";
            Console.WriteLine($"[Strategy] Using OpenRouter Key: {maskedKey}");
        }
        else
        {
            Console.WriteLine("[Strategy] WARNING: Using placeholder OpenRouter Key (Check .env/Vault)");
        }

        builder.Services.AddKeyedSingleton<IChatCompletionService>(
            "openrouter",
            (sp, key) => new OpenRouterChatCompletionService(apiKey, modelId));

        Console.WriteLine($"[Strategy] Configured OpenRouter ({modelId})");
    }
}

public class OpenRouterChatCompletionService : IChatCompletionService
{
    private readonly string _apiKey;
    private readonly string _modelId;
    private readonly HttpClient _httpClient;
    private readonly IReadOnlyDictionary<string, object?> _attributes = new Dictionary<string, object?>();

    public IReadOnlyDictionary<string, object?> Attributes => _attributes;

    public OpenRouterChatCompletionService(string apiKey, string modelId)
    {
        _apiKey = apiKey;
        _modelId = modelId;
        _httpClient = new HttpClient();
    }

    public async Task<IReadOnlyList<ChatMessageContent>> GetChatMessageContentsAsync(
        ChatHistory chatHistory,
        PromptExecutionSettings? executionSettings = null,
        Kernel? kernel = null,
        CancellationToken cancellationToken = default)
    {
        var messages = chatHistory.Select(m => new
        {
            role = m.Role == AuthorRole.System ? "system" : m.Role == AuthorRole.User ? "user" : "assistant",
            content = m.Content
        }).ToList();

        var requestBody = new
        {
            model = _modelId,
            messages
        };

        var json = JsonSerializer.Serialize(requestBody);

        var request = new HttpRequestMessage(HttpMethod.Post, "https://openrouter.ai/api/v1/chat/completions");
        request.Headers.Add("Authorization", $"Bearer {_apiKey}");
        request.Headers.Add("HTTP-Referer", "https://github.com/ronaldinho-agent");
        request.Headers.Add("X-Title", "ronaldinho-agent");
        request.Content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.SendAsync(request, cancellationToken);
        var responseString = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"OpenRouter API Error: {response.StatusCode} - {responseString}");
        }

        using var doc = JsonDocument.Parse(responseString);
        var contentText = doc.RootElement.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString();

        return new List<ChatMessageContent>
        {
            new ChatMessageContent(AuthorRole.Assistant, contentText)
        };
    }

    public async IAsyncEnumerable<StreamingChatMessageContent> GetStreamingChatMessageContentsAsync(
        ChatHistory chatHistory,
        PromptExecutionSettings? executionSettings = null,
        Kernel? kernel = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var result = await GetChatMessageContentsAsync(chatHistory, executionSettings, kernel, cancellationToken);
        yield return new StreamingChatMessageContent(AuthorRole.Assistant, result[0].Content);
    }
}
