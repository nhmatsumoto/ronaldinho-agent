using Microsoft.SemanticKernel;
using System.ComponentModel;

namespace Ronaldinho.NeuralCore.Services.Skills;

public class FindingsSkill
{
    private readonly string _findingsPath;

    public FindingsSkill(string rootPath)
    {
        // Using .toon extension for Token-Oriented Object Notation (Optimized Context)
        _findingsPath = Path.Combine(rootPath, "findings.toon");
    }

    [KernelFunction, Description("Saves a key research finding or insight to persistent memory in TOON format.")]
    public async Task SaveFindingAsync(
        [Description("The topic or category of the finding (e.g., 'Gemini API')")] string topic,
        [Description("Concise content of the finding (bullet points preferred)")] string content)
    {
        // TOON Format: Minimalist, Structured, High-Signal
        string entry = $"\n## 🧠 {topic} [{DateTime.Now:yyyy-MM-dd}]\n{content}\n";
        await File.AppendAllTextAsync(_findingsPath, entry);
        Console.WriteLine($"[FindingsSkill] Saved insight about '{topic}' to .toon");
    }

    [KernelFunction, Description("Reads all past findings.")]
    public async Task<string> ReadFindingsAsync()
    {
        if (File.Exists(_findingsPath))
        {
            return await File.ReadAllTextAsync(_findingsPath);
        }
        return "No findings recorded yet.";
    }
}
