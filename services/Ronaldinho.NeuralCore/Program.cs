using Microsoft.Extensions.Configuration;
using Ronaldinho.NeuralCore.Core;
using Ronaldinho.NeuralCore.Gateway;
using Ronaldinho.NeuralCore.Services.Strategies;
using DotNetEnv;

namespace Ronaldinho.NeuralCore;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("⚽ RONALDINHO NEURAL CORE: REVOLUTION STARTING ⚽");

        // 1. Load Environment (Root .env)
        var rootPath = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", ".."));
        var envPath = Path.Combine(rootPath, ".env");
        
        if (File.Exists(envPath))
        {
            Env.Load(envPath);
            Console.WriteLine("[System] Environment loaded from root .env");
        }
        else
        {
            Console.WriteLine($"[Warning] .env not found at {envPath}");
        }

        // Build Configuration for Strategy Pattern
        var configuration = new ConfigurationBuilder()
            .AddEnvironmentVariables()
            .Build();

        string telegramToken = configuration["TELEGRAM_BOT_TOKEN"] ?? "";

        if (string.IsNullOrEmpty(telegramToken))
        {
            Console.WriteLine("❌ CRITICAL: Missing TELEGRAM_BOT_TOKEN");
            return;
        }

        // 2. Load SOUL.md
        string soulPath = Path.Combine(rootPath, "ronaldinho", "config", "SOUL.md");
        string soul = File.Exists(soulPath) ? await File.ReadAllTextAsync(soulPath) : "MANDATO SUPREMO: Você é o Ronaldinho.";
        Console.WriteLine("[System] Ronaldinho's Soul loaded.");

        // 3. Initialize Brain (NeuralOrchestrator) with Configuration
        var orchestrator = new NeuralOrchestrator(configuration, soul, rootPath);

        // 4. Initialize Gateway (Telegram)
        var gateway = new TelegramGateway(telegramToken, orchestrator);

        // 5. Start the Game
        Console.WriteLine("[System] Ronaldinho is entering the field...");
        await gateway.StartAsync();
    }
}
