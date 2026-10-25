# ADR-001: Adoção do padrão Outbox transacional no MySQL para publicação de eventos de webhook

| Campo | Valor |
| --- | --- |
| Status | Aceito |
| Data | 2026-10-17 (data de elaboração; a reunião não registrou data) |
| Decisores | Diego, Larissa e Bruno `[T-05]`, `[T-39]`, `[T-40]`, `[T-51]` |
| Origem | `[T-05]` · `[09:06]` Diego / `[09:08]` Larissa; `[T-51]` · `[09:34]` Bruno/Diego; `[T-34]` · `[09:40]`–`[09:41]` Bruno/Diego; `[T-39]` · `[09:51]` Larissa; `[T-40]` · `[09:52]` Larissa |

## Status

Aceito

## Contexto

No código atual, a mudança de status de um pedido ocorre em `OrderService.changeStatus` (`src/modules/orders/order.service.ts:126-179`), que abre uma transação interativa via `this.prisma.$transaction(async (tx) => { ... })` (`src/modules/orders/order.service.ts:131`, com `TxClient = Prisma.TransactionClient` na linha 24, `src/modules/orders/order.service.ts:24`), debita ou repõe estoque (`src/modules/orders/order.service.ts:152-155`, `src/modules/orders/order.service.ts:228`), atualiza a tabela `orders` (`src/modules/orders/order.service.ts:158`) e insere o histórico em `order_status_history` (`src/modules/orders/order.service.ts:159`) `[T-56]`. Dentro de `changeStatus`, o serviço opera diretamente sobre o cliente transacional `tx` sem passar por `OrderRepository` (`src/modules/orders/order.service.ts:131-178`). A equipe precisava publicar notificações de webhook a cada transição de status sem introduzir chamadas HTTP síncronas dentro da transação de pedidos — para não travar a mudança de status de outros pedidos quando o cliente estiver lento e não dar rollback na mudança de status quando o cliente estiver fora do ar `[T-04]` — e sem subir infraestrutura adicional de mensageria além do MySQL já existente `[T-05]`, `[T-06]`.

## Decisão

Decidimos adotar o padrão *Transactional Outbox* utilizando uma tabela de outbox no próprio MySQL (ainda inexistente no código atual; nenhuma ocorrência de 'webhook' em `prisma/schema.prisma`), gravando o evento de webhook na mesma transação de banco que altera o status do pedido em `OrderService.changeStatus` (`src/modules/orders/order.service.ts:126-179`), porque isso garante atomicidade entre a mudança de status e o agendamento da notificação sem depender de chamadas externas na transação nem de nova infraestrutura `[T-05]`, `[T-56]`.

**Regras e restrições fechadas:**

- **Inserção transacional via função auxiliar com `tx`:** A gravação na outbox será feita dentro da transação aberta em `OrderService.changeStatus` (`src/modules/orders/order.service.ts:131`) por meio da função proposta `publishWebhookEvent(tx, order, fromStatus, toStatus)` (ainda inexistente no código), recebendo o cliente transacional `tx` (`TxClient`, `src/modules/orders/order.service.ts:24`) `[T-05]`, `[T-34]`.
- **Filtro de status na inserção:** A verificação de quais status o webhook do cliente assina ocorre no momento da inserção na outbox, e não no momento do envio HTTP, evitando gravar eventos para transições que não possuem assinantes interessados `[T-51]`.
- **Chave primária em UUID:** A tabela de outbox utilizará UUID como chave primária, conforme definido na reunião para seguir o padrão mencionado do projeto `[T-39]` (no schema atual, as entidades de domínio usam `@id @default(uuid()) @db.Char(36)`, como em `prisma/schema.prisma:26` e `prisma/schema.prisma:75`, com exceção da tabela auxiliar `OrderNumberSequence` em `prisma/schema.prisma:134`).
- **Payload gravado já renderizado, na inserção:** O evento gravado na outbox terá o payload gravado já renderizado, na inserção `[T-40]`.
- **Indexação para leitura de pendentes:** A tabela de outbox terá índice(s) no campo de `status` e em `created_at` (sem definir entre dois índices separados ou um índice composto, definição que cabe ao [FDD](../FDD.md)) para que o processador leia apenas os registros pendentes em lote pequeno (em `[09:08]`, Diego listou os valores `pendente`, `processando`, `falhou` e `entregue`, sendo que o uso efetivo do status `falhou` na outbox depende da resolução da ambiguidade registrada em Questões em aberto sobre a DLQ) `[T-07]`.

## Alternativas consideradas

### Alternativa 1: Envio HTTP síncrono dentro do `OrderService`

