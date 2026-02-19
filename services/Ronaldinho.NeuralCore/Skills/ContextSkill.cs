using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Skills;

public class ContextSkill
{
    private readonly string _rootPath;

    public ContextSkill(string rootPath)
    {
        _rootPath = rootPath;
    }

    [KernelFunction, Description("Gera um mapa recursivo da estrutura do projeto (pastas e arquivos).")]
    public string MapProject(
        [Description("Profundidade máxima da pesquisa (padrão: 3)")] int maxDepth = 3)
    {
        var tree = new List<string>();
        var ignore = new HashSet<string> { ".git", "__pycache__", "bin", "obj", "node_modules", ".venv" };

        void Walk(string path, int depth)
        {
            if (depth > maxDepth) return;
            try
            {
                foreach (var item in Directory.GetFileSystemEntries(path).OrderBy(x => x))
                {
                    string name = Path.GetFileName(item);
                    if (ignore.Contains(name)) continue;

                    bool isDir = Directory.Exists(item);
                    string relPath = Path.GetRelativePath(_rootPath, item);
                    string prefix = new string(' ', depth * 2) + (isDir ? "📁 " : "📄 ");
                    
                    tree.Add($"{prefix}{relPath}");

                    if (isDir) Walk(item, depth + 1);
                }
            }
            catch (Exception ex)
            {
                tree.Add(new string(' ', depth * 2) + $"⚠️ Erro em {path}: {ex.Message}");
            }
        }

        Walk(_rootPath, 0);
        return string.Join("\n", tree);
    }

    [KernelFunction, Description("Retorna um resumo do estado atual do projeto (identidade, missões, habilidades).")]
    public string GetProjectSummary()
    {
        var summary = new List<string>
        {
            "Projeto: Ronaldinho-Agent (NeuralCore)",
            $"Local: {_rootPath}"
        };

        // Skill count
        string skillsPath = Path.Combine(_rootPath, "services", "Ronaldinho.NeuralCore", "Skills");
        if (Directory.Exists(skillsPath))
        {
            var skills = Directory.GetFiles(skillsPath, "*.cs").Length;
            summary.Add($"Habilidades Nativas: {skills}");
        }

        return string.Join("\n", summary);
    }
}
