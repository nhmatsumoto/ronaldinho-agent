FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy all csproj files to allow proper restore
COPY ["services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj", "services/Ronaldinho.Bridge/"]
COPY ["services/Ronaldinho.Contracts/Ronaldinho.Contracts.csproj", "services/Ronaldinho.Contracts/"]

RUN dotnet restore "services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj"

# Copy full source and build
COPY . .
WORKDIR "/src/services/Ronaldinho.Bridge"
RUN dotnet build "Ronaldinho.Bridge.csproj" -c Release -o /app/build

# Publish
FROM build AS publish
RUN dotnet publish "Ronaldinho.Bridge.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final Image
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# The app searches for .env in the root. 
# We'll map the configuration to / in docker-compose
ENTRYPOINT ["dotnet", "Ronaldinho.Bridge.dll"]
