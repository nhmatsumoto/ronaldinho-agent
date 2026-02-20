using Microsoft.AspNetCore.DataProtection;
using System.Text.Json;

namespace Ronaldinho.NeuralCore.Services;

public class LocalKeyVault : ILocalKeyVault
{
    private readonly IDataProtector _protector;
    private readonly string _vaultPath = "brain/Security/vault.json";

    public LocalKeyVault(IDataProtectionProvider provider)
    {
        _protector = provider.CreateProtector("Ronaldinho.NeuralCore.LocalKeyVault");
        Directory.CreateDirectory(Path.GetDirectoryName(_vaultPath)!);
    }

    public void SaveKey(string userId, string provider, string apiKey)
    {
        var data = LoadVault();
        if (!data.ContainsKey(userId)) data[userId] = new Dictionary<string, string>();
        
        string encryptedKey = _protector.Protect(apiKey);
        data[userId][provider] = encryptedKey;

        SaveVault(data);
    }

    public string? GetKey(string userId, string provider)
    {
        var data = LoadVault();
        if (data.TryGetValue(userId, out var userKeys) && userKeys.TryGetValue(provider, out var encryptedKey))
        {
            try
            {
                return _protector.Unprotect(encryptedKey);
            }
            catch
            {
                return null; // Decryption failed
            }
        }
        return null;
    }

    public string? GetGlobalKey(string provider)
    {
        var data = LoadVault();
        foreach (var userKeys in data.Values)
        {
            if (userKeys.TryGetValue(provider, out var encryptedKey))
            {
                try
                {
                    return _protector.Unprotect(encryptedKey);
                }
                catch { }
            }
        }
        return null; // Fallback missing
    }

    private Dictionary<string, Dictionary<string, string>> LoadVault()
    {
        if (!File.Exists(_vaultPath)) return new Dictionary<string, Dictionary<string, string>>();
        var json = File.ReadAllText(_vaultPath);
        return JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, string>>>(json) ?? new();
    }

    private void SaveVault(Dictionary<string, Dictionary<string, string>> data)
    {
        var json = JsonSerializer.Serialize(data, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(_vaultPath, json);
    }
}
