using System.Text.Json;

namespace Ronaldinho.Bridge;

public interface IExchangeService
{
    Task WriteToInboxAsync(long userId, string text);
    Task<List<OutboxMessage>> ReadNewOutboxMessagesAsync();
    Task MarkAsSentAsync(string timestamp);
}

public class OutboxMessage
{
    public string ts { get; set; } = string.Empty;
    public long user_id { get; set; }
    public string text { get; set; } = string.Empty;
    public string action { get; set; } = string.Empty; // e.g., "typing"
    public bool sent { get; set; }
}

public class ExchangeService : IExchangeService
{
    private readonly string _inboxPath;
    private readonly string _outboxPath;

    public ExchangeService()
    {
        var baseDir = AppContext.BaseDirectory;
        while (!Directory.Exists(Path.Combine(baseDir, "ronaldinho")) && Path.GetDirectoryName(baseDir) != null)
        {
            baseDir = Path.GetDirectoryName(baseDir)!;
        }

        _inboxPath = Path.Combine(baseDir, "ronaldinho", "data", "telegram", "inbox.jsonl");
        _outboxPath = Path.Combine(baseDir, "ronaldinho", "data", "telegram", "outbox.jsonl");
        
        Directory.CreateDirectory(Path.GetDirectoryName(_inboxPath)!);
    }

    private readonly JsonSerializerOptions _jsonOptions = new() 
    { 
        NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowReadingFromString 
    };

    public async Task WriteToInboxAsync(long userId, string text)
    {
        var entry = new
        {
            ts = DateTime.UtcNow.ToString("O"),
            user_id = userId,
            text = text,
            processed = false
        };

        var json = JsonSerializer.Serialize(entry, _jsonOptions);
        await File.AppendAllLinesAsync(_inboxPath, new[] { json });
    }

    public async Task<List<OutboxMessage>> ReadNewOutboxMessagesAsync()
    {
        if (!File.Exists(_outboxPath)) return new List<OutboxMessage>();

        var messages = new List<OutboxMessage>();
        var lines = await File.ReadAllLinesAsync(_outboxPath);

        foreach (var line in lines)
        {
            try
            {
                var msg = JsonSerializer.Deserialize<OutboxMessage>(line, _jsonOptions);
                if (msg != null && !msg.sent)
                {
                    messages.Add(msg);
                }
            }
            catch { /* Ignore corrupt lines */ }
        }

        return messages;
    }

    public async Task MarkAsSentAsync(string timestamp)
    {
        if (!File.Exists(_outboxPath)) return;

        var lines = await File.ReadAllLinesAsync(_outboxPath);
        var updatedLines = new List<string>();

        foreach (var line in lines)
        {
            try
            {
                var msg = JsonSerializer.Deserialize<OutboxMessage>(line, _jsonOptions);
                if (msg != null && msg.ts == timestamp)
                {
                    msg.sent = true;
                }
                updatedLines.Add(JsonSerializer.Serialize(msg, _jsonOptions));
            }
            catch 
            {
                updatedLines.Add(line);
            }
        }

        await File.WriteAllLinesAsync(_outboxPath, updatedLines);
    }
}
