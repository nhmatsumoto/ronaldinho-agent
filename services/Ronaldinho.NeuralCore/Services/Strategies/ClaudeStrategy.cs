using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Services;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public class ClaudeStrategy : ILLMStrategy
{
    public string ProviderName => "Claude";

    public void Configure(IKernelBuilder builder, IConfiguration configuration)
    {
        string apiKey = configuration["ANTHROPIC_API_KEY"] 
            ?? throw new ArgumentNullException("ANTHROPIC_API_KEY not found in configuration");
            
        string modelId = configuration["CLAUDE_MODEL_ID"] ?? "claude-3-5-sonnet-20240620";

        // Register Custom Claude Service
        builder.Services.AddKeyedSingleton<IChatCompletionService>(
            "claude", 
            (sp, key) => new ClaudeChatCompletionService(apiKey, modelId));

        Console.WriteLine($"[Strategy] Configured Claude ({modelId}) - Custom Service");
    }
}

// --- Minimal Anthropic Chat Service Implementation ---

public class ClaudeChatCompletionService : IChatCompletionService
{
    private readonly string _apiKey;
    private readonly string _modelId;
    private readonly HttpClient _httpClient;
    private readonly IReadOnlyDictionary<string, object?> _attributes = new Dictionary<string, object?>();

    public IReadOnlyDictionary<string, object?> Attributes => _attributes;

    public ClaudeChatCompletionService(string apiKey, string modelId)
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
        // 1. Prepare Request
        var requestBody = new
        {
            model = _modelId,
            max_tokens = 4096,
            messages = chatHistory.Where(m => m.Role != AuthorRole.System).Select(m => new 
            {
                role = m.Role == AuthorRole.User ? "user" : "assistant",
                content = m.Content
            }).ToList(),
            system = chatHistory.FirstOrDefault(m => m.Role == AuthorRole.System)?.Content 
        };

        var json = JsonSerializer.Serialize(requestBody);
        var request = new HttpRequestMessage(HttpMethod.Post, "https://api.anthropic.com/v1/messages");
        request.Headers.Add("x-api-key", _apiKey);
        request.Headers.Add("anthropic-version", "2023-06-01");
        request.Content = new StringContent(json, Encoding.UTF8, "application/json");

        // 2. Send
        var response = await _httpClient.SendAsync(request, cancellationToken);
        var responseString = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"Claude API Error: {response.StatusCode} - {responseString}");
        }

        // 3. Parse
        using var doc = JsonDocument.Parse(responseString);
        var contentText = doc.RootElement.GetProperty("content")[0].GetProperty("text").GetString();

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
        // Simple non-streaming fallback for now
        var result = await GetChatMessageContentsAsync(chatHistory, executionSettings, kernel, cancellationToken);
        yield return new StreamingChatMessageContent(AuthorRole.Assistant, result[0].Content);
    }
}
