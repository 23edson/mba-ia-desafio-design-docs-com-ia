# Análise da Transcrição

## 📋 Tabela Principal de Mapeamento

| ID | Timestamp | Falante | Categoria | Resumo em uma linha |
| :--- | :--- | :--- | :--- | :--- |
| **T-01** | `[09:00]` | Marcos | `REQUISITO FUNCIONAL \| CONTEXTO` | Solicitação de clientes B2B (Atlas, MaxDistribuição, Nova Cargo) para notificações em tempo real de alteração de status de pedidos. |
| **T-02** | `[09:02]` | Marcos | `RESTRIÇÃO` | Latência aceitável pelos clientes para notificação em "tempo real" é de até 10 segundos. |
| **T-03** | `[09:02]` | Marcos | `RESTRIÇÃO` | Escopo de integração é estritamente outbound (envio de notificações do OMS para sistemas de clientes). |
| **T-04** | `[09:04]` | Bruno | `DECISÃO FECHADA \| DESCARTADO` | Descarte de envio HTTP síncrono dentro do "service de orders" (termo de Larissa em `[09:03]`) para evitar gargalos. Caminho exato a verificar no código. |
| **T-05** | `[09:06]` | Diego/Larissa | `DECISÃO FECHADA` | Adição do padrão Outbox Pattern no MySQL inserindo eventos na mesma transação de `orders`. (Proposto por Diego, fechado por Larissa `[09:08]`) |
| **T-06** | `[09:07]` | Larissa/Diego | `DESCARTADO` | Larissa sugeriu Redis Streams, mas Diego descartou por considerar overengineering. |
| **T-07** | `[09:08]` | Diego | `DETALHE SECUNDÁRIO` | Indexação por status ("pendente, processando, falhou, entregue") e `created_at`. O worker lê "só os pendentes em batch pequeno" (tamanho não definido). |
| **T-08** | `[09:09]` | Diego/Larissa | `DECISÃO FECHADA` | Worker de envio executará em polling constante a cada 2 segundos lendo registros pendentes da outbox. (Fechado por Larissa `[09:10]`) |
| **T-09** | `[09:09]` | Bruno/Diego | `DESCARTADO` | Em `[09:09]` Bruno perguntou: "Não dá pra usar trigger do banco pra ser mais reativo?". Diego respondeu descartando: "MySQL não tem listener nativo". |
| **T-10** | `[09:11]` | Diego/Larissa | `DECISÃO FECHADA` | Worker rodará como processo separado (Diego); Larissa sugeriu entry-point nova (`src/worker.ts` e `npm run worker`). |
| **T-11** | `[09:12], [09:13], [09:14]` | Diego/Larissa/Marcos | `RESTRIÇÃO` | Sem garantia de ordering global, apenas por `order_id` e enquanto for single-worker. Larissa fechou como "limitação conhecida" em `[09:13]`. Marcos reforçou em `[09:14]` que clientes não pediram ordering global. |
| **T-12** | `[09:17]` | Larissa | `DECISÃO FECHADA` | Backoff exponencial com teto de tentativas e envio para DLQ. |
| **T-12.1** | `[09:15], [09:17]` | Diego/Larissa | `AMBÍGUO` | Em `[09:15]` Diego cita que 5 tentativas cobrem "uma janela de até 12 ou 24 horas" e em `[09:17]` cita "quase 15 horas entre primeira falha e última tentativa". Larissa fechou "Decidido: 5 tentativas" em `[09:17]`. Ambiguidade: (a) 5 no total ou (b) 1 inicial + 5 retries. |
| **T-13** | `[09:17]` | Diego/Larissa | `DECISÃO FECHADA` | Intervalos de retentativa fixados em 1m, 5m, 30m, 2h e 12h. (Fechado por Larissa `[09:17]`) |
| **T-14** | `[09:18]` | Diego | `DECISÃO FECHADA` | Armazenamento de falhas esgotadas em tabela dedicada `webhook_dead_letter`. |
| **T-15** | `[09:18]` | Diego | `REQUISITO FUNCIONAL` | Endpoint administrativo (`POST /admin/webhooks/dead-letter/:id/replay`) para reprocessamento manual na DLQ (reconfirmado em `[09:35]`). |
| **T-16** | `[09:20]` | Sofia | `DECISÃO FECHADA` | Assinatura de payloads HTTP via HMAC-SHA256 transmitida no cabeçalho `X-Signature`. (Fechado por Sofia `[09:22]`) |
| **T-17** | `[09:21]` | Sofia | `DECISÃO FECHADA` | Chave secreta única por endpoint de webhook com suporte a rotação e período de tolerância de 24 horas. (Fechado por Sofia `[09:22]`) |
| **T-18** | `[09:23]` | Sofia | `RESTRIÇÃO` | Exigência mandatória de HTTPS em URLs cadastradas, validada via schema Zod. |
| **T-19** | `[09:24]` | Diego | `RESTRIÇÃO` | Limite máximo de tamanho de payload em 64KB, rejeitando eventos que excedam este tamanho. |
| **T-20** | `[09:24]` | Diego/Larissa | `DECISÃO FECHADA` | Garantia de entrega *at-least-once* contendo `X-Event-Id` (UUID) para desduplicação pelo receptor. (Fechado por Larissa `[09:26]`) |
| **T-21** | `[09:27]` | Bruno | `GANCHO COM CÓDIGO` | Organização do módulo em `src/modules/webhooks` mantendo os padrões de controller, service, repository, routes e schemas. |
| **T-22** | `[09:28]` | Bruno | `AMBÍGUO` | Criação do processador, mas o nome do arquivo ficou ambíguo: `webhook.worker.ts` ou `webhook.processor.ts`. |
| **T-23** | `[09:28], [09:29]` | Bruno/Larissa | `GANCHO COM CÓDIGO` | Padronização de erros customizados (`WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL`, `WEBHOOK_SECRET_REQUIRED`). Bruno sugeriu em `[09:28]` e Larissa fechou o prefixo `WEBHOOK_` em `[09:29]`. |
| **T-24** | `[09:29]` | Bruno | `GANCHO COM CÓDIGO` | Reutilização do logger Pino e do middleware de erro centralizado, que "vai pegar nossos erros sem precisar mudar nada". |
| **T-25** | `[09:30]` | Bruno | `GANCHO COM CÓDIGO` | Instanciação de cliente Prisma separado no processo do worker conectando à mesma `DATABASE_URL`. |
| **T-26** | `[09:31]` | Marcos | `REQUISITO FUNCIONAL` | Endpoint `POST` para cadastro de webhooks especificando URL e lista de status monitorados, devolvendo a secret gerada. |
| **T-27** | `[09:32]` | Larissa | `DECISÃO FECHADA` | O `customer_id` não vem do JWT. |
| **T-27.1** | `[09:32]` | Larissa | `AMBÍGUO` | Vínculo de `customer_id`: passado no body ou no path. |
| **T-28** | `[09:33]` | Bruno | `REQUISITO FUNCIONAL` | Endpoints CRUD (`GET`, `PATCH`, `DELETE`) para gestão de assinaturas. |
| **T-29** | `[09:34]` | Marcos | `REQUISITO FUNCIONAL` | Endpoint `GET /webhooks/:id/deliveries` para consulta dos últimos 100 registros. Campos listados: sucesso/falha, payload, response e tempo de resposta. |
| **T-30** | `[09:36]` | Larissa/Sofia | `RESTRIÇÃO` | Larissa: "role ADMIN obrigatório no replay e a gente reaproveita o requireRole que já existe". Sofia pediu log de quem fez o replay, pra auditoria. A assinatura exata da função deve ser conferida no código. |
| **T-31** | `[09:37]` | Larissa | `ADIADO` | Notificação por e-mail sobre falhas recorrentes de entrega mantida fora do escopo desta fase. |
| **T-32** | `[09:39]` | Diego | `ADIADO` | Implementação de rate limiting de saída para chamadas HTTP marcada para avaliação futura. |
| **T-33** | `[09:40]` | Larissa | `FORA DE ESCOPO` | Dashboard visual de gestão de webhooks agora não, é projeto separado do time de frontend. |
| **T-34** | `[09:40], [09:41]` | Bruno/Diego | `GANCHO COM CÓDIGO` | Inserção na outbox no método `changeStatus` do service de orders (a verificar no código se é `src/modules/orders/order.service.ts`). O nome `publishWebhookEvent(tx, order, fromStatus, toStatus)` foi proposto por Bruno em `[09:41]` e aceito por Diego. |
| **T-35** | `[09:42]` | Diego | `RESTRIÇÃO` | Timeout limite de 10 segundos para chamadas HTTP de notificação. |
| **T-36** | `[09:43]` | Diego | `AMBÍGUO` | Formato do payload: event_id, event_type ("order.status_changed"), timestamp ISO 8601, order_id, order_number, from_status, to_status, customer_id e "campos básicos da order, tipo total_cents" (sem items). Ambiguidade: quais são os campos básicos. |
| **T-37** | `[09:44], [09:45]` | Diego/Sofia | `DETALHE SECUNDÁRIO` | Cabeçalhos HTTP (`X-Event-Id`, `X-Signature`, `X-Timestamp`, `Content-Type`). O X-Timestamp é "pra cliente conseguir detectar replay attack se quiser" (Diego `[09:44]`). O `X-Webhook-Id` foi sugerido por Sofia em `[09:44]` e aceito por Diego em `[09:45]`. |
| **T-38** | `[09:46]` | Larissa | `DETALHE SECUNDÁRIO` | Planejamento de entrega estimado em 3 sprints. |
| **T-38.1** | `[09:46]` | Sofia | `DETALHE SECUNDÁRIO` | 2 dias úteis de revisão de segurança antes do deploy. |
| **T-39** | `[09:51]` | Larissa | `DECISÃO FECHADA` | Uso de UUID como chave primária da tabela de outbox. |
| **T-40** | `[09:52]` | Larissa | `DECISÃO FECHADA` | Armazenamento do payload de evento como snapshot imutável no momento da gravação na outbox. |
| **T-41** | `[09:15]` | Diego | `DESCARTADO` | Retry indefinido com backoff (evento ficaria pendurado se o cliente sumisse). |
| **T-42** | `[09:16]` | Bruno/Diego | `DESCARTADO` | Apenas 3 tentativas (considerado pouco para indisponibilidade de ~2h em manutenção planejada). |
| **T-43** | `[09:17]` | Larissa/Diego| `DESCARTADO` | Marcar status "failed" na própria outbox; Diego preferiu tabela separada (`[09:18]`). |
| **T-44** | `[09:25]` | Diego | `DESCARTADO` | Entrega exactly-once (exigiria coordenação complexa dos dois lados). |
| **T-45** | `[09:23]` | Sofia/Larissa | `DESCARTADO` | Truncar payload grande (Sofia defendeu "erra, não trunca", e Larissa confirmou). |
| **T-46** | `[09:13]` | Diego | `ADIADO` | Múltiplos workers (particionar por order_id ou lock pessimista), "problema do futuro". |
| **T-47** | `[09:08]` | Diego | `ADIADO` | Arquivamento das linhas entregues. |
| **T-48** | `[09:30]` | Larissa | `DECISÃO FECHADA` | Reuso máximo (AppError, Pino, middleware de erro, padrão de módulos, schemas Zod, padrão de códigos de erro). (Fechado por Larissa `[09:30]`) |
| **T-49** | `[09:21]` | Sofia | `REQUISITO FUNCIONAL` | Endpoint pro cliente pedir nova secret pela API (caminho não foi definido). |
| **T-50** | `[09:37]` | Sofia | `RESTRIÇÃO` | CRUD de configuração aberto a qualquer role autenticada "por enquanto", a endurecer depois. |
| **T-51** | `[09:34]` | Bruno/Diego | `DECISÃO FECHADA` | Filtro de status na inserção da outbox, não no envio. |
| **T-52** | `[09:00]` | Marcos | `CONTEXTO` | Clientes ficam consultando GET /orders em loop; a Atlas sugeriu migrar para o concorrente se não entregarmos até o fim do trimestre. |
| **T-53** | `[09:45]` | Marcos | `CONTEXTO` | A Atlas quer a entrega até o fim de novembro. |
| **T-54** | `[09:26]` | Marcos | `DEPENDÊNCIA` | Documentar o at-least-once e a deduplicação no portal de desenvolvedor. |
| **T-55** | `[09:48]` | Larissa | `DECISÃO FECHADA` | Resumo consolidado lido por Larissa, confirmado por Diego, Bruno e Sofia em `[09:49]`. |
| **T-56** | `[09:04]` | Bruno | `GANCHO COM CÓDIGO` | A transação de mudança de status atualiza orders, insere em order_status_history e decrementa stock_quantity. |
| **T-57** | `[09:28]` | Bruno | `GANCHO COM CÓDIGO` | AppError e classes como InsufficientStockError e InvalidStatusTransitionError, com códigos INSUFFICIENT_STOCK e INVALID_STATUS_TRANSITION. |
| **T-58** | `[09:11]` | Larissa | `GANCHO COM CÓDIGO` | `src/server.ts` como modelo da nova entry point. |
| **T-59** | `[09:36]` | Larissa | `GANCHO COM CÓDIGO` | Reaproveitar o requireRole existente. |
| **T-60** | `[09:41]` | Bruno/Diego | `DESCARTADO` | Injetar o repository de webhook no OrderService (preferiu-se a função publishWebhookEvent recebendo o tx). |
| **T-61** | `[09:21]` | Bruno/Sofia | `REQUISITO FUNCIONAL` | A tabela de configuração guarda url, secret, customer_id e estado ativo (Bruno perguntou, Sofia confirmou). |
| **T-62** | `[09:32]` | Marcos | `CONTEXTO` | O cliente usa a API direto, autenticado com o JWT do sistema, e existem usuários que representam o cliente. |
| **T-63** | `[09:08], [09:18]` | Diego | `AMBÍGUO` | Depois que o evento vai pra DLQ, a linha da outbox vira "falhou" ou é removida? Em `[09:08]` lista status "falhou" na outbox, em `[09:18]` escolhe tabela webhook_dead_letter separada. No replay "recoloca na outbox como pendente". Não ficou claro o que acontece com a linha original. |
| **T-64** | `[09:18]` | Diego | `AMBÍGUO` | No replay, o evento mantém o event_id original ou recebe outro? (A reunião não tratou disso; confirmado como lacuna). |
| **T-65** | `[09:49], [09:50]` | Sofia/Larissa | `CONTEXTO` | Em `[09:50]` Larissa vai "abrir o doc de design da feature e marcar uma sessão pro Bruno e o Diego revisarem comigo antes da gente começar a codar"; em `[09:49]` Sofia pede: "não esqueçam de me agendar pra revisão de segurança antes de subir". |

