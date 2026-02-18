using Ronaldinho.Daemon;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using System.IO;

var builder = WebApplication.CreateBuilder(args);

// Configuração do ambiente e root
string root = Directory.Exists("/workspace") ? "/workspace" : Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));
string missionStorePath = Path.Combine(root, ".agent/MISSION_STORE.toon");
string projectInfoPath = Path.Combine(root, ".agent/PROJECT_INFO.toon");

// Configura o Kestrel para ouvir em todas as interfaces na porta 5000
builder.WebHost.ConfigureKestrel(serverOptions =>
{
    serverOptions.ListenAnyIP(5000);
});

// Registrar serviços
builder.Services.AddHostedService<Worker>();
builder.Services.AddCors(options => options.AddPolicy("AllowAll", p => p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

app.UseCors("AllowAll");

var dashboardPath = Path.Combine(root, ".agent/dashboard");
Console.WriteLine($"Serving dashboard from: {dashboardPath}");

var fileProvider = new Microsoft.Extensions.FileProviders.PhysicalFileProvider(dashboardPath);
app.UseDefaultFiles(new DefaultFilesOptions
{
    FileProvider = fileProvider,
    RequestPath = ""
});
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = fileProvider,
    RequestPath = ""
});

// API Endpoints
app.MapGet("/api/missions", async () => {
    if (!File.Exists(missionStorePath)) return Results.NotFound();
    using var fs = new FileStream(missionStorePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
    using var reader = new StreamReader(fs);
    var content = await reader.ReadToEndAsync();
    return Results.Text(content, "text/plain");
});

app.MapGet("/api/logs", async () => {
    string logsRoot = Path.Combine(root, "logs/runs");
    if (!Directory.Exists(logsRoot)) return Results.Text("");

    // Busca o diretório de data mais recente
    var lastDateDir = Directory.GetDirectories(logsRoot)
        .OrderByDescending(d => d)
        .FirstOrDefault();

    if (lastDateDir == null) return Results.Text("");

    // Busca todos os arquivos .jsonl do dia e concatena os últimos
    var logFiles = Directory.GetFiles(lastDateDir, "*.jsonl")
        .OrderByDescending(f => File.GetLastWriteTime(f))
        .Take(5); // Pega os 5 arquivos de log mais recentes

    var allContent = new List<string>();
    foreach (var file in logFiles)
    {
        using var fs = new FileStream(file, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        using var reader = new StreamReader(fs);
        allContent.Add(await reader.ReadToEndAsync());
    }

    return Results.Text(string.Join("\n", allContent), "text/plain");
});

app.MapGet("/api/finance", () => {
    // Simulação usando o novo FinancialEngine
    double npv = Ronaldinho.Toolbox.FinancialEngine.CalculateNPV(0.1, new double[] { -1000, 400, 500, 600 });
    double roi = Ronaldinho.Toolbox.FinancialEngine.CalculateROI(1500, 1000);
    
    return Results.Json(new { 
        npv = Math.Round(npv, 2), 
        roi = Math.Round(roi * 100, 2) + "%", 
        health = "SAUDÁVEL" 
    });
});

app.MapGet("/api/project", async () => {
    if (!File.Exists(projectInfoPath)) return Results.NotFound();
    using var fs = new FileStream(projectInfoPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
    using var reader = new StreamReader(fs);
    var content = await reader.ReadToEndAsync();
    return Results.Text(content, "text/plain");
});

app.MapPost("/api/chat", async (HttpRequest request) => {
    using var reader = new StreamReader(request.Body);
    var message = await reader.ReadToEndAsync();
    
    // Gera uma nova missão baseada no chat
    string missionId = $"M-CHAT-{DateTime.Now:fff}";
    string missionLine = $"| {missionId} | {message} | EM_EXECUCAO | Orquestrador |";
    
    await File.AppendAllTextAsync(missionStorePath, "\n" + missionLine);
    return Results.Ok(new { status = "Mission Created", id = missionId });
});

app.MapPost("/api/project", async (HttpRequest request) => {
    using var bodyReader = new StreamReader(request.Body);
    var newDescription = await bodyReader.ReadToEndAsync();
    
    // Atualiza o PROJECT_INFO.toon
    string[] lines;
    using (var fs = new FileStream(projectInfoPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
    using (var reader = new StreamReader(fs)) {
        var content = await reader.ReadToEndAsync();
        lines = content.Split(new[] { Environment.NewLine, "\n" }, StringSplitOptions.None);
    }

    for (int i = 0; i < lines.Length; i++) {
        if (lines[i].Contains("| Description |")) {
            lines[i] = $"| Description | {newDescription} |";
            break;
        }
    }

    using (var fs = new FileStream(projectInfoPath, FileMode.Create, FileAccess.Write, FileShare.ReadWrite))
    using (var writer = new StreamWriter(fs)) {
        await writer.WriteAsync(string.Join("\n", lines));
    }

    return Results.Ok();
});

app.Run();
