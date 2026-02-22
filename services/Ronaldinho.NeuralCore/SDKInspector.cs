using System;
using System.Reflection;
using System.Linq;
using Google.GenAI;

namespace Ronaldinho.NeuralCore
{
    public static class SDKInspector
    {
        public static void Inspect()
        {
            try
            {
                var type = typeof(global::Google.GenAI.Client);
                Console.WriteLine($"Type: {type.FullName}");
                
                Console.WriteLine("Constructors:");
                foreach (var ctor in type.GetConstructors())
                {
                    var pars = string.Join(", ", ctor.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($" - {ctor.DeclaringType.Name}({pars})");
                }

                Console.WriteLine("Properties:");
                foreach (var prop in type.GetProperties())
                {
                    Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                }

                var modelsProp = type.GetProperty("Models");
                if (modelsProp != null)
                {
                    var modelsType = modelsProp.PropertyType;
                    Console.WriteLine($"Models Type: {modelsType.FullName}");
                    
                    var genMethod = modelsType.GetMethods().FirstOrDefault(m => m.Name == "GenerateContentAsync" && m.GetParameters().Length == 4);
                    if (genMethod != null)
                    {
                        var responseType = genMethod.ReturnType.GenericTypeArguments[0];
                        Console.WriteLine($"Response Type: {responseType.FullName}");
                        var candidateType = responseType.GetProperty("Candidates").PropertyType.GenericTypeArguments[0];
                        Console.WriteLine($"Candidate Type: {candidateType.FullName}");
                        foreach (var prop in candidateType.GetProperties())
                        {
                            Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                        }
                        
                        var contentType = candidateType.GetProperty("Content").PropertyType;
                        Console.WriteLine($"Content Type: {contentType.FullName}");
                        foreach (var prop in contentType.GetProperties())
                        {
                            Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                        }

                        var partType = contentType.GetProperty("Parts").PropertyType.GenericTypeArguments[0];
                        Console.WriteLine($"Part Type: {partType.FullName}");
                        foreach (var prop in partType.GetProperties())
                        {
                            Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
