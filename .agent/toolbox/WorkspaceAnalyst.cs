using System.Text.RegularExpressions;

namespace Ronaldinho.Toolbox;

public static class WorkspaceAnalyst
{
    /// <summary>
    /// Calculates TF-IDF for a set of documents to find important keywords.
    /// </summary>
    public static Dictionary<string, double> CalculateTfidf(IEnumerable<string> docs, string targetDoc)
    {
        var allDocs = docs.ToList();
        var tf = GetTermFrequencies(targetDoc);
        var idf = GetInverseDocumentFrequencies(allDocs);
        
        var tfidf = new Dictionary<string, double>();
        foreach (var term in tf.Keys)
        {
            if (idf.ContainsKey(term))
            {
                tfidf[term] = tf[term] * idf[term];
            }
        }
        
        return tfidf.OrderByDescending(x => x.Value).Take(20).ToDictionary(x => x.Key, x => x.Value);
    }

    private static Dictionary<string, double> GetTermFrequencies(string doc)
    {
        var words = Regex.Matches(doc.ToLower(), @"\w+").Select(m => m.Value).Where(w => w.Length > 3);
        int total = words.Count();
        return words.GroupBy(w => w).ToDictionary(g => g.Key, g => (double)g.Count() / total);
    }

    private static Dictionary<string, double> GetInverseDocumentFrequencies(List<string> allDocs)
    {
        var terms = allDocs.SelectMany(d => Regex.Matches(d.ToLower(), @"\w+").Select(m => m.Value).Distinct());
        int totalDocs = allDocs.Count;
        return terms.GroupBy(t => t).ToDictionary(g => g.Key, g => Math.Log((double)totalDocs / g.Count()));
    }
}
