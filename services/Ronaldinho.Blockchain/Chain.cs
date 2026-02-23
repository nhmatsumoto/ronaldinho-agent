using System;
using System.Collections.Generic;
using System.Linq;
using LiteDB;
using Microsoft.Extensions.Logging;

namespace Ronaldinho.Blockchain
{
    /// <summary>
    /// Represents the blockchain ledger that stores knowledge transactions.
    /// Provides methods to add new blocks, validate the chain, and persist using LiteDB.
    /// </summary>
    public class Chain
    {
        private readonly ILogger<Chain> _logger;
        private readonly string _dbPath;
        private const int Difficulty = 3; // number of leading zeros required in hash

        public List<Block> Blocks { get; private set; } = new();
        public event Func<Block, Task>? OnBlockAdded;

        public Chain(string dbPath, ILogger<Chain> logger)
        {
            _dbPath = dbPath ?? throw new ArgumentNullException(nameof(dbPath));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            LoadFromDatabase();
        }

        private void LoadFromDatabase()
        {
            using var db = new LiteDatabase(_dbPath);
            var col = db.GetCollection<Block>("blocks");
            var stored = col.FindAll().OrderBy(b => b.Index).ToList();
            if (stored.Any())
            {
                Blocks = stored;
                _logger.LogInformation("Loaded blockchain with {Count} blocks from {Path}", Blocks.Count, _dbPath);
            }
            else
            {
                // Genesis block
                var genesis = CreateGenesisBlock();
                Blocks.Add(genesis);
                SaveBlock(genesis);
                _logger.LogInformation("Created genesis block.");
            }
        }

        private Block CreateGenesisBlock()
        {
            var genesis = new Block
            {
                Index = 0,
                Timestamp = DateTime.UtcNow,
                PreviousHash = new string('0', 64),
                Transactions = new List<KnowledgeTransaction>()
            };
            genesis.Nonce = MineNonce(genesis);
            genesis.Hash = genesis.ComputeHash();
            return genesis;
        }

        private int MineNonce(Block block)
        {
            int nonce = 0;
            while (true)
            {
                block.Nonce = nonce;
                var hash = block.ComputeHash();
                if (hash.StartsWith(new string('0', Difficulty)))
                    return nonce;
                nonce++;
            }
        }

        private void SaveBlock(Block block)
        {
            using var db = new LiteDatabase(_dbPath);
            var col = db.GetCollection<Block>("blocks");
            col.Insert(block);
            db.Commit();
        }

        /// <summary>
        /// Adds a new block containing the given transactions.
        /// </summary>
        public void AddBlock(IEnumerable<KnowledgeTransaction> transactions)
        {
            var previous = Blocks.Last();
            var newBlock = new Block
            {
                Index = previous.Index + 1,
                Timestamp = DateTime.UtcNow,
                PreviousHash = previous.Hash,
                Transactions = transactions.ToList()
            };
            newBlock.Nonce = MineNonce(newBlock);
            newBlock.Hash = newBlock.ComputeHash();
            Blocks.Add(newBlock);
            SaveBlock(newBlock);
            _logger.LogInformation("Added block {Index} with {TxCount} transactions.", newBlock.Index, newBlock.Transactions.Count);

            // Notify P2P network
            OnBlockAdded?.Invoke(newBlock);
        }

        /// <summary>
        /// Synchronizes blocks received from other peers.
        /// </summary>
        public void SyncBlocks(List<Block> newBlocks)
        {
            foreach (var block in newBlocks.OrderBy(b => b.Index))
            {
                if (block.Index <= Blocks.Last().Index) continue;

                // Simplified validation: just check if it fits the current chain end
                if (block.PreviousHash == Blocks.Last().Hash && block.Validate())
                {
                    Blocks.Add(block);
                    SaveBlock(block);
                    _logger.LogInformation("Synced block {Index} from peer.", block.Index);
                }
            }
        }

        /// <summary>
        /// Validates the integrity of the chain.
        /// </summary>
        public bool Validate()
        {
            for (int i = 1; i < Blocks.Count; i++)
            {
                var current = Blocks[i];
                var previous = Blocks[i - 1];
                if (current.PreviousHash != previous.Hash)
                {
                    _logger.LogError("Block {Index} has invalid previous hash.", current.Index);
                    return false;
                }
                if (current.ComputeHash() != current.Hash)
                {
                    _logger.LogError("Block {Index} hash mismatch.", current.Index);
                    return false;
                }
                if (!current.Hash.StartsWith(new string('0', Difficulty)))
                {
                    _logger.LogError("Block {Index} does not meet difficulty.", current.Index);
                    return false;
                }
            }
            return true;
        }
    }
}
