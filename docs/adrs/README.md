# Architectural Decision Records (ADRs)

Este diretório armazena os ADRs (Architectural Decision Records) e o plano de decisões arquiteturais do Sistema de Webhooks de Notificação de Pedidos `[T-55]`.

## Planejamento e Escopo

- [**Plano dos ADRs (`PLANO-ADRS.md`)**](../../_work/PLANO-ADRS.md): matriz de rastreabilidade ligando todas as decisões fechadas da reunião (`_work/CATALOGO.md`), alternativas descartadas (`_work/INDICE.md`) e âncoras de código (`_work/MAPA-CODIGO.md`) a cada ADR `[T-55]`.

## Índice de ADRs Previstos

| ADR | Arquivo | Decisão Central | Origem Principal |
| :--- | :--- | :--- | :--- |
| **ADR-001** | [`ADR-001-outbox-transacional-no-mysql.md`](./ADR-001-outbox-transacional-no-mysql.md) | Padrão Outbox transacional no MySQL na mesma transação de mudança de status do pedido | `[T-05]`, `[T-39]`, `[T-40]`, `[T-51]`, [código: `src/modules/orders/order.service.ts`] |
| **ADR-002** | [`ADR-002-worker-separado-com-polling.md`](./ADR-002-worker-separado-com-polling.md) | Worker em processo Node.js separado com polling a cada 2 segundos | `[T-08]`, `[T-10]`, `[T-11]`, [código: `src/server.ts`], [código: `src/config/database.ts`] |
| **ADR-003** | [`ADR-003-retry-com-backoff-e-dlq.md`](./ADR-003-retry-com-backoff-e-dlq.md) | Política de retry com backoff exponencial, tabela de DLQ separada e replay restrito a `ADMIN` | `[T-12]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-30]`, [código: `src/middlewares/auth.middleware.ts`] |
| **ADR-004** | [`ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md`](./ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) | Assinatura HMAC-SHA256 com secret única por endpoint, rotação com janela de 24h e HTTPS obrigatório | `[T-16]`, `[T-17]`, `[T-18]`, [código: `src/shared/logger/index.ts`] |
| **ADR-005** | [`ADR-005-entrega-at-least-once-com-event-id.md`](./ADR-005-entrega-at-least-once-com-event-id.md) | Garantia de entrega *at-least-once* com `X-Event-Id` (UUID) para deduplicação pelo receptor | `[T-20]`, `[T-37]`, `[T-44]` |
| **ADR-006** | [`ADR-006-reuso-dos-padroes-do-projeto.md`](./ADR-006-reuso-dos-padroes-do-projeto.md) | Reuso dos padrões existentes do projeto (módulos, `AppError` com `WEBHOOK_`, Pino, Zod, `requireRole`, `PrismaClient`) | `[T-48]`, `[T-21]`, `[T-23]`, `[T-24]`, `[T-25]`, [código: `src/modules/orders/`] |
| **ADR-007** | [`ADR-007-payload-snapshot-e-limite-de-64kb.md`](./ADR-007-payload-snapshot-e-limite-de-64kb.md) | Payload gravado como snapshot imutável sem itens do pedido e limite rígido de 64 KB | `[T-19]`, `[T-36]`, `[T-40]`, `[T-45]`, [código: `src/modules/orders/order.service.ts`] |
