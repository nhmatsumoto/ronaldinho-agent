using System.Text.RegularExpressions;

namespace Ronaldinho.Toolbox;

public static class SearchTools
{
    public static async Task<IEnumerable<int>> FindPatternAsync(string content, string pattern, bool isRegex = false)
    {
        return await PerformanceMonitor.MeasureAsync("FindPattern", () => Task.FromResult(FindPatternInternal(content, pattern, isRegex)));
    }

    private static IEnumerable<int> FindPatternInternal(string content, string pattern, bool isRegex = false)
    {
        if (isRegex)
        {
            return Regex.Matches(content, pattern).Cast<Match>().Select(m => m.Index);
        }

        var results = new List<int>();
        int index = content.IndexOf(pattern, StringComparison.Ordinal);
        while (index != -1)
        {
            results.Add(index);
            index = content.IndexOf(pattern, index + pattern.Length, StringComparison.Ordinal);
        }
        return results;
    }

    public static async Task<IEnumerable<string>> FindLinesWithPatternAsync(string filePath, string pattern)
    {
        return await PerformanceMonitor.MeasureAsync($"SearchLines:{Path.GetFileName(filePath)}", () => {
            if (!File.Exists(filePath)) return Task.FromResult(Enumerable.Empty<string>());
            
            var lines = File.ReadLines(filePath)
                .Where(line => line.Contains(pattern, StringComparison.OrdinalIgnoreCase))
                .ToList();
            return Task.FromResult((IEnumerable<string>)lines);
        });
    }
}
