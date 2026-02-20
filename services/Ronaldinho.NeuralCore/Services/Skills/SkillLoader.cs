using System.Text.Json;
using Microsoft.SemanticKernel; // For Kernel and Plugins
using Ronaldinho.NeuralCore.Skills; // For FileSkill, ContextSkill

namespace Ronaldinho.NeuralCore.Services.Skills;

public class SkillLoader
{
    private readonly string _rootPath;
    private readonly Kernel _kernel;

    public SkillLoader(Kernel kernel, string rootPath)
    {
        _kernel = kernel;
        _rootPath = rootPath;
    }

    public void LoadSkills()
    {
        string manifestPath = Path.Combine(_rootPath, "services", "Ronaldinho.NeuralCore", "skills.json");
        if (!File.Exists(manifestPath))
        {
            Console.WriteLine($"[SkillLoader] Warning: Manifest not found at {manifestPath}");
            return;
        }

        try
        {
            var json = File.ReadAllText(manifestPath);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("skills", out var skillsElement))
            {
                foreach (var skill in skillsElement.EnumerateArray())
                {
                    string name = skill.GetProperty("name").GetString() ?? "unknown";
                    bool enabled = skill.GetProperty("enabled").GetBoolean();

                    if (enabled)
                    {
                        LoadSkill(name);
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[SkillLoader] Error loading skills: {ex.Message}");
        }
    }

    private void LoadSkill(string name)
    {
        try
        {
            object? plugin = name switch
            {
                "file" => new FileSkill(_rootPath),
                "context" => new ContextSkill(_rootPath),
                // "auth" is usually loaded earlier due to dependencies, but could be here if decoupled
                // "findings" will be added next
                _ => null
            };

            if (plugin != null)
            {
                _kernel.Plugins.AddFromObject(plugin, name);
                Console.WriteLine($"[SkillLoader] Loaded skill: {name}");
            }
            else if (name != "auth" && name != "findings") // Auth and Findings might be special handled or not yet implemented
            {
                Console.WriteLine($"[SkillLoader] Warning: Skill '{name}' implementation not found.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[SkillLoader] Failed to load '{name}': {ex.Message}");
        }
    }
}
