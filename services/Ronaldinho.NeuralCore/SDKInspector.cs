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
                    Console.WriteLine($" - {ctor}");
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
                    Console.WriteLine("Models Methods:");
                    foreach (var method in modelsType.GetMethods())
                    {
                        Console.WriteLine($" - {method.ReturnType.Name} {method.Name}({string.Join(", ", method.GetParameters().Select(p => p.ParameterType.Name))})");
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
