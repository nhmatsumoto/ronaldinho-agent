using System.Threading;
using System.Threading.Tasks;

namespace Ronaldinho.Contracts
{
    /// <summary>
    /// A universal interface for all input/output channels (Telegram, WhatsApp, P2P, etc.)
    /// </summary>
    public interface IGateway
    {
        string Name { get; }
        Task StartAsync(CancellationToken cancellationToken = default);
        Task StopAsync(CancellationToken cancellationToken = default);
    }
}
