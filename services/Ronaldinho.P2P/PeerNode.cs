using System;
using System.Collections.Concurrent;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using SIPSorcery.Net;

namespace Ronaldinho.P2P
{
    /// <summary>
    /// Represents a peer node that establishes a WebRTC DataChannel with another peer using SIPSorcery.
    /// </summary>
    public class PeerNode : IDisposable
    {
        private readonly ILogger<PeerNode> _logger;
        private readonly ConcurrentDictionary<string, Func<string, Task>> _messageHandlers = new();
        private readonly CancellationTokenSource _cts = new();
        private readonly HttpClient _httpClient = new();

        private RTCPeerConnection? _peerConnection;
        private RTCDataChannel? _dataChannel;

        public PeerNode(ILogger<PeerNode> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <summary>
        /// Connects to a remote peer using a signaling URL.
        /// </summary>
        public async Task ConnectAsync(string signalingUrl, string remotePeerId)
        {
            _logger.LogInformation("Initiating WebRTC connection to {RemotePeerId} via {Url}", remotePeerId, signalingUrl);

            _peerConnection = new RTCPeerConnection();

            // Create data channel
            _dataChannel = await _peerConnection.createDataChannel("ronaldinho-data");
            _dataChannel.onmessage += (dc, protocol, data) => OnDataChannelMessage(data);
            _dataChannel.onopen += () => _logger.LogInformation("DataChannel opened with {RemotePeerId}", remotePeerId);
            _dataChannel.onclose += () => _logger.LogWarning("DataChannel closed with {RemotePeerId}", remotePeerId);

            // ICE Candidates
            _peerConnection.onicecandidate += async (candidate) =>
            {
                if (candidate != null)
                {
                    await SendSignalingMessage(signalingUrl, remotePeerId, "ice", candidate.ToString());
                }
            };

            // Create Offer
            var offer = _peerConnection.createOffer();
            await _peerConnection.setLocalDescription(offer);

            // Send Offer via signaling
            await SendSignalingMessage(signalingUrl, remotePeerId, "offer", offer.sdp);

            _logger.LogInformation("Offer sent to {RemotePeerId}. Waiting for answer...", remotePeerId);

            // Start listening for signaling responses (polling for simplicity in this version)
            _ = PollSignalingAsync(signalingUrl, remotePeerId);
        }

        private async Task SendSignalingMessage(string url, string targetId, string type, string data)
        {
            try
            {
                var payload = JsonSerializer.Serialize(new { type, data, targetId });
                var content = new StringContent(payload, Encoding.UTF8, "application/json");
                await _httpClient.PostAsync($"{url}/send", content);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send signaling message {Type}", type);
            }
        }

        private async Task PollSignalingAsync(string url, string peerId)
        {
            while (!_cts.Token.IsCancellationRequested)
            {
                try
                {
                    var response = await _httpClient.GetStringAsync($"{url}/receive?peerId={peerId}");
                    if (!string.IsNullOrEmpty(response))
                    {
                        var messages = JsonSerializer.Deserialize<SignalingMessage[]>(response);
                        if (messages != null)
                        {
                            foreach (var msg in messages)
                            {
                                await HandleSignalingMessage(msg);
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogTrace("Signaling poll failed (expected if no messages): {Message}", ex.Message);
                }
                await Task.Delay(2000, _cts.Token);
            }
        }

        private async Task HandleSignalingMessage(SignalingMessage msg)
        {
            if (_peerConnection == null) return;

            switch (msg.Type)
            {
                case "answer":
                    _logger.LogInformation("Received answer from peer.");
                    _peerConnection.setRemoteDescription(new RTCSessionDescriptionInit { type = RTCSdpType.answer, sdp = msg.Data });
                    break;
                case "ice":
                    _logger.LogDebug("Received ICE candidate from peer.");
                    _peerConnection.addIceCandidate(new RTCIceCandidateInit { candidate = msg.Data });
                    break;
            }
        }

        private void OnDataChannelMessage(byte[] data)
        {
            var raw = Encoding.UTF8.GetString(data);
            _logger.LogDebug("Received raw message: {Raw}", raw);

            var parts = raw.Split('|', 2);
            if (parts.Length != 2) return;

            var channel = parts[0];
            var payload = parts[1];

            if (_messageHandlers.TryGetValue(channel, out var handler))
            {
                _ = handler(payload);
            }
        }

        public async Task SendMessageAsync(string message)
        {
            if (_dataChannel == null || _dataChannel.readyState != RTCDataChannelState.open)
                throw new InvalidOperationException("DataChannel not ready.");

            _dataChannel.send(message);
            _logger.LogDebug("Sent message: {Message}", message);
            await Task.CompletedTask;
        }

        public void RegisterHandler(string channel, Func<string, Task> handler)
        {
            _messageHandlers[channel] = handler;
        }

        public void Dispose()
        {
            _cts.Cancel();
            _httpClient.Dispose();
            _peerConnection?.Close("Disposed");
            _cts.Dispose();
        }

        private class SignalingMessage
        {
            public string Type { get; set; } = string.Empty;
            public string Data { get; set; } = string.Empty;
        }
    }
}
