using System.Security.Cryptography;
using System.Text;

namespace Ronaldinho.NeuralCore.Core.Memory;

public class SessionContext
{
    public string SessionId { get; set; }
    public string PlatformId { get; set; }
    public string ChannelId { get; set; }
    public string UserId { get; set; }
}

public class SessionRouter
{
    /// <summary>
    /// Generates a deterministic, unique SHA256 hashed Session ID to guarantee context isolation 
    /// between different platforms, channels, and users.
    /// Inspired by OpenClaw's routing strictness.
    /// </summary>
    public SessionContext Route(string platformId, string channelId, string userId)
    {
        var rawString = $"{platformId}::{channelId}::{userId}";
        var hashBytes = SHA256.HashData(Encoding.UTF8.GetBytes(rawString));
        var sessionId = Convert.ToHexString(hashBytes).ToLowerInvariant();

        return new SessionContext
        {
            SessionId = sessionId,
            PlatformId = platformId,
            ChannelId = channelId,
            UserId = userId
        };
    }
}
