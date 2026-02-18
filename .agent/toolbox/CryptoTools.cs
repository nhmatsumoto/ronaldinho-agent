using System.Security.Cryptography;
using System.Text;

namespace Ronaldinho.Toolbox;

public static class CryptoTools
{
    /// <summary>
    /// Encrypts data using AES-GCM (v3 - modern standard).
    /// </summary>
    public static (string Ciphertext, string Nonce, string Tag) Encrypt(string plaintext, byte[] key)
    {
        using var aes = new AesGcm(key, tagSizeInBytes: 16);
        
        byte[] nonce = new byte[12]; // Standard 12-byte nonce for AES-GCM
        RandomNumberGenerator.Fill(nonce);
        
        byte[] plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
        byte[] ciphertext = new byte[plaintextBytes.Length];
        byte[] tag = new byte[16];
        
        aes.Encrypt(nonce, plaintextBytes, ciphertext, tag);
        
        return (Convert.ToBase64String(ciphertext), Convert.ToBase64String(nonce), Convert.ToBase64String(tag));
    }

    public static string Decrypt(string ciphertextB64, string nonceB64, string tagB64, byte[] key)
    {
        using var aes = new AesGcm(key, tagSizeInBytes: 16);
        
        byte[] ciphertext = Convert.FromBase64String(ciphertextB64);
        byte[] nonce = Convert.FromBase64String(nonceB64);
        byte[] tag = Convert.FromBase64String(tagB64);
        byte[] plaintextBytes = new byte[ciphertext.Length];
        
        aes.Decrypt(nonce, ciphertext, tag, plaintextBytes);
        
        return Encoding.UTF8.GetString(plaintextBytes);
    }
}
