using System.Text.RegularExpressions;

namespace Ronaldinho.Toolbox;

public static class SecurityGuard
{
    // Padrões de chaves de API comuns
    private static readonly Regex _keyPattern = new Regex(@"(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36})", RegexOptions.Compiled);
    private static readonly string[] _sensitiveKeywords = { "API_KEY", "SECRET", "PASSWORD", "TOKEN", "PWD" };

    public static string Sanitize(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;

        string sanitized = input;

        // 1. Redigir padrões de chaves conhecidos
        sanitized = _keyPattern.Replace(sanitized, "[REDACTED_API_KEY]");

        // 2. Redigir valores sensíveis baseados em keywords (caso apareçam em logs estruturados)
        foreach (var keyword in _sensitiveKeywords)
        {
            var keywordRegex = new Regex($@"{keyword}\s*[:=]\s*[^\s,]+", RegexOptions.IgnoreCase);
            sanitized = keywordRegex.Replace(sanitized, $"{keyword}: [REDACTED]");
        }

        return sanitized;
    }

    public static bool ContainsSecret(string input)
    {
        return _keyPattern.IsMatch(input);
    }
}
