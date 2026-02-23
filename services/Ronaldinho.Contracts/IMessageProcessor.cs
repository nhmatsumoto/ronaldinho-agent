using System.Threading.Tasks;

namespace Ronaldinho.Contracts
{
    /// <summary>
    /// Interface for processing messages from gateways.
    /// Used to decouple the orchestrator from the communication layer.
    /// </summary>
    public interface IMessageProcessor
    {
        Task<string> ProcessAsync(string platform, string channelId, string userId, string input);
    }
}
