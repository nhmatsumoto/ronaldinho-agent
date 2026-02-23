using System;
using System.Linq;

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
                    var declaringName = ctor.DeclaringType?.Name ?? "<unknown>";
                    Console.WriteLine($" - {declaringName}({pars})");
                }

                Console.WriteLine("Properties:");
                foreach (var prop in type.GetProperties())
                {
                    Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                }

                var modelsProp = type.GetProperty("Models");
                if (modelsProp == null)
                {
                    Console.WriteLine("Models property not found.");
                    return;
                }

                var modelsType = modelsProp.PropertyType;
                Console.WriteLine($"Models Type: {modelsType.FullName}");

                var genMethod = modelsType
                    .GetMethods()
                    .FirstOrDefault(m => m.Name == "GenerateContentAsync" && m.GetParameters().Length == 4);

                if (genMethod == null)
                {
                    Console.WriteLine("GenerateContentAsync overload not found.");
                    return;
                }

                var responseType = genMethod.ReturnType.GenericTypeArguments.FirstOrDefault();
                if (responseType == null)
                {
                    Console.WriteLine("Unable to infer response type from GenerateContentAsync.");
                    return;
                }

                Console.WriteLine($"Response Type: {responseType.FullName}");

                var candidatesProp = responseType.GetProperty("Candidates");
                var candidateType = candidatesProp?.PropertyType.GenericTypeArguments.FirstOrDefault();
                if (candidateType == null)
                {
                    Console.WriteLine("Candidates type not found.");
                    return;
                }

                Console.WriteLine($"Candidate Type: {candidateType.FullName}");
                foreach (var prop in candidateType.GetProperties())
                {
                    Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                }

                var contentProp = candidateType.GetProperty("Content");
                var contentType = contentProp?.PropertyType;
                if (contentType == null)
                {
                    Console.WriteLine("Content type not found.");
                    return;
                }

                Console.WriteLine($"Content Type: {contentType.FullName}");
                foreach (var prop in contentType.GetProperties())
                {
                    Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                }

                var partsProp = contentType.GetProperty("Parts");
                var partType = partsProp?.PropertyType.GenericTypeArguments.FirstOrDefault();
                if (partType == null)
                {
                    Console.WriteLine("Parts type not found.");
                    return;
                }

                Console.WriteLine($"Part Type: {partType.FullName}");
                foreach (var prop in partType.GetProperties())
                {
                    Console.WriteLine($" - {prop.PropertyType.Name} {prop.Name}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
