using System.Threading;
using System.Threading.Tasks;
using Ronaldinho.Contracts;

namespace Ronaldinho.NeuralCore.Gateway;

/// <summary>
/// Manages the lifecycle of multiple integration gateways.
/// </summary>
public class GatewayRegistry
{
    private readonly List<IGateway> _gateways = new();

    public GatewayRegistry AddGateway(IGateway gateway)
    {
        Console.WriteLine($"[Registry] Registering Gateway: {gateway.Name}");
        _gateways.Add(gateway);
        return this;
    }

    public async Task StartAllAsync(CancellationToken cancellationToken = default)
    {
        Console.WriteLine($"[Registry] Starting {_gateways.Count} Gateways...");
        var tasks = new List<Task>();

        foreach (var gateway in _gateways)
        {
            var task = gateway.StartAsync(cancellationToken).ContinueWith(t =>
            {
                if (t.IsFaulted)
                {
                    Console.WriteLine($"[Registry] Gateway {gateway.Name} encountered a fatal error: {t.Exception?.GetBaseException().Message}");
                }
            }, TaskContinuationOptions.ExecuteSynchronously);

            tasks.Add(task);
        }

        await Task.WhenAll(tasks);
    }

    public async Task StopAllAsync(CancellationToken cancellationToken = default)
    {
        Console.WriteLine($"[Registry] Stopping all Gateways...");
        var tasks = new List<Task>();

        foreach (var gateway in _gateways)
        {
            tasks.Add(gateway.StopAsync(cancellationToken));
        }

        await Task.WhenAll(tasks);
    }
}
