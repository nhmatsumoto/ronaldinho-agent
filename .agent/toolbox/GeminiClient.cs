using System.Text;
using System.Text.Json;

namespace Ronaldinho.Toolbox;

public class GeminiClient
{
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;
    private const string ApiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent";

    public GeminiClient(string apiKey)
    {
        _apiKey = apiKey;
        _httpClient = new HttpClient();
    }

    public async Task<string> AskGeminiAsync(string prompt)
    {
        if (string.IsNullOrEmpty(_apiKey)) return "API Key não configurada.";

        var requestBody = new
        {
            contents = new[]
            {
                new { parts = new[] { new { text = prompt } } }
            }
        };

        var json = JsonSerializer.Serialize(requestBody);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{ApiUrl}?key={_apiKey}", content);
        
        if (!response.IsSuccessStatusCode)
        {
            return $"Erro Gemini: {response.StatusCode}";
        }

        var responseJson = await response.Content.ReadAsStringAsync();
        // Nota: Simplificando o parse do JSON de resposta para velocidade
        return responseJson; 
    }

    public async Task<string> SuggestRefactoringAsync(string code, string context)
    {
        string prompt = $"Refatore o seguinte código C# para máxima performance no Linux. Retorne apenas o código corrigido.\nContexto: {context}\n\nCódigo:\n{code}";
        return await AskGeminiAsync(prompt);
    }
}
