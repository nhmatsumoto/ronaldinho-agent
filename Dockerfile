# Estágio de Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copiar projeto e restaurar dependências
COPY [".agent/daemon/Ronaldinho.Daemon.csproj", ".agent/daemon/"]
RUN dotnet restore ".agent/daemon/Ronaldinho.Daemon.csproj"

# Copiar o restante e compilar
COPY . .
RUN dotnet publish ".agent/daemon/Ronaldinho.Daemon.csproj" -c Release -o /app/publish

# Estágio de Runtime
FROM mcr.microsoft.com/dotnet/runtime:9.0 AS final
WORKDIR /app

# Instalar PowerShell para compatibilidade com scripts legados
RUN apt-get update && apt-get install -y \
    powershell \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/publish .

# Criar usuário não-root
RUN useradd -m ronaldinho
USER ronaldinho

# O workspace será montado aqui
WORKDIR /workspace

ENTRYPOINT ["dotnet", "Ronaldinho.Daemon.dll"]
