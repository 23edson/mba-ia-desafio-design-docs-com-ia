# Plano dos Architecture Decision Records (ADRs)

Este documento registra o planejamento e o recorte de escopo dos **7 Architecture Decision Records (`ADR-001` a `ADR-007`)** do Sistema de Webhooks de Notificação de Pedidos, derivado diretamente das decisões fechadas no catálogo congelado da reunião (`_work/CATALOGO.md`), do filtro de escopo e ambiguidades (`_work/INDICE.md`) e do mapeamento verificado da base de código (`_work/MAPA-CODIGO.md`).

---

## Origem e Critérios de Derivação

1. **Cobertura integral das decisões fechadas da reunião:** Todas as entradas classificadas como `DECISÃO FECHADA` na reunião técnica (`T-04`, `T-05`, `T-08`, `T-10`, `T-12`, `T-13`, `T-14`, `T-16`, `T-17`, `T-20`, `T-27`, `T-39`, `T-40`, `T-48`, `T-51`, consolidadas em `T-55`) foram agrupadas por coesão arquitetural em 6 ADRs principais (`ADR-001` a `ADR-006`) e 1 ADR complementar (`ADR-007`) `[T-55]`.
2. **Isolamento de escopo por ADR:** Cada ficha abaixo define o arquivo de destino, a decisão central em uma frase, o conjunto fechado de IDs `T-xx` permitidos, as âncoras verificadas no código existente e os pontos que o ADR **não pode decidir** (por serem classificados como `AMBÍGUO`, `ADIADO` ou lacuna da reunião) `[T-55]`.
3. **Separação de responsabilidades entre documentos:** Fluxos passo a passo, modelagem detalhada de tabelas, contratos de endpoints HTTP e payloads JSON completos pertencem ao `docs/FDD.md`, enquanto cada ADR documenta exclusivamente o contexto, a decisão, as alternativas consideradas, as consequências/trade-offs e as questões em aberto daquela escolha pontual `[T-55]`.

---

## Matriz de Rastreabilidade: Decisões da Reunião → ADRs

| Decisão Arquitetural | Decisões Fechadas (`_work/CATALOGO.md`) | Alternativas Descartadas (`_work/INDICE.md`) | Questões em Aberto / Ambiguidades / Adiados | Arquivo Previsto em `docs/adrs/` |
| :--- | :--- | :--- | :--- | :--- |
| **1. Padrão Outbox transacional no MySQL** | `T-05`, `T-39`, `T-40`, `T-51` | `T-04` (HTTP síncrono), `T-06` (Redis Streams), `T-60` (repository injetado no `OrderService`) | `T-47` (arquivamento adiado), `T-63` (destino da linha após DLQ), Lacuna 7 (tamanho do batch), Achado 1 (`OrderService.create`) | `ADR-001-outbox-transacional-no-mysql.md` |
| **2. Worker em processo separado com polling** | `T-08`, `T-10` | `T-09` (trigger no MySQL), `T-06` (Redis Streams) | `T-22` (nome do arquivo do processador), `T-46` (múltiplos workers adiado), Lacunas 7 e 8 | `ADR-002-worker-separado-com-polling.md` |
| **3. Política de retry com backoff exponencial e DLQ** | `T-12`, `T-13`, `T-14` | `T-41` (retry indefinido), `T-42` (apenas 3 tentativas), `T-43` (status `failed` na própria outbox) | `T-12.1` (5 no total vs. 1+5), `T-63`, `T-64` (`event_id` no replay), `T-31` e `T-32` (adiados), Lacunas 1 e 10 | `ADR-003-retry-com-backoff-e-dlq.md` |
| **4. Autenticação HMAC-SHA256 com secret por endpoint** | `T-16`, `T-17` | `T-61` (secret global da plataforma, descartada por risco de segurança) | Lacuna 4 (rota de rotação), Lacuna 6 (proteção da secret em repouso), Lacuna 11 (encoding hex/base64 de `X-Signature`) | `ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md` |
| **5. Garantia de entrega *at-least-once* com `X-Event-Id`** | `T-20` | `T-44` (entrega *exactly-once*) | `T-64` (manutenção ou renovação do `event_id` no replay da DLQ) | `ADR-005-entrega-at-least-once-com-event-id.md` |
| **6. Reuso dos padrões existentes do projeto** | `T-48`, `T-27` | `T-60` (acoplar repository no `OrderService`), introdução de bibliotecas externas fora do padrão | `T-22` (nome do processador), `T-27` e `T-50` (escopo de autorização por cliente / Achado 4) | `ADR-006-reuso-dos-padroes-do-projeto.md` |
| **7. Payload como snapshot imutável e limite de 64 KB** | `T-40` | `T-45` (truncar payload grande), gravar apenas `order_id` para consulta posterior | `T-36` (quais são os "campos básicos da order" além de `total_cents`), Lacuna 11, Achado 1 (`OrderService.create`) | `ADR-007-payload-snapshot-e-limite-de-64kb.md` |

