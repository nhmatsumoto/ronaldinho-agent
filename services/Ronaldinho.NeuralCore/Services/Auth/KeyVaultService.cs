using Microsoft.Extensions.Configuration;
using System.Collections.Concurrent;

namespace Ronaldinho.NeuralCore.Services.Auth;

public class KeyVaultService
{
    private readonly IConfiguration _configuration;
    private readonly ConcurrentDictionary<string, List<string>> _providerKeys = new();

    public KeyVaultService(IConfiguration configuration)
    {
        _configuration = configuration;
        InitializeKeys();
    }

    private void InitializeKeys()
    {
        // Load Gemini Keys
        var geminiKeys = new List<string>();
        
        // 1. Legacy single key
        var singleKey = _configuration["GEMINI_API_KEY"];
        if (!string.IsNullOrEmpty(singleKey))
        {
            geminiKeys.Add(singleKey);
        }

        // 2. Multi-key env var (comma separated)
        var multiKeyString = _configuration["GEMINI_KEYS"];
        if (!string.IsNullOrEmpty(multiKeyString))
        {
            var keys = multiKeyString.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            foreach (var k in keys)
            {
                if (!geminiKeys.Contains(k))
                {
                    geminiKeys.Add(k);
                }
            }
        }

        if (geminiKeys.Any())
        {
            _providerKeys["Gemini"] = geminiKeys;
            Console.WriteLine($"[KeyVault] Loaded {geminiKeys.Count} keys for Gemini.");
        }

        // Load OpenAI Keys
        var openaiKeys = new List<string>();
        
        var singleOpenAI = _configuration["OPENAI_API_KEY"];
        if (!string.IsNullOrEmpty(singleOpenAI)) openaiKeys.Add(singleOpenAI);

        var multiOpenAI = _configuration["OPENAI_KEYS"];
        if (!string.IsNullOrEmpty(multiOpenAI))
        {
            var keys = multiOpenAI.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            foreach (var k in keys) if (!openaiKeys.Contains(k)) openaiKeys.Add(k);
        }

        if (openaiKeys.Any())
        {
            _providerKeys["OpenAI"] = openaiKeys;
            Console.WriteLine($"[KeyVault] Loaded {openaiKeys.Count} keys for OpenAI.");
        }
    }

    public List<string> GetKeys(string provider)
    {
        return _providerKeys.TryGetValue(provider, out var keys) ? keys : new List<string>();
    }
}
