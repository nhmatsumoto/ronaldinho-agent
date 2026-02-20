namespace Ronaldinho.NeuralCore.Core.Memory;

public class TemporalDecayEngine
{
    /// <summary>
    /// Applies a time-based decay algorithm to the memory array.
    /// Older memories lose "weight" naturally, mimicking human forgetfulness 
    /// but prioritizing high-relevance/recent context within token limits.
    /// </summary>
    public List<MemoryEntry> ApplyDecay(List<MemoryEntry> history, int maxItems = 10)
    {
        if (history == null || !history.Any())
            return new List<MemoryEntry>();

        var currentTime = DateTime.UtcNow;

        // Basic Decay: We sort by Timestamp descending automatically. 
        // In a vector-based implementation (Phase 2), we would multiply semantic similarity scores 
        // by a decay factor e.g., Math.Exp(-lambda * daysElapsed).
        // For Phase 1, we simulate temporal decay by dropping the tail of the chronological list.
        
        var decayedList = history
            .OrderByDescending(e => e.Timestamp)
            .Take(maxItems) // Natural cut-off representing absolute forgotten context
            .OrderBy(e => e.Timestamp) // Re-sort chronological for LLM ingestion
            .ToList();

        return decayedList;
    }
}
