# Ronaldinho-Agent 🚀 (Level 6 Autonomy)

O Ronaldinho-Agent é um ecossistema de desenvolvimento autônomo, seguro e auto-evolutivo, projetado para operar como um serviço de background (Daemon) de alta performance.

## 🌟 Capacidades Atuais

- **Daemon Nativo (.NET 9)**: Opera 24/7 monitorando o workspace em segundo plano.
- **Multitasking Real**: Processa múltiplas missões simultaneamente usando a Task Parallel Library (TPL).
- **Inteligência Gemini L6**: Utiliza IA para análise de código, sugestão de refatoração e tomada de decisões arquiteturais.
- **Auto-Otimização**: Monitora a própria performance e cria missões para melhorar seus algoritmos internos.
- **Toolbox de Alta Performance**: Algoritmos nativos em C# para Busca, Diff e Ordenação, otimizados para grandes codebases.
- **Segurança L4 (SecurityGuard)**: Proteção ativa contra vazamento de chaves de API e sanitização automática de logs.

## 🛠️ Como Iniciar

### 1. Configuração de Credenciais
Crie ou edite o arquivo `.env` na raiz do projeto e adicione sua chave do Gemini:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### 2. Execução via Docker (Recomendado)
Para rodar em um ambiente isolado e seguro:
```bash
docker compose up -d --build
```

### 3. Execução Local (Desenvolvimento)
Se preferir rodar fora do Docker:
```bash
dotnet run --project .agent/daemon/Ronaldinho.Daemon.csproj
```

## 🎮 Como Usar

O Ronaldinho é orientado a **Missões**. Para dar uma ordem a ele, você interage com o arquivo de estado:

1. **Adicionar Missão**: Edite o arquivo `.agent/MISSION_STORE.toon` e adicione uma nova linha na tabela.
   - Exemplo: `| M-001 | Ajustar Layout Home | EM_PLANEJAMENTO | ALTA | Descrição da tarefa... |`
2. **Monitorar Progresso**:
   - **Logs de Performance**: Confira [.agent/PERFORMANCE_LOG.toon](file:///.agent/PERFORMANCE_LOG.toon) para ver o que ele está otimizando.
   - **Status do Projeto**: O arquivo `.agent/PROJECT_STATUS.toon` (se configurado) mostrará o progresso em tempo real.
3. **Auto-Evolução**: Fique de olho no `MISSION_STORE`. Você verá o Ronaldinho criando missões com o prefixo `M-OPT-` quando ele decidir que precisa se auto-otimizar.

---
*Ronaldinho-Agent: Onde a autonomia encontra a maestria técnica.*
