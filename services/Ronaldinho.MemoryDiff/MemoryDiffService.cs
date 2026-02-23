using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using JsonDiffPatchDotNet;

namespace Ronaldinho.MemoryDiff
{
    /// <summary>
    /// Service responsible for persisting commits, generating diffs, and retrieving history.
    /// Commits are stored as JSON files under `data/memorydiff/commits/`.
    /// Diffs are stored as JSON files under `data/memorydiff/diffs/`.
    /// </summary>
    public class MemoryDiffService
    {
        private readonly string _basePath;
        private readonly string _commitsPath;
        private readonly string _diffsPath;
        private readonly JsonDiffPatch _jdp = new();

        public MemoryDiffService(string basePath = "data/memorydiff")
        {
            _basePath = Path.GetFullPath(basePath);
            _commitsPath = Path.Combine(_basePath, "commits");
            _diffsPath = Path.Combine(_basePath, "diffs");
            Directory.CreateDirectory(_commitsPath);
            Directory.CreateDirectory(_diffsPath);
        }

        /// <summary>
        /// Saves a new commit and returns its identifier.
        /// </summary>
        public string SaveCommit(object knowledgeState)
        {
            var commit = new Commit(knowledgeState);
            var filePath = Path.Combine(_commitsPath, $"{commit.Id}.json");
            File.WriteAllText(filePath, commit.DataJson);
            return commit.Id;
        }

        /// <summary>
        /// Loads a commit by its identifier.
        /// </summary>
        public Commit LoadCommit(string commitId)
        {
            var filePath = Path.Combine(_commitsPath, $"{commitId}.json");
            if (!File.Exists(filePath))
                throw new FileNotFoundException($"Commit {commitId} not found.");
            var json = File.ReadAllText(filePath);
            var data = JsonConvert.DeserializeObject<object>(json);
            return new Commit(data) { Id = commitId, DataJson = json };
        }

        /// <summary>
        /// Generates a diff (JSON‑Patch) between two commits and persists it.
        /// </summary>
        public Diff GenerateDiff(string fromCommitId, string toCommitId)
        {
            var fromCommit = LoadCommit(fromCommitId);
            var toCommit = LoadCommit(toCommitId);

            var fromJ = JToken.Parse(fromCommit.DataJson);
            var toJ = JToken.Parse(toCommit.DataJson);
            var patch = _jdp.Diff(fromJ, toJ) ?? JValue.CreateNull();

            var diff = new Diff(fromCommitId, toCommitId, patch);
            var diffPath = Path.Combine(_diffsPath, $"{fromCommitId}_to_{toCommitId}.json");
            File.WriteAllText(diffPath, patch.ToString(Formatting.Indented));
            return diff;
        }

        /// <summary>
        /// Retrieves a previously generated diff.
        /// </summary>
        public Diff LoadDiff(string fromCommitId, string toCommitId)
        {
            var diffPath = Path.Combine(_diffsPath, $"{fromCommitId}_to_{toCommitId}.json");
            if (!File.Exists(diffPath))
                throw new FileNotFoundException($"Diff from {fromCommitId} to {toCommitId} not found.");
            var patch = JToken.Parse(File.ReadAllText(diffPath));
            return new Diff(fromCommitId, toCommitId, patch);
        }

        /// <summary>
        /// Returns a list of all commit identifiers in chronological order based on file creation time.
        /// </summary>
        public IEnumerable<string> ListCommits()
        {
            return new DirectoryInfo(_commitsPath).GetFiles("*.json")
                .OrderBy(f => f.CreationTimeUtc)
                .Select(f => Path.GetFileNameWithoutExtension(f.Name));
        }
    }
}
