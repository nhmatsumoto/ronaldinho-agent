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
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using DotNetEnv;
using System.Text.Json;
using Ronaldinho.Blockchain;
using Ronaldinho.P2P;
using Microsoft.AspNetCore.DataProtection;

namespace Ronaldinho.NeuralCore;

public record AgentSettingsDto(
    string GeminiApiKey,
    string OpenAIApiKey,
    string AnthropicApiKey,
    string NvidiaApiKey,
    string NvidiaModelId,
    string TelegramToken,
    string AiModel,
    string Personality,
    bool LocalPermissions,
    bool AutoFallback,
    bool SimultaneousLlm);

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

        string geminiKey = builder.Configuration["GEMINI_API_KEY"] ?? "";
        Console.WriteLine($"[*] Gemini API Key: {MaskKey(geminiKey)}");

        string openAIKey = builder.Configuration["OPENAI_API_KEY"] ?? "";
        Console.WriteLine($"[*] OpenAI API Key: {MaskKey(openAIKey)}");

        string anthropicKey = builder.Configuration["ANTHROPIC_API_KEY"] ?? "";
        Console.WriteLine($"[*] Anthropic API Key: {MaskKey(anthropicKey)}");

        string nvidiaKey = builder.Configuration["NVIDIA_API_KEY"] ?? "";
        Console.WriteLine($"[*] NVIDIA API Key: {MaskKey(nvidiaKey)}");

        string telegramToken = builder.Configuration["TELEGRAM_BOT_TOKEN"] ?? "";

        if (string.IsNullOrEmpty(telegramToken))
        {
            Console.WriteLine("❌ CRITICAL: Missing TELEGRAM_BOT_TOKEN");
            // Still proceed to boot the API so the UI can be used to set the token.
        }

        // 2. Load SOUL.md
        string dataDirName = builder.Configuration["DATA_DIR"] ?? "ronaldinho";
        string dataRoot = Path.Combine(rootPath, dataDirName);
        string soulPath = Path.Combine(dataRoot, "config", "SOUL.md");
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

        // --- KEYCLOAK OIDC AUTHENTICATION ---
        string authAuthority = builder.Configuration["AUTH_AUTHORITY"] ?? "http://localhost:8080/realms/ronaldinho";
        string authAudience = builder.Configuration["AUTH_AUDIENCE"] ?? "account";

        builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.Authority = authAuthority;
                options.RequireHttpsMetadata = true; // FORCE HTTPS ALWAYS FOR SECURITY
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateAudience = true,
                    ValidAudiences = new[] { authAudience, "configui-client" },
                    ValidateIssuer = true,
                    ValidIssuer = authAuthority
                };
            });

        builder.Services.AddAuthorization();

        // Add Security Services Early
        builder.Services.AddDataProtection();
        builder.Services.AddSingleton<ILocalKeyVault>(sp =>
            new LocalKeyVault(sp.GetRequiredService<IDataProtectionProvider>(), dataRoot));

        // Inject DB Vault Keys into IConfiguration
        // To avoid ASP0000 (BuildServiceProvider anti-pattern), we manually instantiate the KeyVault
        // for the early bootstrap phase.
        var dataProtectionProvider = Microsoft.AspNetCore.DataProtection.DataProtectionProvider.Create(
            new DirectoryInfo(Path.Combine(dataRoot, "data", "protection-keys")));
        var earlyVault = new LocalKeyVault(dataProtectionProvider, dataRoot);

        if (earlyVault.GetGlobalKey("GEMINI") is string gk) builder.Configuration["GEMINI_API_KEY"] = gk;
        if (earlyVault.GetGlobalKey("OPENAI") is string ok) builder.Configuration["OPENAI_API_KEY"] = ok;
        if (earlyVault.GetGlobalKey("ANTHROPIC") is string ak) builder.Configuration["ANTHROPIC_API_KEY"] = ak;
        if (earlyVault.GetGlobalKey("NVIDIA") is string nk) builder.Configuration["NVIDIA_API_KEY"] = nk;

        // 5. Initialize Core Services (singleton-like instantiations)
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
        if (!string.IsNullOrWhiteSpace(openAIKey))
        {
            var openAIStrategy = new OpenAIStrategy();
            var researchBuilder = Kernel.CreateBuilder();
            openAIStrategy.Configure(researchBuilder, builder.Configuration);
            _ = new ResearcherAgent(messageBus, researchBuilder.Build());
        }
        else
        {
            Console.WriteLine("[MCP] OpenAI key not configured. ResearcherAgent will stay offline.");
        }

        Console.WriteLine("[MCP] Booting SecuritySpecialistAgent with NvidiaStrategy...");
        if (!string.IsNullOrEmpty(nvidiaKey))
        {
            var nvidiaStrategy = new NvidiaStrategy();
            var securityBuilder = Kernel.CreateBuilder();
            nvidiaStrategy.Configure(securityBuilder, builder.Configuration);
            _ = new SecuritySpecialistAgent(messageBus, securityBuilder.Build());
        }
        // ===============================================

        // 9. Initialize Master Brain (NeuralOrchestrator)
        var memDiffService = new Ronaldinho.MemoryDiff.MemoryDiffService(Path.Combine(dataRoot, "data", "memorydiff"));
        var loggerFactory = builder.Services.BuildServiceProvider().GetRequiredService<ILoggerFactory>();
        var blockchainLogger = loggerFactory.CreateLogger<Chain>();
        var blockchain = new Chain(Path.Combine(dataRoot, "data", "chain.db"), blockchainLogger);

        var orchestrator = new NeuralOrchestrator(
            builder.Configuration, soul, rootPath, fileSystemSkill, textProcessingSkill, logAnalyzerSkill, codebaseDiffSkill, sessionRouter, memoryStore, messageBus, memDiffService, blockchain);

        // Wire Blockchain to P2P relay
        bool p2pInitiator = builder.Configuration["P2P_INITIATOR"] == "true";
        var p2pGateway = new P2PGateway(
            builder.Configuration["P2P_SIGNALING"] ?? "http://localhost:3000",
            builder.Configuration["P2P_LOCAL_ID"] ?? "peer-a",
            builder.Configuration["P2P_REMOTE_ID"] ?? "peer-b",
            p2pInitiator,
            orchestrator,
            builder.Services.BuildServiceProvider().GetRequiredService<ILoggerFactory>());

        blockchain.OnBlockAdded += async block =>
        {
            var json = JsonSerializer.Serialize(block);
            await p2pGateway.SendAsync("all", "blockchain_sync", json);
        };

        p2pGateway.RegisterHandler("blockchain_sync", async json =>
        {
            try
            {
                var block = JsonSerializer.Deserialize<Block>(json);
                if (block != null)
                {
                    blockchain.SyncBlocks(new List<Block> { block });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[P2P] Failed to sync block: {ex.Message}");
            }
        });

        // Build the ASP.NET Core Application
        var app = builder.Build();

        app.UseCors("AllowFrontend");
        app.UseAuthentication();
        app.UseAuthorization();

        // --- API ROUTES ---

        app.MapGet("/api/settings", async (HttpContext ctx) =>
        {
            var config = app.Services.GetRequiredService<IConfiguration>();
            var vault = app.Services.GetRequiredService<ILocalKeyVault>();

            var currentSoul = File.Exists(soulPath) ? await File.ReadAllTextAsync(soulPath) : "";

            var userSub = ctx.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userSub)) return Results.Unauthorized();

            return Results.Ok(new AgentSettingsDto(
                GeminiApiKey: vault.GetKey(userSub, "GEMINI") != null ? "VAULT_LOCKED_KEY" : "",
                OpenAIApiKey: vault.GetKey(userSub, "OPENAI") != null ? "VAULT_LOCKED_KEY" : "",
                AnthropicApiKey: vault.GetKey(userSub, "ANTHROPIC") != null ? "VAULT_LOCKED_KEY" : "",
                NvidiaApiKey: vault.GetKey(userSub, "NVIDIA") != null ? "VAULT_LOCKED_KEY" : "",
                NvidiaModelId: config["NVIDIA_MODEL_ID"] ?? "",
                TelegramToken: config["TELEGRAM_BOT_TOKEN"] ?? "",
                AiModel: config["LLM_PROVIDER"] ?? "gemini",
                Personality: currentSoul,
                LocalPermissions: config["ALLOW_LOCAL_TOOLS"] == "true",
                AutoFallback: config["ENABLE_AUTO_FALLBACK"] == "true",
                SimultaneousLlm: config["ENABLE_SIMULTANEOUS_LLM"] == "true"
            ));
        }).RequireAuthorization();

        app.MapPost("/api/settings", async (HttpContext ctx, [FromBody] AgentSettingsDto request) =>
        {
            var userSub = ctx.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userSub)) return Results.Unauthorized();

            Console.WriteLine($"[API] Saving new configurations for user ID: {userSub}...");

            var vault = app.Services.GetRequiredService<ILocalKeyVault>();

            // 0. Update Keys if provided and not just placeholder
            if (!string.IsNullOrEmpty(request.GeminiApiKey) && request.GeminiApiKey != "VAULT_LOCKED_KEY")
            {
                vault.SaveKey(userSub, "GEMINI", request.GeminiApiKey);
                app.Configuration["GEMINI_API_KEY"] = request.GeminiApiKey;
            }
            if (!string.IsNullOrEmpty(request.OpenAIApiKey) && request.OpenAIApiKey != "VAULT_LOCKED_KEY")
            {
                vault.SaveKey(userSub, "OPENAI", request.OpenAIApiKey);
                app.Configuration["OPENAI_API_KEY"] = request.OpenAIApiKey;
            }
            if (!string.IsNullOrEmpty(request.AnthropicApiKey) && request.AnthropicApiKey != "VAULT_LOCKED_KEY")
            {
                vault.SaveKey(userSub, "ANTHROPIC", request.AnthropicApiKey);
                app.Configuration["ANTHROPIC_API_KEY"] = request.AnthropicApiKey;
            }
            if (!string.IsNullOrEmpty(request.NvidiaApiKey) && request.NvidiaApiKey != "VAULT_LOCKED_KEY")
            {
                vault.SaveKey(userSub, "NVIDIA", request.NvidiaApiKey);
                app.Configuration["NVIDIA_API_KEY"] = request.NvidiaApiKey;
            }

            // 1. Update SOUL.md
            var dir = Path.GetDirectoryName(soulPath);
            if (dir != null && !Directory.Exists(dir)) Directory.CreateDirectory(dir);
            await File.WriteAllTextAsync(soulPath, request.Personality);

            // 2. Update .env
            var envDict = new Dictionary<string, string>();
            if (File.Exists(envPath))
            {
                foreach (var line in await File.ReadAllLinesAsync(envPath))
                {
                    var parts = line.Split('=', 2);
                    if (parts.Length == 2) envDict[parts[0]] = parts[1];
                }
            }

            envDict["TELEGRAM_BOT_TOKEN"] = request.TelegramToken;
            envDict["LLM_PROVIDER"] = request.AiModel;
            envDict["NVIDIA_MODEL_ID"] = request.NvidiaModelId;
            envDict["ALLOW_LOCAL_TOOLS"] = request.LocalPermissions ? "true" : "false";
            envDict["ENABLE_AUTO_FALLBACK"] = request.AutoFallback ? "true" : "false";
            envDict["ENABLE_SIMULTANEOUS_LLM"] = request.SimultaneousLlm ? "true" : "false";

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
        registry.AddGateway(p2pGateway);

        var cronEngine = new Ronaldinho.NeuralCore.Core.Automation.CronMissionEngine(rootPath, orchestrator, builder.Configuration);

        var cts = new CancellationTokenSource();
        // Fire and forget the background tasks
        _ = cronEngine.StartAsync(cts.Token);
        _ = registry.StartAllAsync(cts.Token);

        // Listen on configurable port (default 5000)
        var port = builder.Configuration["PORT"] ?? "5000";
        app.Urls.Add($"http://*:{port}");

        Console.WriteLine($"[System] Listening for API requests on http://*:{port}...");

        // blocks the main thread and runs the HTTP server
        await app.RunAsync(cts.Token);
    }

    private static string MaskKey(string key)
    {
        if (string.IsNullOrEmpty(key)) return "[NOT CONFIGURED]";
        if (key.Length <= 8) return "[SECURELY LOADED]";
        return $"{key[..4]}...{key[^4..]}";
    }
}
