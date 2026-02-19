using Hangfire;
using Hangfire.Storage.SQLite;
using Microsoft.Extensions.DependencyInjection;
using Ronaldinho.Bridge;
using Telegram.Bot;
using System.Text.Json;

var builder = Host.CreateApplicationBuilder(args);

// 1. Load Secrets and find Root
var baseDir = AppContext.BaseDirectory;
while (!Directory.Exists(Path.Combine(baseDir, "workspace")) && Path.GetDirectoryName(baseDir) != null)
{
    baseDir = Path.GetDirectoryName(baseDir)!;
}

var secretsPath = Path.Combine(baseDir, "workspace", "data", "secrets", "telegram.json");
string token = "";

if (File.Exists(secretsPath))
{
    var secrets = JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(secretsPath));
    if (secrets != null && secrets.TryGetValue("token", out var t))
    {
        token = t;
    }
}

if (string.IsNullOrEmpty(token))
{
    Console.WriteLine("CRITICAL: Telegram Token not found in workspace/data/secrets/telegram.json");
}
else
{
    Console.WriteLine($"[*] Root Directory discovered: {baseDir}");
    Console.WriteLine($"[*] Telegram Token loaded successfully.");
}

// 2. Configure Services
builder.Services.AddSingleton<ITelegramBotClient>(new TelegramBotClient(token));
builder.Services.AddSingleton<IExchangeService, ExchangeService>();
builder.Services.AddTransient<TelegramJob>();

// 3. Configure Hangfire
var dbDir = Path.Combine(baseDir, "workspace", "data");
var dbPath = Path.Combine(dbDir, "bridge.db");
Directory.CreateDirectory(dbDir); // Ensure directory exists

builder.Services.AddHangfire(configuration => configuration
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UseSQLiteStorage(dbPath));

builder.Services.AddHangfireServer();

var host = builder.Build();

// 4. Schedule Recurring Job
using (var scope = host.Services.CreateScope())
{
    var recurringJobManager = scope.ServiceProvider.GetRequiredService<IRecurringJobManager>();
    recurringJobManager.AddOrUpdate<TelegramJob>(
        "telegram-polling",
        job => job.ExecuteAsync(),
        "*/10 * * * * *" // Every 10 seconds
    );
}

host.Run();