---

## 🔢 Tabela Específica de Números e Parâmetros Métricos

| Parâmetro / Métrica | Valor Citado | Contexto / Aplicação | Timestamp & Falante | ID |
| :--- | :--- | :--- | :--- | :--- |
| **Latência Máxima Desejada** | `< 10 segundos` | Requisito de tempo aceitável para "tempo real" pelos clientes | `[09:02]` Marcos | `T-02` |
| **Intervalo de Polling** | `2 segundos` | Frequência de leitura de eventos pendentes na outbox pelo worker | `[09:09]` Diego | `T-08` |
| **Quantidade de Tentativas** | `5 tentativas` | Ambiguidade: (a) 5 no total (sobraria o intervalo de 12h) ou (b) 1 inicial + 5 retries (usa os 5 intervalos, somando ~15 horas). | `[09:15]` Diego | `T-12.1` |
| **Intervalos de Backoff** | `1m, 5m, 30m, 2h, 12h` | Janela de tempo de retentativas (~15 horas totais) | `[09:17]` Diego | `T-13` |
| **Tolerância de Rotação (Grace Period)** | `24 horas` | Período em que a chave antiga continua válida após rotação | `[09:21]` Sofia | `T-17` |
| **Tamanho Máximo de Payload** | `64 KB` | Teto limite de tamanho do corpo da requisição de webhook | `[09:24]` Diego | `T-19` |
| **Histórico de Entregas** | `100 envios` | Quantidade de registros retornados no endpoint de consulta | `[09:34]` Marcos | `T-29` |
| **Timeout de Requisição HTTP** | `10 segundos` | Tempo máximo de espera por resposta do endpoint do cliente | `[09:42]` Diego | `T-35` |
| **Prazo de Desenvolvimento** | `3 sprints` | Estimativa de entrega do projeto | `[09:46]` Larissa | `T-38` |
| **Janela de Revisão de Segurança** | `2 dias úteis` | Tempo reservado para auditoria de segurança pré-deploy | `[09:46]` Sofia | `T-38.1` |

