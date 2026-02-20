using System.Text.Json;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Ronaldinho.NeuralCore.Core;

namespace Ronaldinho.NeuralCore.Core.Automation;

public class CronJobConfig
{
    public string Id { get; set; } = string.Empty;
    public string ScheduleCron { get; set; } = string.Empty; // Format HH:mm
    public string ActionPayload { get; set; } = string.Empty;
    public bool Enabled { get; set; } = true;
    public DateTime? LastRun { get; set; }
}

public class CronMissionEngine : BackgroundService
{
    private readonly string _configPath;
    private readonly NeuralOrchestrator _orchestrator;
    private readonly string _adminTelegramId; // ID configured to receive pro-active notifications

    public CronMissionEngine(string rootPath, NeuralOrchestrator orchestrator, Microsoft.Extensions.Configuration.IConfiguration config) : base()
    {
        _configPath = Path.Combine(rootPath, "ronaldinho", "config", "automation.json");
        _orchestrator = orchestrator;
        _adminTelegramId = config["TELEGRAM_ADMIN_ID"] ?? "";
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Console.WriteLine("[Automation] CronMissionEngine initialized.");
        
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessCronJobsAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Automation] Timer loop error: {ex.Message}");
            }

            // Sleep for 30 seconds before checking time again
            await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
        }
    }

    private async Task ProcessCronJobsAsync()
    {
        if (!File.Exists(_configPath)) return;

        var json = await File.ReadAllTextAsync(_configPath);
        var jobs = JsonSerializer.Deserialize<List<CronJobConfig>>(json) ?? new List<CronJobConfig>();
        var nowString = DateTime.Now.ToString("HH:mm");
        var changed = false;

        foreach (var job in jobs)
        {
            if (!job.Enabled) continue;

            // Simple HH:mm matcher for now.
            if (job.ScheduleCron == nowString)
            {
                // Prevent duplicate runs in the same minute
                if (job.LastRun.HasValue && job.LastRun.Value.Date == DateTime.Now.Date && job.LastRun.Value.Hour == DateTime.Now.Hour && job.LastRun.Value.Minute == DateTime.Now.Minute)
                {
                    continue;
                }

                Console.WriteLine($"[Automation] Triggering Job '{job.Id}' Payload: {job.ActionPayload}");
                
                // If we know who the admin is, send them a proactive neural thought!
                if (!string.IsNullOrEmpty(_adminTelegramId) && long.TryParse(_adminTelegramId, out long adminId))
                {
                    // Fire and forget via Orchestrator to simulate a user prompting the system
                    _ = Task.Run(async () => {
                        try 
                        {
                            Console.WriteLine($"[Automation] Dispatching execution to admin '{adminId}'...");
                            // ProcessMessageAsync evaluates the payload and returns the string response
                            // To actually send back to Telegram, the strategy requires gateway awareness or dropping a file to outbox.
                            // For Autonomous operations, returning it directly helps log it.
                            
                            var context = _orchestrator.Router.Route("CronMissionEngine", "System", adminId.ToString());
                            var response = await _orchestrator.ProcessMessageAsync(context, $"[SYSTEM CRON AUTOMATION]: {job.ActionPayload}");
                            
                            Console.WriteLine($"[Automation] Thought result: {response}");
                        }
                        catch(Exception ex) 
                        {
                             Console.WriteLine($"[Automation] Process Error: {ex}");
                        }
                    });
                }
                else
                {
                    Console.WriteLine("[Automation] Missing TELEGRAM_ADMIN_ID in .env. Execution skipped.");
                }

                job.LastRun = DateTime.Now;
                changed = true;
            }
        }

        if (changed)
        {
            await File.WriteAllTextAsync(_configPath, JsonSerializer.Serialize(jobs, new JsonSerializerOptions { WriteIndented = true }));
        }
    }
}
