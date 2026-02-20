using System.Threading.Tasks;

namespace Ronaldinho.NeuralCore.Services.MCP.Core;

/// <summary>
/// The standard contract for every Agent operating within the MCP network.
/// </summary>
public interface IMcpAgent
{
    /// <summary>
    /// The unique topic/name of this agent (e.g., "coder").
    /// </summary>
    string Topic { get; }
    
    /// <summary>
    /// A description of the agent's capabilities, so the orchestrator knows when to use it.
    /// </summary>
    string Description { get; }

    /// <summary>
    /// The main entry point when a message is routed to this agent by the IMessageBus.
    /// </summary>
    Task ProcessMessageAsync(McpMessage message);
}
