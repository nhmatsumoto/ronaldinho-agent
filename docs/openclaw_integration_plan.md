# Plano de Implementação — Integração de padrões OpenClaw no Ronaldinho

## 0) Contexto e limitação desta análise

Este documento foi construído com análise **profunda do Ronaldinho** + tentativa de inspeção dos repositórios `openclaw` no GitHub.

### Comandos executados para inspeção externa
- `curl -s https://api.github.com/users/openclaw/repos?per_page=100 | python ...`
- `curl -s -H 'User-Agent: codex' https://api.github.com/users/openclaw/repos?per_page=100 | head`
- `curl -I https://github.com -m 10`

### Resultado
O ambiente bloqueou acesso ao GitHub (`CONNECT tunnel failed, response 403`), então **não foi possível ler os repositórios remotos do OpenClaw** nesta execução.

---

## 1) Estado atual do Ronaldinho (base para o plano)

### 1.1 Camada de LLM e fallback
- O `LLMStrategyFactory` já seleciona providers por credencial válida e prioriza `LLM_PROVIDER`.
- Providers atuais no fallback: Gemini, OpenAI, Claude, Nvidia, OpenRouter.
- O fallback pode ficar vazio e o orquestrador já responde mensagem operacional segura.

### 1.2 Camada de segurança/diagnóstico
- Existe `ProviderConfigurationValidator` para normalização/validação de segredo e diagnóstico (`Configured`, `Ready`, `Notes`).
- Endpoint autenticado `/api/providers/diagnostics` já expõe o status sanitizado dos providers.

### 1.3 Camada de canais (Telegram)
- O `TelegramGateway` já protege erro técnico com mensagem amigável + `correlationId`.
- Ainda há erro genérico para casos não classificados (o que pode reduzir observabilidade de operação).

### 1.4 Camada MCP (agentes especialistas)
- O orquestrador agora consulta especialistas com `QuerySpecialistAsync` e degradação segura quando agente está offline/timeout.
- Existe agente `configops` para diagnóstico de providers via MCP.

---

## 2) O que precisamos absorver do OpenClaw (modelo alvo)

> Como o acesso externo falhou, o alvo abaixo é definido por hipóteses operacionais típicas de plataformas de IA open-source maduras e deve ser confirmado assim que houver acesso aos repositórios `openclaw`.

### 2.1 Capacidades esperadas para benchmark
1. **Provider abstraction robusta**: contrato único para prompt/chat/streaming/tools.
2. **Policy engine de roteamento**: seleção por custo, latência, taxa de erro, contexto e criticidade.
3. **Telemetria de execução ponta a ponta**: tracing por requisição com correlação entre canal, orquestrador e provider.
4. **Circuit breaker + retry policy**: por provider/modelo, com cooldown dinâmico.
5. **Modo canário/A-B**: comparar modelos sem afetar estabilidade geral.
6. **Suite de testes de confiabilidade**: caos controlado (timeouts, 429, 5xx, quota, key inválida).

---

## 3) Gaps do Ronaldinho para atingir nível “OpenClaw-ready”

1. **Ausência de telemetria estruturada unificada** (hoje logs `Console.WriteLine` predominam).
2. **Fallback sem score dinâmico por SLA** (seleção ainda é majoritariamente estática por ordem/config).
3. **Sem circuito de saúde persistente por provider/modelo** (estado de degradação não é compartilhado).
4. **Sem suíte automatizada de resiliência** para casos de erro de provider no pipeline completo.
5. **Configuração com parsing manual de `.env`** no `Program.cs` (risco de drift e edge cases).
6. **MCP ainda com agentes “simulados” em partes críticas** (efeito limitado em produção).

---

## 4) Plano de implementação (Ronaldinho -> OpenClaw-like)

## Fase A — Discovery real do OpenClaw (bloqueada no ambiente atual)
**Objetivo:** transformar hipóteses em requisitos concretos.

### Entregas
- Matriz de comparação `OpenClaw x Ronaldinho` (arquitetura, providers, runtime, observabilidade, segurança).
- Catálogo de padrões reutilizáveis com prioridade (`MUST/SHOULD/COULD`).
- ADR específica: “Adoção de padrões OpenClaw”.

### Critério de saída
- 100% dos padrões citados no plano validados contra código real do OpenClaw.

