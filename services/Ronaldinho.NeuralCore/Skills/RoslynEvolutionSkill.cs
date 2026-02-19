using System.ComponentModel;
using System.Reflection;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Skills;

public class RoslynEvolutionSkill
{
    private readonly Kernel _kernel;
    private readonly string _rootPath;

    public RoslynEvolutionSkill(Kernel kernel, string rootPath)
    {
        _kernel = kernel;
        _rootPath = rootPath;
    }

    [KernelFunction, Description("Evolui o Ronaldinho criando uma nova habilidade nativa em C# em tempo de execução.")]
    public async Task<string> Evolve(
        [Description("Nome único para a nova habilidade (ex: MathPlugin)")] string pluginName,
        [Description("Código C# completo da classe. Deve ser uma classe simples com métodos anotados com [KernelFunction].")] string csharpCode)
    {
        await Task.CompletedTask; // Fix CS1998
        try
        {
            Console.WriteLine($"[Evolution] Criando plugin: {pluginName}...");

            // 1. Compilation setup
            var syntaxTree = CSharpSyntaxTree.ParseText(csharpCode);
            var assemblyName = $"Ronaldinho.Evolved.{pluginName}.{Guid.NewGuid():N}";

            var references = AppDomain.CurrentDomain.GetAssemblies()
                .Where(a => !a.IsDynamic && !string.IsNullOrWhiteSpace(a.Location))
                .Select(a => MetadataReference.CreateFromFile(a.Location))
                .Cast<MetadataReference>()
                .ToList();

            // Add SemanticKernel reference explicitly if needed
            references.Add(MetadataReference.CreateFromFile(typeof(KernelFunctionAttribute).Assembly.Location));

            var compilation = CSharpCompilation.Create(
                assemblyName,
                new[] { syntaxTree },
                references,
                new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));

            using var ms = new MemoryStream();
            var result = compilation.Emit(ms);

            if (!result.Success)
            {
                var failures = string.Join("\n", result.Diagnostics.Where(d => d.Severity == DiagnosticSeverity.Error).Select(d => d.GetMessage()));
                return $"❌ Erro de compilação na evolução:\n{failures}";
            }

            // 2. Load and Register
            ms.Seek(0, SeekOrigin.Begin);
            var assembly = Assembly.Load(ms.ToArray());
            var type = assembly.GetTypes().FirstOrDefault(t => t.IsClass);

            if (type == null) return "⚠️ Nenhuma classe encontrada no código fornecido.";

            var pluginInstance = Activator.CreateInstance(type);
            if (pluginInstance == null) return "⚠️ Não foi possível instanciar a classe da evolução.";

            _kernel.Plugins.AddFromObject(pluginInstance, pluginName);

            // 3. Persist the source for posterity (audit)
            string evolutionDir = Path.Combine(_rootPath, ".toolbox", "evolved_cs");
            Directory.CreateDirectory(evolutionDir);
            File.WriteAllText(Path.Combine(evolutionDir, $"{pluginName}.cs"), csharpCode);

            return $"🚀 EVOLUÇÃO CONCLUÍDA! Habilidade '{pluginName}' carregada nativamente e pronta para uso.";
        }
        catch (Exception ex)
        {
            return $"💥 Falha na evolução: {ex.Message}";
        }
    }
}
