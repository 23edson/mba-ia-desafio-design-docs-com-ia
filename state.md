# Estado Atual do Projeto (`state.md`)

**Data de atualização:** 2026-10-17

---

## 1. Resumo Executivo

- **Fase de preparação e fontes da verdade (Etapa 1):** **100% concluída e congelada.**
  - Tanto a transcrição da reunião (`_work/CATALOGO.md`) quanto a inspeção da base de código (`_work/MAPA-CODIGO.md`) passaram por múltiplas rodadas de verificação, estão congeladas em modo somente leitura (`chmod a-w` / `0444`) e possuem checksums SHA-256 verificados.
- **Fase de redação dos entregáveis finais (Etapas 2 a 8):** **ADRs concluídos; RFC, FDD, PRD, Tracker e README pendentes.**
  - Os arquivos em `docs/` (`PRD.md`, `RFC.md`, `FDD.md`, `TRACKER.md`) ainda contêm os placeholders originais, os 7 ADRs em `docs/adrs/` foram gerados e validados, e o `README.md` ainda contém o enunciado original do desafio.
- **Integridade do código-fonte:** **Preservada.** Nenhum arquivo de `src/`, `prisma/`, `tests/`, `package.json` ou `TRANSCRICAO.md` foi alterado.

---

## 2. Progresso por Etapa

| Etapa | Descrição | Status | Entregáveis / Artefatos e Situação Atual |
| :--- | :--- | :--- | :--- |
| **Etapa 1** | Contextualização, Mapeamento e Análise de Fontes | **CONCLUÍDA (Congelada)** | - `_work/CATALOGO.md` (congelado, `0444`, 65 itens `T-01` a `T-65` + 11 lacunas)<br>- `_work/INDICE.md` (mapeamento de `T-xx` por documento e lista `NÃO ENTRA`)<br>- `_work/MAPA-CODIGO.md` (congelado, `0444`, provas cruas `ls`/`grep -n`/`sed -n`, 7 divergências e 11 achados pendentes para o FDD)<br>- `_work/LOG.md` (histórico completo de prompts e correções)<br>- Versionamento direto em `_work/` (apenas artefatos definitivos) |
| **Etapa 2** | Elaboração dos Architecture Decision Records (ADRs) | **CONCLUÍDA (7 ADRs Gerados e Auditados)** | `_work/PLANO-ADRS.md` e `docs/adrs/README.md` com a matriz de rastreabilidade e escopo de `ADR-001` a `ADR-007`. Os 7 arquivos `ADR-NNN-*.md` gerados e validados com 0 erros. |
| **Etapa 3** | Consolidação do Request for Comments (RFC) | **PENDENTE** | `docs/RFC.md` contém apenas o placeholder original (67 bytes: `# RFC — Notificações de Eventos de Pedidos via Webhook`). |
| **Etapa 4** | Detalhamento do Feature Design Document (FDD) | **PENDENTE** | `docs/FDD.md` contém apenas o placeholder original (70 bytes: `# FDD — Notificações de Eventos de Pedidos via Webhook`). |
| **Etapa 5** | Elaboração do Product Requirement Document (PRD) | **PENDENTE** | `docs/PRD.md` contém apenas o placeholder original (76 bytes: `# PRD — Notificações de Eventos de Pedidos via Webhook`). |
| **Etapa 6** | Construção do Tracker de Rastreabilidade | **PENDENTE** | `docs/TRACKER.md` contém apenas o placeholder original (79 bytes: `# Tracker de Rastreabilidade — Fontes das Decisões`). |
| **Etapa 7** | Substituição do `README.md` da Raiz com a Jornada | **PENDENTE** | `README.md` ainda é o enunciado original do desafio (19.544 bytes). |
| **Etapa 8** | Auditoria de Critérios de Aceite e Entrega | **PENDENTE** | Depende da conclusão das Etapas 2 a 7. |

---

## 3. Artefatos de Trabalho e Fontes da Verdade (`_work/`)

| Arquivo | Permissão | Tamanho | Checksum SHA-256 / Observação |
| :--- | :--- | :--- | :--- |
| `_work/CATALOGO.md` | `-r--r--r--` | 15.822 B | `fbc5dd06f2e75265296bfb24a3b89519370d7bd8481d2e875907b9d849e489d4` (verificado via `_work/CATALOGO.sha256` e cópia `_work/CATALOGO.v1-congelado.md`) |
| `_work/MAPA-CODIGO.md` | `-r--r--r--` | 71.672 B | `7c91d681f38aa47f47c116d85375b1eb6cc27fa97a336ccc863724c3f23f16d3` (verificado via `_work/MAPA-CODIGO.sha256` e cópia `_work/MAPA-CODIGO.v1-congelado.md`) |
| `_work/INDICE.md` | `-rw-r--r--` | 6.759 B | Índice derivado de `CATALOGO.md` (o que não entra, ambiguidades, lacunas e números) |
| `_work/LOG.md` | `-rw-r--r--` | Atualizado | Registro cronológico de todos os prompts, fontes consultadas, arquivos alterados e rodadas de correção |
| `_work/templates/` | `drwxr-xr-x` | — | Templates estruturais (`prd_template.md`, `rfc_template.md`, `adr_template.md`, `fdd_template.md`) |
| `_work/PLANO-ADRS.md` | `-rw-r--r--` | Atualizado | Plano e matriz de rastreabilidade dos 7 ADRs (`ADR-001` a `ADR-007`) derivado de `CATALOGO.md`, `INDICE.md` e `MAPA-CODIGO.md` |

