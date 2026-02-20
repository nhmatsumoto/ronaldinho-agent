using System;
using System.Threading.Tasks;

namespace Ronaldinho.NeuralCore.Services.MCP.Core;

/// <summary>
/// Contracts for the central message bus coordinating the MCP network.
/// </summary>
public interface IMessageBus
{
    /// <summary>
    /// Publishes a message to the bus. Subscribers to the target topic will process it.
    /// </summary>
    Task PublishAsync(McpMessage message);

    /// <summary>
    /// Subscribes an agent callback to a specific topic.
    /// </summary>
    void Subscribe(string topic, Func<McpMessage, Task> handler);
    
    /// <summary>
    /// Subscribes for a single message matching a correlation ID (useful for RPC/Request-Reply logic).
    /// </summary>
    Task<McpMessage> WaitForReplyAsync(string correlationTopic, TimeSpan timeout);
}
