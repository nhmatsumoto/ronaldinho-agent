using System;

namespace Ronaldinho.NeuralCore.Services.MCP.Core;

/// <summary>
/// A strongly-typed message payload exchanged between agents in the MCP network.
/// </summary>
public record McpMessage
{
    public Guid Id { get; init; } = Guid.NewGuid();
    
    /// <summary>
    /// The name of the agent sending the message (e.g., "orchestrator")
    /// </summary>
    public string Sender { get; init; } = string.Empty;
    
    /// <summary>
    /// The topic or agent this message is intended for (e.g., "coder", "researcher")
    /// </summary>
    public string TargetTopic { get; init; } = string.Empty;
    
    /// <summary>
    /// For request-response patterns. The target should send the answer back to this topic.
    /// </summary>
    public string ReplyTo { get; init; } = string.Empty;
    
    /// <summary>
    /// A human/LLM readable description of what needs to be done.
    /// </summary>
    public string TaskDescription { get; init; } = string.Empty;
    
    /// <summary>
    /// Optional JSON or structured data payload.
    /// </summary>
    public string Payload { get; init; } = string.Empty;
    
    /// <summary>
    /// The original correlation ID from the initial user request, to tie the whole chain together.
    /// </summary>
    public string CorrelationId { get; init; } = string.Empty;
}
