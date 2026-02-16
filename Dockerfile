# Estágio de Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copiar projeto e restaurar dependências
COPY [".agent/daemon/Ronaldinho.Daemon.csproj", ".agent/daemon/"]
RUN dotnet restore ".agent/daemon/Ronaldinho.Daemon.csproj"

# Copiar o restante e compilar
COPY . .
RUN dotnet publish ".agent/daemon/Ronaldinho.Daemon.csproj" -c Release -o /app/publish

# Estágio final: Runtime Linux
FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble
WORKDIR /app
COPY --from=build /app/publish .

# Garante que o diretório .agent e subpastas existam
RUN mkdir -p /workspace/.agent/dashboard

# Copiar os arquivos do frontend e metadados para o local esperado pelo daemon
COPY .agent/dashboard /workspace/.agent/dashboard
COPY .agent/specialists /workspace/.agent/specialists
COPY .agent/scripts /workspace/.agent/scripts
COPY .agent/*.toon /workspace/.agent/
COPY .env /app/.env

# Configurar variáveis de ambiente do ASP.NET
ENV ASPNETCORE_URLS=http://+:5000
EXPOSE 5000

# Reinserir PowerShell para compatibilidade de scripts legados
RUN apt-get update && apt-get install -y wget apt-transport-https software-properties-common && \
    wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && apt-get install -y powershell

ENTRYPOINT ["dotnet", "Ronaldinho.Daemon.dll"]
