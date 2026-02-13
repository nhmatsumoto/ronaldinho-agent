using Ronaldinho.Daemon;

Console.WriteLine($"Current Dir: {Directory.GetCurrentDirectory()}");
Console.WriteLine($"Base Dir: {AppDomain.CurrentDomain.BaseDirectory}");

var builder = Host.CreateApplicationBuilder(args);
builder.Services.AddHostedService<Worker>();

var host = builder.Build();
host.Run();
