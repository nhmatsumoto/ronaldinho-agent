using Google.Apis.Auth.OAuth2;
using Google.Apis.Auth.OAuth2.Flows;
using Google.Apis.Auth.OAuth2.Responses;
using Google.Apis.Util.Store;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json; 

namespace Ronaldinho.NeuralCore.Services.Auth;

public class GoogleAuthService
{
    private readonly string _clientId;
    private readonly string _clientSecret;
    private readonly TokenStorageService _tokenStorage;
    
    // Scopes needed for basic profile and future services
    private static readonly string[] Scopes = { 
        "openid", 
        "email", 
        "profile",
        "https://www.googleapis.com/auth/drive.readonly", // Example scope
        "https://www.googleapis.com/auth/calendar.readonly" 
    };

    public GoogleAuthService(IConfiguration config, TokenStorageService tokenStorage)
    {
        _clientId = config["GOOGLE_CLIENT_ID"] ?? "";
        _clientSecret = config["GOOGLE_CLIENT_SECRET"] ?? "";
        _tokenStorage = tokenStorage;
    }

    public async Task<UserCredential?> AuthenticateAsync()
    {
        if (string.IsNullOrEmpty(_clientId) || string.IsNullOrEmpty(_clientSecret))
        {
            Console.WriteLine("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env");
            return null;
        }

        try
        {
            Console.WriteLine("🔐 Initiating Secure Google OAuth2 Flow...");

            // Custom DataStore bridge to use our DPAPI storage
            var dataStore = new SecureDataStore(_tokenStorage);

            var credential = await GoogleWebAuthorizationBroker.AuthorizeAsync(
                new ClientSecrets
                {
                    ClientId = _clientId,
                    ClientSecret = _clientSecret
                },
                Scopes,
                "user",
                CancellationToken.None,
                dataStore
            );

            Console.WriteLine($"✅ Authenticated as: {credential.Token.Scope}");
            return credential;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Auth Failed: {ex.Message}");
            return null;
        }
    }
}

// Bridge between Google library's IDataStore and our DPAPI TokenStorageService
public class SecureDataStore : IDataStore
{
    private readonly TokenStorageService _storage;

    public SecureDataStore(TokenStorageService storage)
    {
        _storage = storage;
    }

    public Task StoreAsync<T>(string key, T value)
    {
        var json = JsonConvert.SerializeObject(value);
        _storage.SaveToken("google_" + key, json);
        return Task.CompletedTask;
    }

    public Task<T> GetAsync<T>(string key)
    {
        var json = _storage.LoadToken("google_" + key);
        if (string.IsNullOrEmpty(json))
            return Task.FromResult<T>(default!);

        var result = JsonConvert.DeserializeObject<T>(json);
        return Task.FromResult(result!);
    }

    public Task DeleteAsync<T>(string key)
    {
        // Not implemented for this MVP
        return Task.CompletedTask;
    }

    public Task ClearAsync()
    {
        return Task.CompletedTask;
    }
}
