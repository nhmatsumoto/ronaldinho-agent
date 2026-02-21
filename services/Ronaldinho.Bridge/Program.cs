using Hangfire;
using Hangfire.Storage.SQLite;
using Microsoft.Extensions.DependencyInjection;
using Ronaldinho.Bridge;
using System.Text.Json;
using DotNetEnv;

var builder = Host.CreateApplicationBuilder(args);

// 1. Load Secrets and find Root
var baseDir = AppContext.BaseDirectory;
while (!Directory.Exists(Path.Combine(baseDir, "ronaldinho")) && Path.GetDirectoryName(baseDir) != null)
{
    baseDir = Path.GetDirectoryName(baseDir)!;
}

// Load Environment from root .env
var envPath = Path.Combine(baseDir, ".env");
if (File.Exists(envPath))
{
    DotNetEnv.Env.Load(envPath);
    Console.WriteLine("[*] Environment loaded from root .env");
}

var secretsPath = Path.Combine(baseDir, "ronaldinho", "data", "secrets", "telegram.json");
string token = "";

if (File.Exists(secretsPath))
{
    var secrets = JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(secretsPath));
    if (secrets != null && secrets.TryGetValue("token", out var t))
    {
        token = t;
    }
}

// Fallback to Environment Variable (consistency with NeuralCore)
if (string.IsNullOrEmpty(token))
{
    token = Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN") ?? "";
}

if (string.IsNullOrEmpty(token))
{
    Console.WriteLine("CRITICAL: Telegram Token not found in ronaldinho/data/secrets/telegram.json OR Environment Variable.");
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
var dbDir = Path.Combine(baseDir, "ronaldinho", "data");
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
        "*/1 * * * * *" // Every 1 second
    );
}

host.Run();
