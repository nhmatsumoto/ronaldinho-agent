# Autenticação Keycloak OIDC e Armazenamento Seguro de Chaves (Key Vault)

## Visão Geral
A fim de suportar múltiplos usuários e uma federação de identidade mais robusta, o sistema integrará Autenticação via Keycloak (OpenID Connect) no frontend em vez de usar conexões OAuth diretas com provedores externos. Isso mantém a soberania dos dados de identidade e o mecanismo de "Local Key Vault" no C# Minimal API protegerá credenciais sensíveis.

## Fluxo de Autenticação e Armazenamento

```mermaid
sequenceDiagram
    participant Usuario
    participant Frontend (React)
    participant Backend (C# Minimal API)
    participant Local Key Vault
    participant Keycloak (IdP)

    Usuario->>Frontend (React): Inicia Login
    Frontend (React)->>Keycloak (IdP): Redireciona via OIDC
    Keycloak (IdP)-->>Frontend (React): Retorna Access Token / ID Token (JWT)
    Frontend (React)->>Backend (C# Minimal API): Envia Bearer Token nas requisições API
    Backend (C# Minimal API)->>Backend (C# Minimal API): Valida JWT contra o Realm do Keycloak
     Backend (C# Minimal API)-->>Frontend (React): Acesso Autorizado

    Note over Frontend (React), Local Key Vault: Fluxo de Armazenamento de API Keys
    Usuario->>Frontend (React): Insere API Key (ex: OpenAI)
    Frontend (React)->>Backend (C# Minimal API): POST /api/keys { provider, key }
    Backend (C# Minimal API)->>Local Key Vault: Criptografa a chave (AES-256 / DataProtection)
    Local Key Vault-->>Backend (C# Minimal API): Salva chave criptografada vinculada ao Usuário
    Backend (C# Minimal API)-->>Frontend (React): Confirmação de Sucesso
```

## Componentes Principais

* **Keycloak IdP**: Novo serviço Docker fornecendo gestão de usuários e identidades independentes.
* **Frontend (`oidc-client-ts` ou `react-oidc-context`)**: Tela inicial que redireciona ao Keycloak para autenticação antes de expor a interface.
* **Backend Validador (`Microsoft.AspNetCore.Authentication.JwtBearer`)**: Middleware em ASP.NET Core que valida tokens JWT emitidos pelo Keycloak em vez de assinar os do Google de forma manual.
* **Local Key Vault**: Um serviço C# (`ILocalKeyVault`) que utiliza o `Microsoft.AspNetCore.DataProtection` (ou criptografia forte equivalente) para armazenar as chaves de forma segura (em arquivo local criptografado ou SQLite), impedindo que as chaves fiquem em texto puro (.env).

## Benefícios
* **Segurança Aprimorada**: Chaves sensíveis de IA não ficam mais legíveis no disco.
* **Rastreabilidade**: Sabemos qual usuário configurou o agente.
* **Isolamento de Contexto**: Abre portas para cada usuário ter sua própria configuração e memória no agente.
