using System.Text.Json;
using System.Security.Cryptography;
using System.Text;

using System.Runtime.Versioning;

namespace Ronaldinho.NeuralCore.Services.Auth;

/// <summary>
/// Handles secure storage of user credentials using Windows DPAPI.
/// </summary>
[SupportedOSPlatform("windows")]
public class TokenStorageService
{
    private readonly string _storagePath;

    public TokenStorageService(string rootPath)
    {
        _storagePath = Path.Combine(rootPath, "ronaldinho", "data", "secure_tokens");
        if (!Directory.Exists(_storagePath))
        {
            Directory.CreateDirectory(_storagePath);
        }
    }

    public void SaveToken(string providerName, string tokenJson)
    {
        try
        {
            byte[] rawBytes = Encoding.UTF8.GetBytes(tokenJson);
            
            // Protect data - can only be decrypted by the current user on this machine
            byte[] encryptedBytes = ProtectedData.Protect(
                rawBytes, 
                null, 
                DataProtectionScope.CurrentUser);

            string safePath = Path.Combine(_storagePath, $"{providerName}.dat");
            File.WriteAllBytes(safePath, encryptedBytes);

            Console.WriteLine($"[Secure] Token for {providerName} saved securely.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Secure] Failed to save token: {ex.Message}");
        }
    }

    public string? LoadToken(string providerName)
    {
        try
        {
            string safePath = Path.Combine(_storagePath, $"{providerName}.dat");
            if (!File.Exists(safePath)) return null;

            byte[] encryptedBytes = File.ReadAllBytes(safePath);

            // Unprotect data
            byte[] decryptedBytes = ProtectedData.Unprotect(
                encryptedBytes, 
                null, 
                DataProtectionScope.CurrentUser);

            return Encoding.UTF8.GetString(decryptedBytes);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Secure] Failed to decrypt token (maybe wrong user context?): {ex.Message}");
            return null;
        }
    }
}