Ordem de geração prevista: `ADR-001` a `ADR-007` (um documento por vez, validado contra `_work/CATALOGO.md`, `_work/MAPA-CODIGO.md` e `docs/TRACKER.md`).

---

## ADR-001

- **Arquivo:** `ADR-001-outbox-transacional-no-mysql.md`
- **Decisão:** registrar o evento de webhook numa tabela outbox do MySQL, na mesma transação que muda o status do pedido, com filtro de status na inserção e payload gravado como snapshot `[T-05]`, `[T-39]`, `[T-40]`, `[T-51]`.
- **IDs permitidos:**
  - Decisão e restrições: T-05, T-07, T-39, T-40, T-51
  - Alternativas descartadas: T-04 (envio síncrono, também decisão fechada), T-06 (Redis Streams), T-60 (injetar o repository de webhook no `OrderService`)
  - Gancho com código: T-56, T-34 (função proposta, ainda inexistente)
  - Questões em aberto: T-47 (arquivamento, adiado), T-63 (destino da linha da outbox após a DLQ, ambíguo)
- **Âncoras de código (mapa):**
  - Parte A, T-56: [código: `src/modules/orders/order.service.ts`] (`TxClient` linha 24; `changeStatus` 126–179; `$transaction` 131; gravação em `order_status_history` 158–159)
  - Seção 2 do mapa: a transação usa `tx` direto, sem o repository [código: `src/modules/orders/order.service.ts`]
  - Parte C: `publishWebhookEvent` e tabelas de webhook marcados `NÃO EXISTE`
  - Achados 1, 2 e 3 [código: `src/modules/orders/order.service.ts`]
- **Não pode decidir:**
  - T-63 (o que acontece com a linha da outbox depois da DLQ) `[T-63]`
  - Se a criação de pedido (`OrderService.create`) também emite evento (achado 1) [código: `src/modules/orders/order.service.ts`]
  - Tamanho do lote do polling (lacuna 7, não está na transcrição) `[T-07]`
  - Arquivamento das linhas entregues (T-47, adiado) `[T-47]`
  - A posição exata da chamada dentro da transação é proposta de design: a reunião disse só "dentro da mesma transação" `[T-34]`
- **Alternativas esperadas:** envio síncrono dentro do service `[T-04]`; Redis Streams ou fila externa `[T-06]`; injetar o repository no `OrderService` `[T-60]`.

## ADR-002

- **Arquivo:** `ADR-002-worker-separado-com-polling.md`
- **Decisão:** processar a outbox num processo Node.js separado da API, por polling a cada 2 segundos, com ordem garantida só por pedido e só com um worker `[T-08]`, `[T-10]`, `[T-11]`.
- **IDs permitidos:**
  - Decisão e restrições: T-02, T-07, T-08, T-10, T-11, T-25
  - Alternativas descartadas: T-09 (trigger no MySQL), T-06 (Redis, só se citada como alternativa de infraestrutura)
  - Gancho com código: T-58, T-25
  - Questões em aberto: T-22 (nome do arquivo do processador, ambíguo), T-46 (múltiplos workers, adiado)
- **Âncoras de código (mapa):**
  - Parte A, T-58: [código: `src/server.ts`] (6–27: `bootstrap`, `shutdown`, `SIGINT` e `SIGTERM`)
  - Parte A, T-25: [código: `src/config/database.ts`] (4–10: `createPrismaClient`)
  - Seção 10: [código: `src/config/env.ts`] (7, 8, 22, 27)
  - Achados 5 e 6 (o worker não sobe sem `JWT_SECRET`; o logger fixa `service: 'order-management-api'`) [código: `src/config/env.ts`], [código: `src/shared/logger/index.ts`]
  - Parte C: entry point do worker marcado `NÃO EXISTE`
- **Não pode decidir:**
  - Nome do arquivo do processador `[T-22]`
  - Tamanho do lote (lacuna 7, não está na transcrição) `[T-07]`
  - Recuperação de itens presos em "processando" após queda do worker (lacuna 8, não está na transcrição) `[T-07]`
  - Múltiplos workers `[T-46]`
  - Como o worker resolve o acoplamento ao `env` e ao nome do logger (achados 5 e 6): registrar como observação, a solução é do FDD [código: `src/config/env.ts`], [código: `src/shared/logger/index.ts`]
- **Alternativas esperadas:** trigger de banco `[T-09]`; processar dentro da instância da API `[T-10]`; fila externa com consumidor próprio `[T-06]`.

## ADR-003

