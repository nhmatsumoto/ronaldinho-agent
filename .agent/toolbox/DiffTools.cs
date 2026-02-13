namespace Ronaldinho.Toolbox;

public class DiffTools
{
    public struct DiffResult
    {
        public enum DiffType { Unchanged, Added, Deleted }
        public DiffType Type;
        public string Text;
    }

    public static async Task<List<DiffResult>> SimpleDiffAsync(string oldText, string newText)
    {
        return await PerformanceMonitor.MeasureAsync("SimpleDiff", () => Task.FromResult(SimpleDiffInternal(oldText, newText)));
    }

    private static List<DiffResult> SimpleDiffInternal(string oldText, string newText)
    {
        var results = new List<DiffResult>();
        var oldLines = oldText.Split('\n');
        var newLines = newText.Split('\n');

        int i = 0, j = 0;
        while (i < oldLines.Length || j < newLines.Length)
        {
            if (i < oldLines.Length && j < newLines.Length && oldLines[i] == newLines[j])
            {
                results.Add(new DiffResult { Type = DiffResult.DiffType.Unchanged, Text = oldLines[i] });
                i++; j++;
            }
            else if (j < newLines.Length && (i >= oldLines.Length || !oldLines.Contains(newLines[j])))
            {
                results.Add(new DiffResult { Type = DiffResult.DiffType.Added, Text = newLines[j] });
                j++;
            }
            else if (i < oldLines.Length)
            {
                results.Add(new DiffResult { Type = DiffResult.DiffType.Deleted, Text = oldLines[i] });
                i++;
            }
        }
        return results;
    }
}
