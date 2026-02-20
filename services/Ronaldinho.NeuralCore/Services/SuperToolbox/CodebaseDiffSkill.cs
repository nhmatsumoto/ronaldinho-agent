using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.SuperToolbox;

public class CodebaseDiffSkill
{
    private readonly string _rootPath;

    public CodebaseDiffSkill(string rootPath)
    {
        _rootPath = rootPath;
    }

    [KernelFunction("perform_text_diff")]
    [Description("Performs a basic unified-diff like comparison between two text snippets (e.g. file contents or function blocks) to identify additions and deletions locally without requiring git.")]
    public string PerformTextDiff(
        [Description("The original baseline text snippet")] string originalText,
        [Description("The modified text snippet to compare against")] string newText)
    {
        var originalLines = originalText.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);
        var newLines = newText.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);

        // A naive diff implementation using dynamic programming or simple line checking
        // Since full Hunt-Szymanski diff is complex for a native skill snippet, we do a fast line-by-line comparison
        // prioritizing insertions and deletions block by block.
        
        var diffResult = new System.Text.StringBuilder();
        
        int i = 0, j = 0;
        while (i < originalLines.Length || j < newLines.Length)
        {
            if (i < originalLines.Length && j < newLines.Length && originalLines[i] == newLines[j])
            {
                diffResult.AppendLine($"  {originalLines[i]}"); // Unchanged
                i++;
                j++;
            }
            else
            {
                // Mismatch block. Gather deletions
                while (i < originalLines.Length && (j >= newLines.Length || originalLines[i] != newLines[j]))
                {
                    diffResult.AppendLine($"- {originalLines[i]}");
                    i++;
                }

                // Gather insertions
                while (j < newLines.Length && (i >= originalLines.Length || (i < originalLines.Length && originalLines[i] != newLines[j])))
                {
                    diffResult.AppendLine($"+ {newLines[j]}");
                    j++;
                }
            }
        }

        return diffResult.ToString();
    }
}
