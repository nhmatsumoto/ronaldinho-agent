# Ronaldinho-Agent 🚀 (Python Edition)

> [!IMPORTANT]
> **Pivô para Python**: O projeto migrou de .NET/C# para um ecossistema **100% Python**. Esta mudança foi estratégica para permitir uma integração nativa com ferramentas agentic avançadas (terminal, editor) e aproveitar o ecossistema de IA em rápida evolução.

Ronaldinho-Agent é um ecossistema de engenharia autônoma composto por:

- **Python NeuralCore**: O cérebro orquestrador (FastAPI + PydanticAI).
- **Python Bridge**: Integração com Telegram.
- **ConfigUI**: Interface de governança em React.

## 🧠 Arquitetura e Fluxo de Agente

O Ronaldinho agora opera com um loop de raciocínio que permite o uso de ferramentas do sistema de forma autônoma.

```mermaid
graph TD
    User([Usuário]) --> Bridge[Bridge Telegram]
    Bridge --> Core[NeuralCore Python]

    subgraph "Reasoning Loop (PydanticAI)"
        Core --> Planner[Planejamento]
        Planner --> Tools{Chamada de Ferramentas}
        Tools --> Terminal[Execução de Shell]
        Tools --> Editor[Edição de Código]
        Terminal --> Result[Resultado da Ação]
        Editor --> Result
        Result --> Core
    end

    Core --> FinalResp([Resposta Final])
    FinalResp --> Bridge
```

## 💾 Memória Evolutiva (Git-Backed)

O conhecimento do Ronaldinho não é apenas salvo; ele **evolui**. Inspirado no sistema de controle de versão Git, cada aprendizado significativo ou mudança de estado é registrado como um commit imutável.

- **Rastreabilidade**: Todo o histórico de "pensamentos" e ajustes de personalidade pode ser auditado.
- **Rollback de Conhecimento**: Capacidade de retornar a estados anteriores de consciência em caso de "alucinações" persistentes.

```mermaid
gitGraph
    commit id: "Personalidade Base"
    commit id: "Aprendizado: FastAPI"
    branch feature/autonomia
    checkout feature/autonomia
    commit id: "Ferramenta: Terminal"
    commit id: "Ferramenta: Editor"
    checkout main
    merge feature/autonomia
    commit id: "Ronaldinho Fenomenal v2"
```

## ⛓️ Inteligência Distribuída & Blockchain

O Ronaldinho não está sozinho. O projeto visa criar uma rede de agentes descentralizada onde o conhecimento é validado e compartilhado via **Blockchain**.

- **Consenso de Conhecimento**: Agentes em diferentes nós validam informações antes de integrá-las à memória coletiva.
- **D-AI (Decentralized AI)**: Uma infraestrutura onde o poder de processamento e o conhecimento são distribuídos, eliminando pontos únicos de falha.

```mermaid
graph LR
    subgraph "Nó 1 (Brasil)"
        A1[Agente A] <--> L1[(Local Ledger)]
    end
    subgraph "Nó 2 (Japão)"
        A2[Agente B] <--> L2[(Local Ledger)]
    end
    subgraph "Nó 3 (Europa)"
        A3[Agente C] <--> L3[(Local Ledger)]
    end

    L1 <--> BC{Blockchain Network}
    L2 <--> BC
    L3 <--> BC

    BC -- "Sincronização de Conhecimento" --> L1
    BC -- "Sincronização de Conhecimento" --> L2
    BC -- "Sincronização de Conhecimento" --> L3
```

## 🌐 Componentes do Ecossistema

O sistema é modular e utiliza protocolos modernos para garantir resiliência e autonomia.

```mermaid
graph LR
    subgraph Services
        NC[NeuralCore]
        B[Bridge]
        UI[ConfigUI]
    end

    subgraph Infrastructure
        D[Docker Compose]
        K[Keycloak Auth]
        S[Signaling Server]
    end

    NC <--> B
    NC <--> UI
    UI <--> K
    NC <--> S
    D -.-> NC
    D -.-> B
    D -.-> UI
```

## 🛠️ Quick Local Start

### 1. Pré-requisitos

- **Python 3.10+**
- **Node.js 18+**
- **Docker**

### 2. Configuração

Crie o arquivo `.env` na raiz baseado no exemplo.

### 3. Lançamento Unificado

O projeto utiliza um script central para subir todos os serviços:

```bash
chmod +x start_ronaldinho.sh
./start_ronaldinho.sh
```

## 🐳 Stack Docker

Para um ambiente isolado e completo:

```bash
docker compose up -d --build
```

## 📂 Estrutura do Repositório

```text
.
├── services/
│   ├── core/                # IA, Orquestração e Ferramentas (FastAPI)
│   ├── bridge/              # Bridge Telegram (Python)
│   └── ui/                  # Interface de Governança (React)
├── ronaldinho/              # Soul & Configurações
├── docker-compose.yml       # Stack Unificada
└── start_ronaldinho.sh      # Launcher Unificado
```

License: **MIT**
