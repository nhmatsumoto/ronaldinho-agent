using global::Google.GenAI;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.LLM;

/// <summary>
/// A specialized service wrapping the official Google.GenAI SDK for direct interaction with Gemini models.
/// </summary>
public class NativeGeminiClient
{
    private readonly global::Google.GenAI.Client _client;
    private readonly string _modelId;

    public NativeGeminiClient(IConfiguration configuration)
    {
        string apiKey = configuration["GEMINI_API_KEY"] ?? throw new InvalidOperationException("GEMINI_API_KEY not found in configuration.");
        _modelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-2.0-flash";
        
        // Final verified constructor:
        _client = new global::Google.GenAI.Client(vertexAI: false, apiKey: apiKey);
    }

    /// <summary>
    /// Generates content using the official Google.GenAI SDK.
    /// </summary>
    public async Task<string> GenerateContentAsync(string prompt)
    {
        try 
        {
            var response = await _client.Models.GenerateContentAsync(_modelId, prompt);
            return response.Candidates?[0]?.Content?.Parts?[0]?.Text ?? "No content generated.";
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[NativeGeminiClient] Error: {ex.Message}");
            throw;
        }
    }
}