- **Arquivo:** `ADR-003-retry-com-backoff-e-dlq.md`
- **Decisão:** retentar com backoff exponencial nos intervalos definidos na reunião, tratar timeout como falha, e mover falhas esgotadas para uma tabela de DLQ separada, com replay manual restrito a `ADMIN` `[T-12]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-30]`, `[T-35]`.
- **IDs permitidos:**
  - Decisão e restrições: T-12, T-13, T-14, T-15, T-30, T-35
  - Alternativas descartadas: T-41 (retry indefinido), T-42 (apenas 3 tentativas), T-43 (marcar `failed` na própria outbox)
  - Ambiguidades (só como questão em aberto): T-12.1, T-63, T-64
  - Gancho com código: T-59
- **Âncoras de código (mapa):**
  - Parte A, T-59: [código: `src/middlewares/auth.middleware.ts`] (`requireRole` 49–61; papéis `ADMIN` e `OPERATOR` na linha 9)
  - Seção 9: [código: `src/modules/users/user.routes.ts`] (única rota atual com `requireRole('ADMIN')`, linha 15)
- **Não pode decidir:**
  - Se "5 tentativas" é 5 no total ou 1 inicial mais 5 retentativas `[T-12.1]`
  - O destino da linha da outbox após a DLQ `[T-63]`
  - Se o replay mantém ou renova o `event_id` `[T-64]`
  - Quais códigos HTTP contam como sucesso (lacuna 1, não está na transcrição); a reunião só definiu que timeout conta como falha `[T-35]`
  - Retenção da DLQ (lacuna 10, não está na transcrição) `[T-14]`
  - Jitter, limite de concorrência e rate limiting (`T-32` é adiado) `[T-32]`
  - E-mail de aviso de falha (`T-31`, adiado) `[T-31]`
- **Alternativas esperadas:** retry indefinido `[T-41]`; 3 tentativas `[T-42]`; status `failed` na própria outbox `[T-43]`.

## ADR-004

- **Arquivo:** `ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md`
- **Decisão:** assinar o corpo da requisição com HMAC-SHA256, com uma secret única por endpoint de webhook, rotacionável com período de sobreposição de 24 horas, e exigir URLs HTTPS `[T-16]`, `[T-17]`, `[T-18]`.
- **IDs permitidos:**
  - Decisão e restrições: T-16, T-17, T-18, T-26, T-37, T-49, T-61
  - Processo: T-38.1 (revisão de segurança de dois dias úteis antes do deploy)
  - Gancho com código: T-24 (apenas para o achado do `redact`)
- **Âncoras de código (mapa):**
  - Seção 11 e achado 7: [código: `src/shared/logger/index.ts`] (`redactPaths` 4–11 não cobre `secret` nem `X-Signature`)
  - Parte B: o schema Zod do projeto ([código: `src/modules/orders/order.schemas.ts`] e [código: `src/middlewares/validate.middleware.ts`]) como padrão de validação de HTTPS `[T-18]`
- **Não pode decidir:**
  - Como a secret é protegida em repouso (lacuna 6, não está na transcrição) `[T-17]`
  - Formato do valor de `X-Signature`, hex ou base64 (lacuna 11, não está na transcrição) `[T-16]`
  - Caminho do endpoint de rotação (lacuna 4, não está na transcrição; `T-49` só diz que existe) `[T-49]`
  - Semântica de `X-Timestamp` além do que Diego disse: serve para o cliente detectar replay, se quiser `[T-37]`
  - Alternativas não discutidas (JWT, mTLS) só entram marcadas como `(plausível, não discutida)`; a reunião descartou a secret global por argumento de Sofia `[T-61]`
- **Alternativas esperadas:** secret global da plataforma (citada por Sofia como risco) `[T-61]`; outro mecanismo de autenticação, marcado como `(plausível, não discutida)`.

## ADR-005

- **Arquivo:** `ADR-005-entrega-at-least-once-com-event-id.md`
- **Decisão:** garantir entrega at-least-once e enviar um `X-Event-Id` (UUID gerado na inserção na outbox) para o receptor deduplicar `[T-20]`, `[T-37]`.
- **IDs permitidos:**
  - Decisão e restrições: T-20, T-37, T-11
  - Alternativa descartada: T-44 (exactly-once)
  - Dependência: T-54 (documentar o at-least-once e a deduplicação no portal de desenvolvedor)
  - Questão em aberto: T-64
- **Âncoras de código (mapa):** nenhuma específica. Se citar código, só a Parte C (nada de webhook existe hoje).
- **Não pode decidir:**
  - Se o replay mantém ou renova o `event_id` `[T-64]`
  - Se o `event_id` é a própria chave primária da outbox ou um campo à parte (não está na transcrição) `[T-20]`
  - Estratégia de deduplicação do lado do cliente além de deduplicar pelo `event_id` `[T-20]`