- **Prós:** Análise técnica: dispararia a requisição no fluxo direto de `OrderService.changeStatus` (`src/modules/orders/order.service.ts:126-179`), sem criar tabela de outbox (nenhuma ocorrência de 'webhook' em `prisma/schema.prisma`) nem leitura assíncrona posterior.
- **Contras:** Um cliente lento trava a mudança de status de outros pedidos e, se o endpoint do cliente estiver fora do ar, não é possível dar rollback na mudança de status do pedido em `OrderService.changeStatus` (`src/modules/orders/order.service.ts:126-179`) `[T-04]`, `[T-56]`.
- **Motivo do descarte:** Descartada por Bruno em `[09:04]` porque um cliente lento trava a mudança de status de outros pedidos dentro da transação que atualiza `orders`, insere em `order_status_history` e decrementa `stockQuantity` (`src/modules/orders/order.service.ts:228`), e porque, se o cliente estiver fora do ar, não é possível dar rollback na mudança de status do pedido (`src/modules/orders/order.service.ts:131-178`). Larissa concordou em `[09:04]` e Diego confirmou em `[09:06]` ("síncrono está fora de questão") `[T-04]`, `[T-56]`.

### Alternativa 2: Uso de Redis Streams

- **Prós:** Análise técnica: fornece estrutura dedicada de streaming/fila para consumo assíncrono de eventos fora do banco relacional.
- **Contras:** Exigiria subir mais infraestrutura além do banco já utilizado pelo projeto `[T-06]`; como análise técnica, uma escrita em Redis não compartilha a transação local `this.prisma.$transaction` aberta em `OrderService.changeStatus` (`src/modules/orders/order.service.ts:131`).
- **Motivo do descarte:** Larissa citou Redis Streams em `[09:07]` já observando que exigiria subir mais infraestrutura; Diego descartou em `[09:07]` por serem um time pequeno, considerando Redis Streams *overengineering* quando o MySQL existente já resolve com uma tabela de outbox `[T-05]`, `[T-06]`.

### Alternativa 3: Injetar o repository de webhook diretamente no `OrderService`

- **Prós:** Análise técnica: seguiria o padrão de instanciação e injeção de repositório no construtor de `OrderService` (`src/app.ts:43`).
- **Contras:** Análise técnica: aumentaria o acoplamento de `OrderService` (`src/modules/orders/order.service.ts:26`) com o módulo de webhooks e destoaria da implementação real de `OrderService.changeStatus`, que executa todas as operações transacionais diretamente sobre `tx` (`src/modules/orders/order.service.ts:131-178`) sem chamar métodos de `OrderRepository`.
- **Motivo do descarte:** Descartada por Bruno e Diego em `[09:41]` em favor da função auxiliar proposta `publishWebhookEvent(tx, order, fromStatus, toStatus)` recebendo o `tx`, evitando injetar o repository inteiro no `OrderService` `[T-34]`, `[T-60]`.

## Consequências

**Positivas**

- Garante atomicidade no MySQL: o evento de webhook só é persistido se o `tx.order.update` (`src/modules/orders/order.service.ts:158`) e o `tx.orderStatusHistory.create` (`src/modules/orders/order.service.ts:159`) também forem confirmados na mesma transação `[T-05]`, `[T-56]`.
- **Análise técnica:** Erros de negócio que abortam `OrderService.changeStatus` antes da atualização — como `from === to` (`ConflictError`, `src/modules/orders/order.service.ts:140-146`), transição inválida (`InvalidStatusTransitionError`, `src/modules/orders/order.service.ts:147-149`) ou estoque insuficiente (`InsufficientStockError`, `src/modules/orders/order.service.ts:152`, `src/modules/orders/order.service.ts:223`) — interrompem `this.prisma.$transaction` (`src/modules/orders/order.service.ts:131-178`); a transação inteira é revertida, então nenhuma linha da outbox é confirmada, evitando notificações indevidas.
- O filtro de status na inserção evita gravar linhas na outbox para transições não assinadas pelo cliente `[T-51]`, e o payload gravado já renderizado, na inserção, preserva os dados do momento do evento `[T-40]`.

**Negativas**

- **Análise técnica:** Como a verificação dos status assinados e a inserção na outbox ocorrem dentro da transação de mudança de status (`src/modules/orders/order.service.ts:131-178`), a transação passa a executar essa consulta de filtro e a escrita adicional antes do commit.
- Demanda índice(s) no campo de `status` e em `created_at` na tabela de outbox e acumula linhas com status `entregue` no banco enquanto o arquivamento permanecer fora do escopo desta feature `[T-07]`, `[T-47]`.

**Trade-off aceito:** aceita-se realizar a verificação de status inscritos e a escrita na outbox dentro da transação de mudança de status no MySQL para garantir a persistência atômica do evento com a alteração do pedido, sem travar a transação em chamadas HTTP síncronas nem subir infraestrutura adicional de mensageria `[T-04]`, `[T-05]`, `[T-06]`, `[T-51]`.

