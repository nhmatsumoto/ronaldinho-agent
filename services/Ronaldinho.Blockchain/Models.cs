using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Ronaldinho.Blockchain
{
    /// <summary>
    /// Represents a single knowledge transaction that will be stored in a block.
    /// </summary>
    public class KnowledgeTransaction
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public string Data { get; set; } = string.Empty; // JSON payload representing knowledge
        public string Author { get; set; } = string.Empty;
    }

    /// <summary>
    /// Represents a block in the lightweight blockchain.
    /// </summary>
    public class Block
    {
        public int Index { get; set; }
        public DateTime Timestamp { get; set; }
        public string PreviousHash { get; set; } = string.Empty;
        public string Hash { get; set; } = string.Empty;
        public int Nonce { get; set; }
        public List<KnowledgeTransaction> Transactions { get; set; } = new();

        /// <summary>
        /// Calculates the SHA‑256 hash of the block contents.
        /// </summary>
        public string ComputeHash()
        {
            var payload = JsonSerializer.Serialize(new
            {
                Index,
                Timestamp,
                PreviousHash,
                Nonce,
                Transactions
            });
            using var sha = SHA256.Create();
            var bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(payload));
            return Convert.ToHexString(bytes);
        }

        public bool Validate()
        {
            return ComputeHash() == Hash;
        }
    }
}
