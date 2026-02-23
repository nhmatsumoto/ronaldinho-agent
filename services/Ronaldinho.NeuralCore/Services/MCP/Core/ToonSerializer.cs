using System.Text;
using System.Collections.Generic;

namespace Ronaldinho.NeuralCore.Services.MCP.Core;

/// <summary>
/// Serializes and deserializes objects to the Ronaldinho .toon format (Pipe-Table).
/// </summary>
public static class ToonSerializer
{
    public static string Serialize(string status, string agent, string data)
    {
        var sb = new StringBuilder();
        sb.AppendLine("| Key | Value |");
        sb.AppendLine("| --- | --- |");
        sb.AppendLine($"| Status | {status} |");
        sb.AppendLine($"| Agent | {agent} |");
        sb.AppendLine($"| Data | {data.Replace("\n", "<br/>")} |");
        return sb.ToString();
    }

    public static Dictionary<string, string> Deserialize(string toon)
    {
        var result = new Dictionary<string, string>();
        var lines = toon.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

        foreach (var line in lines)
        {
            if (!line.StartsWith("|") || line.Contains("---") || line.Contains("| Key |")) continue;

            var parts = line.Split('|', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length >= 2)
            {
                result[parts[0]] = parts[1].Replace("<br/>", "\n");
            }
        }

        return result;
    }
}
