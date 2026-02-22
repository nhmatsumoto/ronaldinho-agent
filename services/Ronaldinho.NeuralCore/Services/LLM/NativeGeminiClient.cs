using Google.GenAI;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.LLM;

/// <summary>
/// A specialized service wrapping the official Google.GenAI SDK for direct interaction with Gemini models.
/// </summary>
public class NativeGeminiClient
{
    private readonly GenerativeModel _model;
    private readonly string _apiKey;

    public NativeGeminiClient(IConfiguration configuration)
    {
        _apiKey = configuration["GEMINI_API_KEY"] ?? throw new InvalidOperationException("GEMINI_API_KEY not found in configuration.");
        string modelId = configuration["GEMINI_MODEL_ID"] ?? "gemini-2.0-flash";
        
        var client = new GoogleAIClient(_apiKey);
        _model = client.Models.GenerativeModel(modelId);
    }

    /// <summary>
    /// Synchronously or Asynchronously generates content using the native SDK.
    /// This is a demonstration of how to bypass Semantic Kernel abstractions when needed.
    /// </summary>
    public async Task<string> GenerateContentAsync(string prompt)
    {
        try 
        {
            var response = await _model.GenerateContentAsync(prompt);
            return response.Text();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[NativeGeminiClient] Error: {ex.Message}");
            throw;
        }
    }
}
