using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Ronaldinho.Contracts;

namespace Ronaldinho.P2P
{
    /// <summary>
    /// Exposes the P2P network as a gateway so other components can send/receive messages via the peer network.
    /// </summary>
    public class P2PGateway : IGateway, IDisposable
    {
        private readonly ILogger<P2PGateway> _logger;
        private readonly PeerNode _peerNode;
        private readonly IMessageProcessor _processor;
        private readonly CancellationTokenSource _cts = new();
        private readonly string _signalingUrl;
        private readonly string _remotePeerId;
        private readonly string _localPeerId;
        private readonly bool _isInitiator;

        public string Name => "P2P";

        public P2PGateway(string signalingUrl, string localPeerId, string remotePeerId, bool isInitiator, IMessageProcessor processor, ILoggerFactory loggerFactory)
        {
            _logger = loggerFactory.CreateLogger<P2PGateway>();
            _processor = processor ?? throw new ArgumentNullException(nameof(processor));
            _peerNode = new PeerNode(loggerFactory.CreateLogger<PeerNode>());
            _signalingUrl = signalingUrl;
            _localPeerId = localPeerId;
            _remotePeerId = remotePeerId;
            _isInitiator = isInitiator;

            // Register a default handler for generic messages
            _peerNode.RegisterHandler("message", async payload => await HandleIncomingAsync(payload));
        }

        public async Task StartAsync(CancellationToken cancellationToken = default)
        {
            _logger.LogInformation("Starting P2P Gateway (Local: {Local}, Remote: {Remote}, Initiator: {IsInitiator})...", _localPeerId, _remotePeerId, _isInitiator);
            await _peerNode.ConnectAsync(_signalingUrl, _localPeerId, _remotePeerId, _isInitiator);
        }

        public async Task StopAsync(CancellationToken cancellationToken = default)
        {
            _logger.LogInformation("Stopping P2P Gateway...");
            _cts.Cancel();
            await Task.CompletedTask;
        }

        private async Task HandleIncomingAsync(string payload)
        {
            // Forward the payload to the processor.
            await _processor.ProcessAsync("P2P", Guid.NewGuid().ToString(), "unknown", payload);
        }

        public async Task SendAsync(string targetPeerId, string channel, string message)
        {
            // Simple protocol: "channel|payload"
            var formatted = $"{channel}|{message}";
            await _peerNode.SendMessageAsync(formatted);
        }

        public void RegisterHandler(string channel, Func<string, Task> handler)
        {
            _peerNode.RegisterHandler(channel, handler);
        }

        public void Dispose()
        {
            _cts.Cancel();
            _cts.Dispose();
            _peerNode.Dispose();
        }
    }
}
