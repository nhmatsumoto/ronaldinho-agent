# Planejamento de Capacidade e Performance (Capacity Planning)

Este documento detalha a estimativa de carga e a estratégia de infraestrutura para suportar a meta de usuários do Kettei Pro.

## 🎯 Meta: 4.300.000 Usuários Diários (DAU)

### 📊 Perfil de Carga Estimado
- **Janela de Operação Principal**: 8 horas (Horário Comercial).
- **Ações por Usuário/Dia**: ~5 requests críticas (Login, Check-in, Check-out, 2x Navegação).
- **Total de Requisições Diárias**: 4.3M * 5 = **21.5 Milhões de Requests/Dia**.

### 📉 Vazão (Throughput)
- **Média (Janela 8h)**: `21.5M / (8 * 3600)` ≈ **746 Requests/segundo (RPS)**.
- **Pico (Manhã/Saída - O "Efeito Manada")**: Estima-se 10x a média no início do turno (8:00 - 9:00).
  - **Pico Esperado**: **~7.500 RPS**.

## 🏗️ Capacidade Atual (Status: Desenvolvimento)
| Componente | Status | Capacidade Est. | Gargalo Atual |
| :--- | :--- | :--- | :--- |
| **API (.NET 9)** | ✅ Implementado | > 50k RPS (Stateless) | Nenhum (Kestrel é rápido). |
| **Leitura (Dapper)** | ⚠️ Parcial | ~2k RPS (Direto no DB) | Falta Cache (Redis) para aliviar o DB. |
| **Escrita (EF Core)** | ✅ Implementado | ~500 RPS | Locking de Banco e I/O de Disco. |
| **Banco (Postgres)** | ⚠️ Single Instance | ~3k TPS | Falta Particionamento e Replica de Leitura. |

## 🚀 Roteiro para Suportar 7.5k RPS (Pico)
Para sair da capacidade de "Dev" (~500 RPS seguros) para "Escala Massiva" (7.5k RPS), precisamos:

1.  **Cache L1/L2 (Redis)**: Cachear sessão e perfil de usuário reduz 90% dos hits no banco no Login/Navegação.
2.  **Particionamento**: Dividir a tabela `Punches` por Mês/Tenant.
3.  **Read Replicas**: 1 Writer (Master) + 3 Readers.
4.  **Horizontal Scaling**: Mínimo de 10 Pods da API no Kubernetes.
