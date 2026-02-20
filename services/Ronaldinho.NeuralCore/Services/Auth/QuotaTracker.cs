using System.Collections.Concurrent;

namespace Ronaldinho.NeuralCore.Services.Auth;

public class QuotaTracker
{
    // Maps API Key -> Cooldown Expiration Time
    private readonly ConcurrentDictionary<string, DateTimeOffset> _cooldowns = new();
    private readonly ConcurrentDictionary<string, int> _usageCount = new();
    private readonly TimeSpan _bannishDuration = TimeSpan.FromMinutes(10); // Standard cooldown for 429

    public bool IsKeyAvailable(string key)
    {
        if (_cooldowns.TryGetValue(key, out var expiration))
        {
            if (DateTimeOffset.UtcNow < expiration)
            {
                return false; // Still cooling down
            }
            // Expired, remove it
            _cooldowns.TryRemove(key, out _);
        }
        return true;
    }

    public void ReportSuccess(string key)
    {
        _usageCount.AddOrUpdate(key, 1, (_, count) => count + 1);
    }

    public void ReportRateLimit(string key)
    {
        var expiration = DateTimeOffset.UtcNow.Add(_bannishDuration);
        _cooldowns.AddOrUpdate(key, expiration, (_, _) => expiration);
        string _suffix = new string(key.TakeLast(6).ToArray());
        Console.WriteLine($"[QuotaTracker] Key ending in ...{_suffix} cooldown until {expiration:HH:mm:ss}");
    }
}