---

## 4. Resumo do Conteúdo Mapeado na Etapa 1

1. **Catálogo da Transcrição (`_work/CATALOGO.md`):**
   - **65 itens catalogados (`T-01` a `T-65`)** com timestamp exato, autor da proposta, quem fechou a decisão e classificação (`DECISÃO`, `REQUISITO`, `RESTRIÇÃO`, `RISCO`, `DESCARTADO`, `ADIADO`, `GANCHO DE CÓDIGO`, `MÉTRICA/PARÂMETRO`, `AMBÍGUO`).
   - **11 lacunas da reunião** explicitamente comprovadas como ausentes na transcrição.
2. **Mapa da Base de Código (`_work/MAPA-CODIGO.md`):**
   - **Parte A:** 12 ganchos citados na reunião verificados com saída crua de `ls`, `grep -n` e `sed -n`.
   - **Detalhamento (Pontos 1 a 11):** Provas completas de `AppError`/`http-errors.ts`, `OrderService.changeStatus` e `OrderService.create`, `order.status.ts`, `prisma/schema.prisma`, `auth.middleware.ts`, `error.middleware.ts`, `response.ts`, `package.json`, `tsconfig.build.json`, `vitest.config.ts`, `tests/setup.ts`, `tests/helpers/factories.ts`, `tests/orders.test.ts`, `.env.example`, `src/app.ts`, `src/routes/index.ts`, `order.routes.ts`, `user.routes.ts`, `database.ts`, `env.ts` e `logger/index.ts`.
   - **Parte B:** 5 fatos estruturais verificados no código para uso no FDD.
   - **Parte C:** 6 ganchos citados na reunião comprovadamente inexistentes no código atual (`NÃO EXISTE`).
   - **Divergências entre reunião e código:** 7 divergências documentadas com evidência linha a linha.
   - **Achados do código sem origem na reunião:** 11 observações factuais marcadas como **`pendência para o FDD`**.

---

## 5. Próximos Passos

Seguir a regra de `GEMINI.md` (**gerar um documento ou uma seção por vez**, usando exclusivamente fatos de `_work/CATALOGO.md` e `_work/MAPA-CODIGO.md` conforme `_work/PLANO-ADRS.md`):

1. **Etapa 2 — ADRs (`docs/adrs/ADR-001*.md` a `ADR-007*.md`):**
   - `ADR-001-outbox-transacional-no-mysql.md`: Outbox transacional no MySQL vs. envio síncrono / Redis Streams / repository injetado no `OrderService`.
   - `ADR-002-worker-separado-com-polling.md`: Worker de polling em processo separado vs. trigger no MySQL / processar na API.
   - `ADR-003-retry-com-backoff-e-dlq.md`: Política de retry com backoff exponencial, tabela de DLQ separada e replay restrito a `ADMIN`.
   - `ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md`: Assinatura HMAC-SHA256 com secret por endpoint, rotação com janela de 24h e HTTPS obrigatório.
   - `ADR-005-entrega-at-least-once-com-event-id.md`: Garantia de entrega *at-least-once* com `X-Event-Id` (UUID) vs. *exactly-once*.
   - `ADR-006-reuso-dos-padroes-do-projeto.md`: Reuso dos padrões do projeto existente (módulos, `AppError` com `WEBHOOK_`, Pino, Zod, `requireRole`, `PrismaClient`).
   - `ADR-007-payload-snapshot-e-limite-de-64kb.md`: Payload como snapshot imutável com limite de 64 KB | fontes: `T-19`, `T-36`, `T-40`, `T-45` | âncoras no código: `OrderService.create`, `changeStatus` (`src/modules/orders/order.service.ts`).
2. **Etapa 3 — RFC (`docs/RFC.md`)**
3. **Etapa 4 — FDD (`docs/FDD.md`)**
4. **Etapa 5 — PRD (`docs/PRD.md`)**
5. **Etapa 6 — Tracker (`docs/TRACKER.md`)**
6. **Etapa 7 — Jornada no `README.md`**
7. **Etapa 8 — Auditoria final contra a checklist**

