using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public static class ProviderConfigurationValidator
{
    private static readonly HashSet<string> InvalidPlaceholders = new(StringComparer.OrdinalIgnoreCase)
    {
        "placeholder",
        "placeholder_key",
        "changeme",
        "your_api_key_here"
    };

    public static string NormalizeSecret(string? value)
        => value?.Trim() ?? string.Empty;

    public static bool IsValidSecret(string? value)
    {
        var normalized = NormalizeSecret(value);
        return !string.IsNullOrWhiteSpace(normalized) && !InvalidPlaceholders.Contains(normalized);
    }

    public static Dictionary<string, ProviderDiagnostic> GetDiagnostics(IConfiguration configuration)
    {
        var diagnostics = new Dictionary<string, ProviderDiagnostic>(StringComparer.OrdinalIgnoreCase)
        {
            ["Gemini"] = Build("GEMINI_API_KEY", configuration["GEMINI_API_KEY"]),
            ["OpenAI"] = Build("OPENAI_API_KEY", configuration["OPENAI_API_KEY"]),
            ["Claude"] = Build("ANTHROPIC_API_KEY", configuration["ANTHROPIC_API_KEY"]),
            ["Nvidia"] = Build("NVIDIA_API_KEY", configuration["NVIDIA_API_KEY"]),
            ["OpenRouter"] = Build("OPENROUTER_API_KEY", configuration["OPENROUTER_API_KEY"]),
        };

        var preferred = configuration["LLM_PROVIDER"]?.Trim();
        if (!string.IsNullOrWhiteSpace(preferred) && diagnostics.TryGetValue(PreferredName(preferred), out var preferredDiag))
        {
            diagnostics[PreferredName(preferred)] = preferredDiag with
            {
                Ready = preferredDiag.Configured,
                Notes = preferredDiag.Configured ? "Preferred provider configured." : "Preferred provider invalid/missing key."
            };
        }

        return diagnostics;
    }

    public static string PreferredName(string provider)
        => provider.Trim().ToLowerInvariant() switch
        {
            "gemini" => "Gemini",
            "openai" => "OpenAI",
            "claude" => "Claude",
            "nvidia" => "Nvidia",
            "openrouter" => "OpenRouter",
            _ => provider
        };

    private static ProviderDiagnostic Build(string sourceKey, string? raw)
    {
        var normalized = NormalizeSecret(raw);

        if (string.IsNullOrWhiteSpace(normalized))
            return new ProviderDiagnostic(sourceKey, Configured: false, Ready: false, Notes: "Missing secret.");

        if (InvalidPlaceholders.Contains(normalized))
            return new ProviderDiagnostic(sourceKey, Configured: false, Ready: false, Notes: "Placeholder secret detected.");

        return new ProviderDiagnostic(sourceKey, Configured: true, Ready: true, Notes: "Credential loaded.");
    }
}

public record ProviderDiagnostic(string SourceKey, bool Configured, bool Ready, string Notes);
