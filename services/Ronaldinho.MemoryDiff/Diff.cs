using Newtonsoft.Json.Linq;
using System;

namespace Ronaldinho.MemoryDiff
{
    /// <summary>
    /// Represents a JSON‑Patch (RFC 6902) diff between two commits.
    /// </summary>
    public class Diff
    {
        public string FromCommitId { get; set; } = string.Empty;
        public string ToCommitId { get; set; } = string.Empty;
        public JToken Patch { get; set; } = JValue.CreateNull();

        public Diff(string fromId, string toId, JToken patch)
        {
            FromCommitId = fromId;
            ToCommitId = toId;
            Patch = patch;
        }
    }
}
