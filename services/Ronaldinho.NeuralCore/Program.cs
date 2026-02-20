using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Ronaldinho.NeuralCore.Core;
using Ronaldinho.NeuralCore.Gateway;
using Ronaldinho.NeuralCore.Services.Strategies;
using Ronaldinho.NeuralCore.Services.MCP.Core;
using Ronaldinho.NeuralCore.Services.MCP.Agents;
using Ronaldinho.NeuralCore.Services;
using Google.Apis.Auth;
using DotNetEnv;
using System.Text.Json;

namespace Ronaldinho.NeuralCore;

public record AgentSettingsDto(string GeminiApiKey, string TelegramToken, string AiModel, string Personality, bool LocalPermissions);

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("⚽ RONALDINHO NEURAL CORE: MINIMAL API WEB SERVER STARTING ⚽");

        var builder = WebApplication.CreateBuilder(args);

        // 1. Load Environment (Root .env)
        var rootPath = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", ".."));
        var envPath = Path.Combine(rootPath, ".env");
        
        if (File.Exists(envPath))
        {
            Env.Load(envPath);
            Console.WriteLine("[System] Environment loaded from root .env");
        }
        
        // Build Configuration
        // Important: Add environment variables so we can read from .env
        builder.Configuration.AddEnvironmentVariables();
        
        string telegramToken = builder.Configuration["TELEGRAM_BOT_TOKEN"] ?? "";
        
        if (string.IsNullOrEmpty(telegramToken))
        {
            Console.WriteLine("❌ CRITICAL: Missing TELEGRAM_BOT_TOKEN");
            // Still proceed to boot the API so the UI can be used to set the token.
        }

        // 2. Load SOUL.md
        string soulPath = Path.Combine(rootPath, "ronaldinho", "config", "SOUL.md");
        string soul = File.Exists(soulPath) ? await File.ReadAllTextAsync(soulPath) : "MANDATO SUPREMO: Você é o Ronaldinho.";

        // --- Configure Web Services ---
        builder.Services.AddCors(options =>
        {
            options.AddPolicy("AllowFrontend",
                policy =>
                {
                    policy.WithOrigins("http://localhost:5173", "http://127.0.0.1:5173")
                          .AllowAnyHeader()
                          .AllowAnyMethod();
                });
        });

        // Add Security Services Early
        builder.Services.AddDataProtection();
        builder.Services.AddSingleton<ILocalKeyVault, LocalKeyVault>();
        
        // Inject DB Vault Keys into IConfiguration
        var earlyProvider = builder.Services.BuildServiceProvider();
        var earlyVault = earlyProvider.GetRequiredService<ILocalKeyVault>();
        
        if (earlyVault.GetGlobalKey("GEMINI") is string gk) builder.Configuration["GEMINI_API_KEY"] = gk;
        if (earlyVault.GetGlobalKey("OPENAI") is string ok) builder.Configuration["OPENAI_API_KEY"] = ok;
        if (earlyVault.GetGlobalKey("ANTHROPIC") is string ak) builder.Configuration["ANTHROPIC_API_KEY"] = ak;

        // 5. Initialize Core Services (singleton-like instantiations)
        var tokenStorage = new Services.Auth.TokenStorageService(rootPath);
        var googleAuth = new Services.Auth.GoogleAuthService(builder.Configuration, tokenStorage);
        var authSkill = new Services.Auth.AuthSkill(googleAuth);
        
        var fileSystemSkill = new Services.SuperToolbox.FileSystemSkill(rootPath);
        var textProcessingSkill = new Services.SuperToolbox.TextProcessingSkill();
        var logAnalyzerSkill = new Services.SuperToolbox.LogAnalyzerSkill(rootPath);
        var codebaseDiffSkill = new Services.SuperToolbox.CodebaseDiffSkill(rootPath);

        var sessionRouter = new Core.Memory.SessionRouter();
        var memoryStore = new Core.Memory.MemoryStore(rootPath);

        // 8. Initialize Multi-Agent Coordination Protocol (MCP)
        Console.WriteLine("[System] Initializing Multi-Agent Coordination Protocol (MCP)...");
        var messageBus = new InMemoryMessageBus();
        
        // ======= MULTI-MODEL LLM STRATEGY BINDING =======
        Console.WriteLine("[MCP] Booting CodeSpecialistAgent with ClaudeStrategy...");
        var claudeStrategy = new ClaudeStrategy();
        var codeBuilder = Kernel.CreateBuilder();
        claudeStrategy.Configure(codeBuilder, builder.Configuration);
        var codeAgent = new CodeSpecialistAgent(messageBus, codeBuilder.Build());

        Console.WriteLine("[MCP] Booting ResearcherAgent with OpenAIStrategy...");
        var openAIStrategy = new OpenAIStrategy();
        var researchBuilder = Kernel.CreateBuilder();
        openAIStrategy.Configure(researchBuilder, builder.Configuration);
        var researcherAgent = new ResearcherAgent(messageBus, researchBuilder.Build());
        // ===============================================

        // 9. Initialize Master Brain (NeuralOrchestrator)
        var orchestrator = new NeuralOrchestrator(
            builder.Configuration, soul, rootPath, authSkill, fileSystemSkill, textProcessingSkill, logAnalyzerSkill, codebaseDiffSkill, sessionRouter, memoryStore, messageBus);

        // Build the ASP.NET Core Application
        var app = builder.Build();

        app.UseCors("AllowFrontend");

        // --- API ROUTES ---
        
        // --- AUTH MIDDLEWARE HELPER ---
        async Task<GoogleJsonWebSignature.Payload?> ValidateGoogleToken(HttpContext context)
        {
            var authHeader = context.Request.Headers["Authorization"].FirstOrDefault();
            if (authHeader == null || !authHeader.StartsWith("Bearer ")) return null;
            
            var token = authHeader.Substring("Bearer ".Length).Trim();
            try
            {
                return await GoogleJsonWebSignature.ValidateAsync(token);
            }
            catch
            {
                return null;
            }
        }

        // --- API ROUTES ---
        
        app.MapGet("/api/settings", async (HttpContext ctx) => 
        {
            var payload = await ValidateGoogleToken(ctx);
            if (payload == null) return Results.Unauthorized();

            var config = app.Services.GetRequiredService<IConfiguration>();
            var vault = app.Services.GetRequiredService<ILocalKeyVault>();
            
            var currentSoul = File.Exists(soulPath) ? await File.ReadAllTextAsync(soulPath) : "";
            
            // Check if key exists in vault to return a placeholder indicator (boolean essentially, but typed as string for UI compatibility)
            var hasGeminiKey = vault.GetKey(payload.Subject, "GEMINI") != null ? "VAULT_LOCKED_KEY" : "";
            
            return Results.Ok(new AgentSettingsDto(
                GeminiApiKey: hasGeminiKey,
                TelegramToken: config["TELEGRAM_BOT_TOKEN"] ?? "",
                AiModel: config["LLM_PROVIDER"] ?? "gemini",
                Personality: currentSoul,
                LocalPermissions: config["ALLOW_LOCAL_TOOLS"] == "true"
            ));
        });

        app.MapPost("/api/settings", async (HttpContext ctx, [FromBody] AgentSettingsDto request) =>
        {
            var payload = await ValidateGoogleToken(ctx);
            if (payload == null) return Results.Unauthorized();

            Console.WriteLine($"[API] Saving new configurations for user: {payload.Email}...");
            
            // 0. Key Vault Savings
            var vault = app.Services.GetRequiredService<ILocalKeyVault>();
            if (!string.IsNullOrEmpty(request.GeminiApiKey) && request.GeminiApiKey != "VAULT_LOCKED_KEY")
            {
                 vault.SaveKey(payload.Subject, "GEMINI", request.GeminiApiKey);
                 Console.WriteLine("[Security] Gemini API Key encrypted and saved to LocalKeyVault.");
                 // Important: update live config so it takes effect immediately without full restart if possible
                 config["GEMINI_API_KEY"] = request.GeminiApiKey;
            }

            // 1. Update SOUL.md (Personality)
            var dir = Path.GetDirectoryName(soulPath);
            if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
            await File.WriteAllTextAsync(soulPath, request.Personality);

            // 2. Update .env (Global Options)
            var envDict = new Dictionary<string, string>();
            if (File.Exists(envPath))
            {
                foreach (var line in await File.ReadAllLinesAsync(envPath))
                {
                    var parts = line.Split('=', 2);
                    if (parts.Length == 2) envDict[parts[0]] = parts[1];
                }
            }
            
            // Do NOT save the Gemini Key to .env anymore.
            envDict["TELEGRAM_BOT_TOKEN"] = request.TelegramToken;
            envDict["LLM_PROVIDER"] = request.AiModel;
            envDict["ALLOW_LOCAL_TOOLS"] = request.LocalPermissions ? "true" : "false";

            var newEnvLines = envDict.Select(kv => $"{kv.Key}={kv.Value}");
            await File.WriteAllLinesAsync(envPath, newEnvLines);

            Console.WriteLine("[API] Configurations saved successfully.");
            return Results.Ok(new { message = "Settings updated successfully" });
        });

        // --- STARTUP BACKGROUND SERVICES ---
        
        var registry = new GatewayRegistry();
        if (!string.IsNullOrEmpty(telegramToken))
        {
            registry.AddGateway(new TelegramGateway(telegramToken, orchestrator));
        }
        
        var cronEngine = new Ronaldinho.NeuralCore.Core.Automation.CronMissionEngine(rootPath, orchestrator, builder.Configuration);
        
        var cts = new CancellationTokenSource();
        // Fire and forget the background tasks
        _ = cronEngine.StartAsync(cts.Token);
        _ = registry.StartAllAsync(cts.Token);

        // Listen on port 5000 (which is the backend exposed port in docker-compose)
        app.Urls.Add("http://*:5000");

        Console.WriteLine("[System] Listening for API requests on http://*:5000...");
        
        // This blocks the main thread and runs the HTTP server
        await app.RunAsync(cts.Token);
    }
}
