using System.Text.RegularExpressions;

namespace Ronaldinho.Toolbox;

public static class SecurityGuard
{
    // Padrões de chaves de API comuns e PII
    private static readonly Regex _keyPattern = new Regex(@"(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36})", RegexOptions.Compiled);
    private static readonly Regex _emailPattern = new Regex(@"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    private static readonly Regex _ccPattern = new Regex(@"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b", RegexOptions.Compiled);
    
    private static readonly string[] _sensitiveKeywords = { "API_KEY", "SECRET", "PASSWORD", "TOKEN", "PWD", "CVC", "CVV" };

    public static string Sanitize(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;

        string sanitized = input;

        // 1. Redigir padrões conhecidos
        sanitized = _keyPattern.Replace(sanitized, "[REDACTED_API_KEY]");
        sanitized = _emailPattern.Replace(sanitized, "[REDACTED_EMAIL]");
        sanitized = _ccPattern.Replace(sanitized, "[REDACTED_CC]");

        // 2. Redigir valores sensíveis baseados em keywords
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