- **Alternativas esperadas:** entrega *exactly-once* (descartada na reunião por exigir coordenação dos dois lados) `[T-44]`.

## ADR-006

- **Arquivo:** `ADR-006-reuso-dos-padroes-do-projeto.md`
- **Decisão:** construir o módulo de webhooks reaproveitando os padrões existentes: estrutura de módulo, `AppError` com códigos de prefixo `WEBHOOK_`, middleware de erro centralizado, Pino, schemas Zod, `requireRole` e um `PrismaClient` próprio no processo do worker `[T-48]`, `[T-21]`, `[T-23]`, `[T-24]`, `[T-25]`.
- **IDs permitidos:**
  - Decisão e restrições: T-48, T-21, T-23, T-24, T-25, T-18
  - Ganchos com código: T-57, T-58, T-59
  - Questões em aberto (só como observação): T-22, T-27, T-50
- **Âncoras de código (mapa):**
  - Parte A: [código: `src/modules/orders/`] (estrutura do módulo)
  - [código: `src/shared/errors/app-error.ts`] (3–16) e [código: `src/shared/errors/http-errors.ts`] (33–63)
  - [código: `src/middlewares/error.middleware.ts`] (14–65)
  - [código: `src/shared/logger/index.ts`] (13–32)
  - [código: `src/middlewares/auth.middleware.ts`] (49–61) e [código: `src/middlewares/validate.middleware.ts`] (11–37)
  - [código: `src/app.ts`] (26–53 e 66–67) e [código: `src/routes/index.ts`] (13–31)
  - [código: `src/config/database.ts`] (4–10), [código: `prisma/schema.prisma`] (convenções)
  - Seção "Divergências entre reunião e código" e achados 4, 6, 7 e 8
- **Não pode decidir:**
  - O nome das colunas novas: a reunião falou em `snake_case` (`stock_quantity`, `created_at`, `customer_id`) e o código usa `camelCase` nos campos e `snake_case` só nas tabelas (`@@map`). Registrar a divergência como questão em aberto [código: `prisma/schema.prisma`]
  - O nome do arquivo do processador `[T-22]`
  - Códigos de erro além dos três exemplos da reunião (`WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL`, `WEBHOOK_SECRET_REQUIRED`) `[T-23]`
  - Quem pode gerenciar webhooks de qual cliente: `T-27` e `T-50` deixam o CRUD aberto a qualquer papel autenticado, e o código não tem papel de cliente (achado 4). Registrar como pendência de segurança, sem propor solução `[T-27]`, `[T-50]`, [código: `src/middlewares/auth.middleware.ts`]
  - Ajustes de `redact` e do nome do logger (achados 6 e 7): observação, solução é do FDD [código: `src/shared/logger/index.ts`]
- **Alternativas esperadas:** biblioteca ou framework novo para erros, logs ou filas `[T-48]`; módulo fora do padrão de `src/modules` `[T-21]`; injetar o repository de webhook no `OrderService` (já descartada no `ADR-001`, referenciada aqui) `[T-48]`.

## ADR-007

- **Arquivo:** `ADR-007-payload-snapshot-e-limite-de-64kb.md`
- **Decisão:** gravar o payload do evento já renderizado como snapshot imutável, sem itens do pedido, e rejeitar (sem truncar) eventos acima de 64 KB `[T-19]`, `[T-36]`, `[T-40]`, `[T-45]`.
- **IDs permitidos:**
  - Decisão e restrições: T-19, T-36, T-40
  - Alternativa descartada: T-45 (truncar payload grande)
  - Gancho com código: T-34, T-56
- **Âncoras de código (mapa):**
  - Parte A e seção 2: [código: `src/modules/orders/order.service.ts`] (`OrderService.create` 50–124; `OrderService.changeStatus` 126–179; linhas 132, 138–139, 158, 169–177)
  - Seção 3: [código: `prisma/schema.prisma`] (modelo `Order`, 74–97)
  - Divergência T-36: payload em `snake_case` na reunião e API em `camelCase` `[T-36]`, [código: `prisma/schema.prisma`]
  - Achados 1 e 3 [código: `src/modules/orders/order.service.ts`]
- **Não pode decidir:**
  - Quais são os "campos básicos da order" além de `total_cents` `[T-36]`
  - Se `OrderService.create` também emite evento (achado 1) [código: `src/modules/orders/order.service.ts`]
  - Como serializar os bytes ou assinar (lacuna 11, não está na transcrição) `[T-19]`
  - O que acontece com a mudança de status quando o evento excede 64 KB (a reunião só diz "erro") `[T-19]`, `[T-45]`
- **Alternativas esperadas:**
  - Gravar só o `order_id` e renderizar o payload no envio (discutida e descartada em favor do snapshot imutável) `[T-40]`.
  - Truncar o payload grande `[T-45]`.