---

## Fase B — Runtime de providers orientado a políticas
**Objetivo:** tornar roteamento de modelo dinâmico, previsível e auditável.

### Implementação
1. Criar `ProviderRuntimePolicy`:
   - Inputs: credencial, latência histórica, taxa de erro, custo estimado, limits.
   - Output: provider/modelo escolhido + motivo da decisão.
2. Criar `ProviderHealthStore` (in-memory + persistência opcional):
   - Métricas por provider/modelo: success ratio, p95 latency, 429/5xx rate, cooldown.
3. Integrar no `LLMStrategyFactory` / `NeuralOrchestrator`:
   - substituir ordem fixa por ranking dinâmico.

### Critérios de aceite
- Cada decisão de roteamento sai com `decision_reason` e `policy_snapshot`.
- Fallback em cascata preservado, mas com ordenação dinâmica.

---

## Fase C — Observabilidade e SRE
**Objetivo:** reduzir MTTR e eliminar cegueira operacional.

### Implementação
1. Introduzir `ILogger<T>` e logs estruturados em:
   - Gateway, Orchestrator, Strategy, MCP Bus.
2. Criar objeto `ExecutionTrace` com:
   - `correlationId`, `channel`, `sessionId`, `provider`, `model`, `latencyMs`, `errorClass`.
3. Expor endpoint autenticado `/api/ops/executions` (últimas N execuções sanitizadas).

### Critérios de aceite
- Diagnóstico de incidente em < 5 min usando apenas endpoints/logs estruturados.

---

## Fase D — Resiliência avançada
**Objetivo:** estabilizar comportamento sob falha de upstream.

### Implementação
1. Circuit breaker por provider/modelo com estados:
   - Closed, Open, HalfOpen.
2. Retry policy por classe de erro:
   - 429: backoff curto + rotação;
   - 5xx: retry limitado;
   - 401/403/key inválida: sem retry, marca provider como indisponível.
3. Bulkhead para chamadas MCP/LLM (limite de concorrência por sessão).

### Critérios de aceite
- Nenhuma exceção de provider deve chegar “crua” ao canal final.
- Sob falha parcial, sistema mantém resposta com degradação controlada.

---

## Fase E — Testes de confiabilidade
**Objetivo:** evitar regressão e provar estabilidade.

### Implementação
1. Testes unitários:
   - seleção dinâmica de provider;
   - classificação de erros;
   - policy/circuit transitions.
2. Testes de integração:
   - Telegram -> Orchestrator -> Provider mock (429, 5xx, timeout, apiKey inválida).
3. Testes de caos local:
   - indisponibilidade de especialistas MCP;
   - latência artificial por provider;
   - queda intermitente do gateway.

### Critérios de aceite
- Cobertura de cenários críticos > 90% (matriz de incidentes).

---

## 5) Backlog técnico detalhado (próximas 3 sprints)

## Sprint 1 (Estabilidade de produção)
- [ ] `ProviderRuntimePolicy` + hooks no orquestrador.
- [ ] `ExecutionTrace` e logs estruturados ponta a ponta.
- [ ] classificador único de erros para Telegram/UI/API.

## Sprint 2 (Resiliência avançada)
- [ ] circuit breaker por provider/modelo.
- [ ] retry matrix por erro.
- [ ] endpoint `/api/ops/executions`.

## Sprint 3 (Qualidade e benchmark OpenClaw)
- [ ] suite de caos automatizada.
- [ ] benchmark comparativo com padrão OpenClaw validado.
- [ ] ADR final de integração + guia operacional.

---

## 6) Governança de implementação

- **Dono técnico:** `Ronaldinho.NeuralCore`
- **Dono de operação:** `Bridge + ConfigUI + observabilidade`
- **Rito semanal:** revisão de métricas (erro por provider, latência p95, taxa de fallback)
- **Gate de release:** bloquear deploy se regressão em cenários críticos de fallback

---

## 7) Definição de pronto (DoD)

1. Não há vazamento de erro técnico para Telegram/UI.
2. Nenhum provider inválido participa de decisão de rota.
3. Toda execução possui trace com `correlationId` auditável.
4. Falha parcial de upstream não derruba o fluxo de resposta.
5. Matriz OpenClaw x Ronaldinho validada contra código real assim que acesso externo estiver liberado.

