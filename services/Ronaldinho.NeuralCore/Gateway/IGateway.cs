using System.Threading;
using System.Threading.Tasks;

namespace Ronaldinho.NeuralCore.Gateway;

/// <summary>
/// A universal interface for all input/output channels (Telegram, WhatsApp, Web, Voice, etc.)
/// </summary>
public interface IGateway
{
    string Name { get; }
    Task StartAsync(CancellationToken cancellationToken = default);
    Task StopAsync(CancellationToken cancellationToken = default);
}
