using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Ronaldinho.MemoryDiff
{
    /// <summary>
    /// Represents a snapshot of the agent's knowledge state.
    /// </summary>
    public class Commit
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public string DataJson { get; set; } = "{}"; // Serialized knowledge payload

        public Commit(object data)
        {
            DataJson = JsonConvert.SerializeObject(data, Formatting.Indented);
        }
    }
}
