using System;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.SuperToolbox;

/// <summary>
/// A native kernel plugin that provides safe local filesystem operations.
/// Restricted strictly to the workspace directory.
/// </summary>
public sealed class FileSystemSkill
{
    private readonly string _workspaceRoot;

    public FileSystemSkill(string workspaceRoot)
    {
        _workspaceRoot = workspaceRoot;
    }

    [KernelFunction, Description("Reads the content of a file from the local workspace.")]
    public async Task<string> ReadFileAsync(
        [Description("The relative path of the file to read, starting from the workspace root (e.g., 'task.md')")] string relativePath)
    {
        try
        {
            var fullPath = NormalizeAndValidatePath(relativePath);
            if (!File.Exists(fullPath)) return "Error: File not found.";
            
            return await File.ReadAllTextAsync(fullPath);
        }
        catch (Exception ex)
        {
            return $"Error reading file: {ex.Message}";
        }
    }

    [KernelFunction, Description("Writes text content to a file in the local workspace. Overwrites existing content.")]
    public async Task<string> WriteFileAsync(
        [Description("The relative path of the file to write (e.g., 'notes.txt')")] string relativePath,
        [Description("The text content to write into the file")] string content)
    {
        try
        {
            var fullPath = NormalizeAndValidatePath(relativePath);
            var directory = Path.GetDirectoryName(fullPath);
            if (directory != null && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            await File.WriteAllTextAsync(fullPath, content);
            return $"Success: Wrote {content.Length} characters to {relativePath}";
        }
        catch (Exception ex)
        {
            return $"Error writing file: {ex.Message}";
        }
    }

    [KernelFunction, Description("Searches for files in a directory matching a pattern.")]
    public string SearchFiles(
        [Description("The relative directory path to search in (use '.' for root)")] string relativeDirectory,
        [Description("The search pattern (e.g., '*.cs' or '*task*')")] string pattern = "*")
    {
        try
        {
            var searchDir = NormalizeAndValidatePath(relativeDirectory);
            if (!Directory.Exists(searchDir)) return "Error: Directory not found.";

            var files = Directory.GetFiles(searchDir, pattern, SearchOption.AllDirectories);
            
            // Map to relative paths for cleaner output
            var relativeFiles = files.Select(f => Path.GetRelativePath(_workspaceRoot, f)).ToArray();

            if (relativeFiles.Length == 0) return "No files found matching the pattern.";
            
            return string.Join("\n", relativeFiles);
        }
        catch (Exception ex)
        {
            return $"Error searching files: {ex.Message}";
        }
    }

    private string NormalizeAndValidatePath(string relativePath)
    {
        // Prevent directory traversal (e.g., ../../../etc/passwd)
        if (relativePath.Contains(".."))
            throw new UnauthorizedAccessException("Directory traversal is strictly forbidden in the SuperToolbox.");
        
        // Strip leading slashes to prevent root injection
        if (relativePath.StartsWith("/") || relativePath.StartsWith("\\"))
            relativePath = relativePath.Substring(1);

        var fullPath = Path.GetFullPath(Path.Combine(_workspaceRoot, relativePath));

        // Final sanity check
        if (!fullPath.StartsWith(Path.GetFullPath(_workspaceRoot), StringComparison.OrdinalIgnoreCase))
            throw new UnauthorizedAccessException("Access denied. Path is outside the authorized workspace.");

        return fullPath;
    }
}
