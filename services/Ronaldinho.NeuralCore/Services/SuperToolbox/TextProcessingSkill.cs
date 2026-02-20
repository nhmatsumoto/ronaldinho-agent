using System.ComponentModel;
using System.Linq;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.SuperToolbox;

/// <summary>
/// A native kernel plugin for manipulating text strings directly in the orchestrator pipeline.
/// </summary>
public sealed class TextProcessingSkill
{
    [KernelFunction, Description("Counts the number of words in a given text string.")]
    public int CountWords(
        [Description("The text to process")] string input)
    {
        if (string.IsNullOrWhiteSpace(input)) return 0;
        
        var charDelimiters = new[] { ' ', '\r', '\n' };
        return input.Split(charDelimiters, System.StringSplitOptions.RemoveEmptyEntries).Length;
    }

    [KernelFunction, Description("Extracts lines from a text string that contain a specific keyword.")]
    public string ExtractLinesWithKeyword(
        [Description("The full text to search through")] string text,
        [Description("The keyword to find")] string keyword)
    {
        if (string.IsNullOrWhiteSpace(text) || string.IsNullOrWhiteSpace(keyword))
            return string.Empty;

        var lines = text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        var matchedLines = lines.Where(l => l.Contains(keyword, System.StringComparison.OrdinalIgnoreCase)).ToArray();

        return matchedLines.Length > 0 
            ? string.Join("\n", matchedLines) 
            : "No lines containing the keyword were found.";
    }

    [KernelFunction, Description("Calculates a basic structural diff between two small text strings.")]
    public string BasicTextDiff(
        [Description("The original text")] string original,
        [Description("The modified text")] string modified)
    {
        // Note: For a true file diff, we would use a more sophisticated diffing library like DiffPlex.
        // This acts as a placeholder for simple string comparison in the brain.
        if (original == modified) return "No changes detected.";

        var origLines = original.Split('\n');
        var modLines = modified.Split('\n');

        return $"Strings differ. Original has {origLines.Length} lines. Modified has {modLines.Length} lines.";
    }
}
