using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.LLM;

/// <summary>
/// Direct Gemini REST client used as a stable fallback when SDK contracts change.
/// </summary>
public class NativeGeminiClient
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;
    private readonly string _modelId;

    public NativeGeminiClient(IConfiguration configuration)
    {
        _apiKey = configuration["GEMINI_API_KEY"] ?? throw new InvalidOperationException("GEMINI_API_KEY not found in configuration.");
        _modelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-2.0-flash";
        _httpClient = new HttpClient { Timeout = TimeSpan.FromMinutes(2) };
    }

    /// <summary>
    /// Generates content using Google's public Gemini REST endpoint.
    /// </summary>
    public async Task<string> GenerateContentAsync(string prompt)
    {
        if (string.IsNullOrWhiteSpace(prompt))
        {
            return string.Empty;
        }

        var endpoint = $"https://generativelanguage.googleapis.com/v1beta/models/{_modelId}:generateContent?key={_apiKey}";

        var payload = new
        {
            contents = new[]
            {
                new
                {
                    parts = new[]
                    {
                        new { text = prompt }
                    }
                }
            }
        };

        using var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
        using var response = await _httpClient.PostAsync(endpoint, content);
        var body = await response.Content.ReadAsStringAsync();

        if (!response.IsSuccessStatusCode)
        {
            throw new InvalidOperationException($"Gemini REST call failed ({(int)response.StatusCode}): {body}");
        }

        using var doc = JsonDocument.Parse(body);

        if (doc.RootElement.TryGetProperty("candidates", out var candidates) &&
            candidates.ValueKind == JsonValueKind.Array &&
            candidates.GetArrayLength() > 0)
        {
            var first = candidates[0];
            if (first.TryGetProperty("content", out var contentNode) &&
                contentNode.TryGetProperty("parts", out var parts) &&
                parts.ValueKind == JsonValueKind.Array &&
                parts.GetArrayLength() > 0 &&
                parts[0].TryGetProperty("text", out var textNode))
            {
                return textNode.GetString() ?? string.Empty;
            }
        }

        return "No content generated.";
    }
}