## Questões em aberto

- **Destino da linha original da outbox após envio para a DLQ (`[T-63]`, ambíguo):** Em `[09:08]`, Diego listou os status da outbox incluindo `falhou`, mas em `[09:18]` propôs mover eventos esgotados para uma tabela separada de dead letter (com concordância de Bruno: "faz sentido") e afirmou que o replay recoloca o item na outbox como `pendente`; não ficou definido se a linha original na outbox permanece com status `falhou` ou é removida ao ser copiada para a DLQ `[T-07]`, `[T-63]`.
- **Arquivamento de eventos entregues (`[T-47]`, adiado):** Em `[09:08]`, Diego citou um prazo informal com ressalva ("depois de 30 dias ou assim") para arquivar linhas com status `entregue` e evitar crescimento da tabela, deixando o arquivamento fora do escopo desta feature `[T-07]`, `[T-47]`.
- **Tamanho exato do lote (*batch*) de leitura da outbox (Lacuna 7, sem origem na reunião):** Foi definido que o worker lê apenas registros pendentes em "batch pequeno", porém o número exato de registros por lote não está na transcrição `[T-07]`.
- **Emissão de evento na criação de pedido em `OrderService.create` (Achado 1 do mapa de código, sem origem na reunião):** A reunião vinculou a chamada de `publishWebhookEvent` apenas ao método `changeStatus` (`src/modules/orders/order.service.ts:126-179`) `[T-34]`, mas `OrderService.create` (`src/modules/orders/order.service.ts:50-124`) também inicia o pedido com `status: OrderStatus.PENDING` (`src/modules/orders/order.service.ts:99`) e insere um registro em `order_status_history` com `fromStatus: null` e `toStatus: OrderStatus.PENDING` (`src/modules/orders/order.service.ts:106-113`); se a criação inicial deve ou não publicar na outbox não está na transcrição `[T-34]`.
- **Posição exata da chamada a `publishWebhookEvent` dentro da transação e uso de `from`/`to` explícitos (Achados 2 e 3 do mapa de código, sem origem na reunião):** Em `OrderService.changeStatus`, o objeto `order` carregado no início da transação (`src/modules/orders/order.service.ts:132`) mantém em memória o status antigo (`from` na linha 138, `src/modules/orders/order.service.ts:138`), o `tx.order.update` na linha 158 não muta essa constante e o pedido recarregado (`refreshed`) só é buscado na linha 169 (`src/modules/orders/order.service.ts:158-177`); a reunião definiu apenas que `publishWebhookEvent(tx, order, fromStatus, toStatus)` roda na mesma transação `[T-34]`, ficando a posição exata da chamada como definição de design para o FDD.

## Referências

- Transcrição: `[09:04]` Bruno e Larissa (`[T-04]`, `[T-56]`); `[09:06]`–`[09:08]` Diego e Larissa (`[T-04]`, `[T-05]`, `[T-06]`, `[T-07]`, `[T-47]`); `[09:18]` Diego e Bruno (`[T-63]`); `[09:34]` Bruno e Diego (`[T-51]`); `[09:40]`–`[09:41]` Bruno e Diego (`[T-34]`, `[T-60]`); `[09:51]`–`[09:52]` Larissa (`[T-39]`, `[T-40]`)
- Código: `src/modules/orders/order.service.ts:24`, `src/modules/orders/order.service.ts:26`, `src/modules/orders/order.service.ts:50-124`, `src/modules/orders/order.service.ts:99`, `src/modules/orders/order.service.ts:106-113`, `src/modules/orders/order.service.ts:126-179`, `src/modules/orders/order.service.ts:131`, `src/modules/orders/order.service.ts:131-178`, `src/modules/orders/order.service.ts:132`, `src/modules/orders/order.service.ts:138`, `src/modules/orders/order.service.ts:140-146`, `src/modules/orders/order.service.ts:147-149`, `src/modules/orders/order.service.ts:152`, `src/modules/orders/order.service.ts:152-155`, `src/modules/orders/order.service.ts:158`, `src/modules/orders/order.service.ts:158-177`, `src/modules/orders/order.service.ts:159`, `src/modules/orders/order.service.ts:223`, `src/modules/orders/order.service.ts:228`, `src/app.ts:43`, `prisma/schema.prisma:26`, `prisma/schema.prisma:75`, `prisma/schema.prisma:134`
- Documentos relacionados: [Plano de ADRs](../../_work/PLANO-ADRS.md) · [README de ADRs](./README.md) · [RFC](../RFC.md) · [FDD](../FDD.md)
