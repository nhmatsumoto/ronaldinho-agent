FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy all csproj files to allow proper restore
COPY ["services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj", "services/Ronaldinho.NeuralCore/"]
COPY ["services/Ronaldinho.Contracts/Ronaldinho.Contracts.csproj", "services/Ronaldinho.Contracts/"]
COPY ["services/Ronaldinho.Blockchain/Ronaldinho.Blockchain.csproj", "services/Ronaldinho.Blockchain/"]
COPY ["services/Ronaldinho.MemoryDiff/Ronaldinho.MemoryDiff.csproj", "services/Ronaldinho.MemoryDiff/"]
COPY ["services/Ronaldinho.P2P/Ronaldinho.P2P.csproj", "services/Ronaldinho.P2P/"]

RUN dotnet restore "services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"

# Copy full source and build
COPY . .
WORKDIR "/src/services/Ronaldinho.NeuralCore"
RUN dotnet build "Ronaldinho.NeuralCore.csproj" -c Release -o /app/build

# Publish
FROM build AS publish
RUN dotnet publish "Ronaldinho.NeuralCore.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final Image
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# The app searches for .env around 5 directories up from AppContext.BaseDirectory
# Inside Docker, AppContext.BaseDirectory is /app, so 5 dirs up is /
# We'll map the configuration to / inside docker-compose
ENTRYPOINT ["dotnet", "Ronaldinho.NeuralCore.dll"]
