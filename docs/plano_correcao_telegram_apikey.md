# Plano de Correção — Falha `apiKey` vazia no Telegram + gaps estruturais

## 1) Objetivo
Eliminar a falha em produção no Telegram (`apiKey` vazia/branca), reduzir erro técnico exposto ao usuário final e fechar gaps de confiabilidade, consistência de configuração e observabilidade do `NeuralCore`.

---

## 2) Escopo do plano

### Incidente principal
- Erro no fluxo de resposta do Telegram causado por configuração inválida de chave de provedor LLM.

### Gaps correlatos
- Tratamento de exceção com mensagem técnica crua para usuário.
- Divergência entre documentação e comportamento real de fallback.
- Persistência parcial de settings na API.
- Riscos de bootstrap por uso repetido de `BuildServiceProvider()`.

---

## 3) Fase 0 — Contenção imediata (0–1 dia)

### Ações
1. Validar em runtime (startup + request) as chaves de todos os providers com regra única:
   - `null`, `""`, whitespace-only e placeholders devem ser inválidos.
2. Se provider principal inválido, retornar erro operacional claro para log interno sem vazar detalhe técnico para chat.
3. No Telegram, substituir mensagem crua por:
   - mensagem amigável ao usuário;
   - `correlationId` para suporte;
   - detalhe técnico apenas em log.

### Critérios de aceite
- Usuário do Telegram não recebe stack/error string de SDK.
- Logs têm causa raiz + `correlationId`.
- Sistema faz fallback somente para providers válidos.

---

## 4) Fase 1 — Correção de arquitetura de configuração (1–2 dias)

### Ações
1. Centralizar validação de configuração em um único componente (ex.: `ProviderConfigurationValidator`).
2. Normalizar carregamento de segredos:
   - ordem explícita: `Vault -> .env -> Environment` (ou política definida) e documentada.
3. Corrigir persistência do endpoint `/api/settings` para incluir todos os campos expostos na UI (incluindo `openRouterModelId`).
4. Adicionar endpoint de diagnóstico seguro (autenticado) com status dos providers:
   - `Configured`, `Invalid`, `Ready` (sem exibir segredo).

### Critérios de aceite
- UI salva e runtime aplica os mesmos parâmetros sem drift.
- Operação consegue saber rapidamente qual provider está apto.

---

## 5) Fase 2 — Resiliência e fallback (2–3 dias)

### Ações
1. Definir política formal de fallback:
   - prioridade por `LLM_PROVIDER`;
   - skip automático de provider inválido;
   - regras para 401/403 (credencial), 429 (rate limit), 5xx (transitório).
2. Adicionar circuito simples por provider (cooldown curto após falha repetida).
3. Padronizar telemetria por tentativa:
   - provider, latência, código de erro, resultado, motivo de rotação.

### Critérios de aceite
- Falha de um provider não derruba experiência quando há outro válido.
- Logs permitem auditar por que houve troca de provider.

---

## 6) Fase 3 — Segurança e UX operacional (1–2 dias)

### Ações
1. Remover exposição de mensagens internas para canais finais (Telegram/UI).
2. Introduzir catálogo de erros amigáveis (ex.: `CONFIG_PROVIDER_INVALID`, `PROVIDER_RATE_LIMIT`, `UPSTREAM_UNAVAILABLE`).
3. Revisar logs para evitar vazamento de segredos em qualquer nível.
4. Incluir playbook de operação no `docs/` com passos de diagnóstico e recuperação.

### Critérios de aceite
- Nenhum erro cru de SDK aparece ao usuário.
- Operação resolve incidente com roteiro objetivo em < 15 min.

---

## 7) Fase 4 — Qualidade, testes e governança (2–3 dias)

### Ações
1. Testes unitários:
   - validação de chave por provider;
   - montagem da cadeia de fallback;
   - mapeamento de erro técnico -> erro amigável.
2. Testes de integração:
   - cenário Telegram com provider inválido;
   - cenário com fallback funcional entre 2+ providers.
3. Gate de CI:
   - build + testes obrigatórios em PR.
4. Alinhar README/ADR com comportamento real (remover divergências, ex.: providers de fallback).

### Critérios de aceite
- Regressão de `apiKey` vazia coberta por teste automatizado.
- Documentação reflete exatamente o runtime.

---

## 8) Plano de execução por prioridade

### P0 (bloqueante)
- Sanitização/validação de credenciais.
- Mensageria amigável no Telegram (sem erro cru).
- Correção de drift de settings (persistência completa).

### P1 (alta)
- Diagnóstico de providers.
- Política formal de fallback com telemetria.

### P2 (média)
- Circuit breaker simples.
- Limpeza de bootstrap/DI e redução de `BuildServiceProvider()`.

### P3 (evolutiva)
- Reforço de docs, ADR e playbooks.

---

## 9) Riscos e mitigação

- **Risco:** quebra de compatibilidade na leitura de config.
  - **Mitigação:** feature flag e rollout progressivo.
- **Risco:** erro de UX por mensagens genéricas demais.
  - **Mitigação:** catálogo de erros com instrução curta e `correlationId`.
- **Risco:** fallback mascarar problema real por excesso de retry.
  - **Mitigação:** limites claros de tentativa + logs estruturados.

---

## 10) Definição de pronto (DoD)

- Erro `apiKey` vazia não chega ao usuário final.
- Fallback ignora providers inválidos de forma determinística.
- `/api/settings` mantém consistência entre UI, `.env`, vault e runtime.
- Observabilidade suficiente para identificar causa raiz em minutos.
- Testes de regressão cobrindo o incidente em CI.
