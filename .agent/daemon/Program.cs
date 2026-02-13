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
app.UseDefaultFiles(); // Procura por index.html
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new Microsoft.Extensions.FileProviders.PhysicalFileProvider(Path.Combine(root, ".agent/dashboard")),
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

app.MapGet("/api/project", async () => {
    if (!File.Exists(projectInfoPath)) return Results.NotFound();
    using var fs = new FileStream(projectInfoPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
    using var reader = new StreamReader(fs);
    var content = await reader.ReadToEndAsync();
    return Results.Text(content, "text/plain");
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
