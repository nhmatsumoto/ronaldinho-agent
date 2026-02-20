using System.Net;

namespace Ronaldinho.NeuralCore.Services.Auth;

/// <summary>
/// A "True Antigravity" handler that intercepts requests and rotates keys if 429 is encountered.
/// </summary>
public class RotationHandler : DelegatingHandler
{
    private readonly KeyVaultService _keyVault;
    private readonly QuotaTracker _quotaTracker;
    private readonly string _provider = "Gemini"; 

    public RotationHandler(KeyVaultService keyVault, QuotaTracker quotaTracker)
    {
        _keyVault = keyVault;
        _quotaTracker = quotaTracker;
    }

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        // 1. Pick a key (Naive Round-Robin or Random for now, improving later)
        // Actually, the request *already* has a key if SK built it.
        // We need to STRIP it and replace it with a valid one.
        // Or, assume the initial request has a dummy key and we always inject a valid one.
        
        // Let's try to execute with the current URL first (or inject a fresh key).
        // Since SK appends the key, let's parse it?
        // Google: https://.../models/...?key=OLD_KEY
        
        var keys = _keyVault.GetKeys(_provider);
        if (keys.Count == 0) return await base.SendAsync(request, cancellationToken);

        // Try loop
        foreach (var key in keys)
        {
            if (!_quotaTracker.IsKeyAvailable(key)) continue;

            // Rewrite URL with this key
            var uriBuilder = new UriBuilder(request.RequestUri!);
            var query = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            query["key"] = key;
            uriBuilder.Query = query.ToString();
            request.RequestUri = uriBuilder.Uri;

            string suffix = new string(key.TakeLast(4).ToArray());
            Console.WriteLine($"[RotationHandler] Using key ending in ...{suffix}");

            var response = await base.SendAsync(request, cancellationToken);

            if (response.StatusCode == HttpStatusCode.TooManyRequests)
            {
                string errorSuffix = new string(key.TakeLast(4).ToArray());
                Console.WriteLine($"[RotationHandler] 429 Detected for key ...{errorSuffix}. Cooldown initiated.");
                _quotaTracker.ReportRateLimit(key);
                // Continue to next key
                continue;
            }

            if (response.IsSuccessStatusCode)
            {
                _quotaTracker.ReportSuccess(key);
            }
            
            return response;
        }

        // If all keys failed or exhausted
        Console.WriteLine("[RotationHandler] All keys exhausted or failed.");
        return new HttpResponseMessage(HttpStatusCode.TooManyRequests);
    }
}
