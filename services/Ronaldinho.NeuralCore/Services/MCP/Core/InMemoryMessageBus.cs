using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Ronaldinho.NeuralCore.Services.MCP.Core;

/// <summary>
/// A fast, thread-safe message bus for coordinating local agents.
/// </summary>
public class InMemoryMessageBus : IMessageBus
{
    // Dictionary mapping Topic -> List of Subscribers
    private readonly ConcurrentDictionary<string, List<Func<McpMessage, Task>>> _subscribers = new();
    
    // Dictionary mapping CorrelationId -> TaskCompletionSource (used for RPC Wait)
    private readonly ConcurrentDictionary<string, TaskCompletionSource<McpMessage>> _waitingReplies = new();

    public async Task PublishAsync(McpMessage message)
    {
        Console.WriteLine($"[MCP Bus] Routing message '{message.TaskDescription}' from '{message.Sender}' -> '{message.TargetTopic}'");

        // First, check if someone is specifically waiting for a direct reply (CorrelationId / ReplyTo pattern)
        if (!string.IsNullOrEmpty(message.TargetTopic) && _waitingReplies.TryGetValue(message.TargetTopic, out var tcs))
        {
            tcs.TrySetResult(message);
            _waitingReplies.TryRemove(message.TargetTopic, out _);
            return; // We consumed this as a reply.
        }

        // If not a direct reply, route to general topic subscribers
        if (_subscribers.TryGetValue(message.TargetTopic, out var handlers))
        {
            // Execute all handlers concurrently
            var tasks = new List<Task>();
            foreach (var handler in handlers)
            {
                tasks.Add(Task.Run(() => handler(message)));
            }
            await Task.WhenAll(tasks);
        }
        else
        {
            Console.WriteLine($"[MCP Bus] Warning: No subscribers found for topic '{message.TargetTopic}'");
        }
    }

    public void Subscribe(string topic, Func<McpMessage, Task> handler)
    {
        _subscribers.AddOrUpdate(
            topic, 
            new List<Func<McpMessage, Task>> { handler }, 
            (key, existingList) => 
            {
                lock(existingList) { existingList.Add(handler); }
                return existingList;
            }
        );
        Console.WriteLine($"[MCP Bus] Agent subscribed to Topic: '{topic}'");
    }

    public async Task<McpMessage> WaitForReplyAsync(string correlationTopic, TimeSpan timeout)
    {
        var tcs = new TaskCompletionSource<McpMessage>(TaskCreationOptions.RunContinuationsAsynchronously);
        
        // Register the one-time waiter
        _waitingReplies.TryAdd(correlationTopic, tcs);

        // Cancel if timeout is reached
        using var timer = new Timer(state => 
        {
            var tcsState = (TaskCompletionSource<McpMessage>)state!;
            tcsState.TrySetException(new TimeoutException($"[MCP Bus] Timeout ({timeout.TotalSeconds}s) waiting for reply on '{correlationTopic}'"));
        }, tcs, timeout, Timeout.InfiniteTimeSpan);

        try 
        {
            // Wait for the completion source to be triggered by PublishAsync
            return await tcs.Task;
        }
        finally 
        {
            // Clean up to prevent memory leaks
            _waitingReplies.TryRemove(correlationTopic, out _);
        }
    }
}
