namespace Ronaldinho.Toolbox;

public static class SortTools
{
    public static List<string> FastSort(IEnumerable<string> items)
    {
        return items.OrderBy(x => x, StringComparer.Ordinal).ToList();
    }
}
