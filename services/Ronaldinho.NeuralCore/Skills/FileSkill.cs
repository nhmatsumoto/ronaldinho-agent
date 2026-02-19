using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Skills;

public class FileSkill
{
    private readonly string _workspacePath;

    public FileSkill(string rootPath)
    {
        _workspacePath = Path.Combine(rootPath, "workspace");
        if (!Directory.Exists(_workspacePath))
        {
            Directory.CreateDirectory(_workspacePath);
        }
    }

    [KernelFunction, Description("Cria um novo arquivo ou sobrescreve um existente na pasta workspace/")]
    public string CreateFile(
        [Description("Nome do arquivo (ex: script.py ou index.html)")] string filename,
        [Description("Conteúdo completo do arquivo")] string content)
    {
        try
        {
            // Security: Enforce workspace isolation
            string safeFilename = Path.GetFileName(filename);
            string fullPath = Path.Combine(_workspacePath, safeFilename);
            
            File.WriteAllText(fullPath, content);
            return $"✅ Arquivo '{safeFilename}' criado com sucesso na workspace.";
        }
        catch (Exception ex)
        {
            return $"❌ Erro ao criar arquivo: {ex.Message}";
        }
    }

    [KernelFunction, Description("Lê o conteúdo de um arquivo da pasta workspace/")]
    public string ReadFile(
        [Description("Nome do arquivo para ler")] string filename)
    {
        try
        {
            string safeFilename = Path.GetFileName(filename);
            string fullPath = Path.Combine(_workspacePath, safeFilename);

            if (!File.Exists(fullPath)) return $"⚠️ Arquivo '{safeFilename}' não encontrado.";

            return File.ReadAllText(fullPath);
        }
        catch (Exception ex)
        {
            return $"❌ Erro ao ler arquivo: {ex.Message}";
        }
    }

    [KernelFunction, Description("Lista todos os arquivos presentes na pasta workspace/")]
    public string ListFiles()
    {
        try
        {
            var files = Directory.GetFiles(_workspacePath);
            if (files.Length == 0) return "📂 A pasta workspace/ está vazia.";

            var fileList = files.Select(Path.GetFileName);
            return $"📂 Arquivos na workspace/:\n- {string.Join("\n- ", fileList)}";
        }
        catch (Exception ex)
        {
            return $"❌ Erro ao listar arquivos: {ex.Message}";
        }
    }
}
