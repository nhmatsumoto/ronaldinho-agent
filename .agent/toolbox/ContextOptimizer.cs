namespace Ronaldinho.Toolbox;

public static class ContextOptimizer
{
    private const int MaxTokens = 120000; // Example for Gemini 1.5 Pro

    /// <summary>
    /// Estimates token count and suggests truncation points.
    /// </summary>
    public static (int Estimate, bool NeedsTruncation) AnalyzeContext(string fullContext)
    {
        // Rough estimation: 4 chars per token
        int estimate = fullContext.Length / 4;
        return (estimate, estimate > (MaxTokens * 0.9));
    }

    /// <summary>
    /// Summarizes or truncates context to fit window.
    /// </summary>
    public static string Optimize(string context, int targetTokens)
    {
        int currentEstimate = context.Length / 4;
        if (currentEstimate <= targetTokens) return context;

        // Truncate oldest (start of string) - keep last N chars
        int charsToKeep = targetTokens * 4;
        if (charsToKeep >= context.Length) return context;
        
        return "... [TRUNCATED] ... " + context.Substring(context.Length - charsToKeep);
    }
}