## ❓ Lacunas da reunião (não ditas)

As seguintes definições são necessárias para a documentação, mas **não foram debatidas na reunião** (portanto, não têm origem na transcrição):

1. **Critério de sucesso de uma entrega:** Em `[09:42]` Diego diz que cliente que não responde em 10s "a gente trata como falha e marca pra retry". Então timeout conta como falha. O que continua sem definição é quais códigos HTTP contam como sucesso ou falha.
2. **Métricas de observabilidade:** Busquei na transcrição inteira e não encontrei nenhuma menção.
3. **Tracing distribuído:** Busquei na transcrição inteira e não encontrei nenhuma menção.
4. **Caminho (rota) dos endpoints (criar, listar, editar, remover e rotacionar secret):** Busquei pelas rotas e não encontrei. Há menção apenas aos verbos HTTP (`[09:31]` POST, `[09:33]` PATCH, DELETE, GET). Os únicos com caminhos exatos são deliveries (`[09:34]`) e replay (`[09:18]`).
5. **Códigos de status HTTP das respostas da API:** Busquei na transcrição inteira e não encontrei nenhuma menção.
6. **Como a secret é protegida em repouso:** Busquei sobre proteção em banco e não encontrei (a discussão em `[09:20]` a `[09:22]` foca apenas no algoritmo HMAC e rotação, não em armazenamento seguro).
7. **Tamanho exato do lote do polling:** Em `[09:08]` Diego diz "lê só os pendentes em batch pequeno", mas busquei por um limite exato e não encontrei o número.
8. **Recuperação de eventos presos em "processando":** Busquei na transcrição inteira e não encontrei menção ao que fazer se o worker cair no meio do processo.
9. **Biblioteca de cliente HTTP:** Busquei por bibliotecas e não encontrei menção (apenas "HTTP call" em `[09:42]`).
10. **Retenção ou limpeza da DLQ:** Em `[09:08]` Diego cita retenção de 30 dias para linhas *entregues* (na outbox), mas busquei regras de retenção para a DLQ e não encontrei.
11. **Formato exato do valor do header X-Signature:** Em `[09:20]` Sofia fala em "assina o payload... manda a assinatura num header", mas busquei pelo encoding exato (hex, base64) e não encontrei.
