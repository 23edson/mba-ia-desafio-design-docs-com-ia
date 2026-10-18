# Índice do Catálogo

Derivado de CATALOGO.md. Não editar à mão.

## NÃO ENTRA (Descartados, Adiados e Fora de Escopo)
- **T-06**: Larissa sugeriu Redis Streams, mas Diego descartou por considerar overengineering. (Origem: Larissa/Diego em [09:07])
- **T-09**: Em `[09:09]` Bruno perguntou: "Não dá pra usar trigger do banco pra ser mais reativo?". Diego respondeu descartando: "MySQL não tem listener nativo". (Origem: Bruno/Diego em [09:09])
- **T-31**: Notificação por e-mail sobre falhas recorrentes de entrega mantida fora do escopo desta fase. (Origem: Larissa em [09:37])
- **T-32**: Implementação de rate limiting de saída para chamadas HTTP marcada para avaliação futura. (Origem: Diego em [09:39])
- **T-33**: Dashboard visual de gestão de webhooks agora não, é projeto separado do time de frontend. (Origem: Larissa em [09:40])
- **T-41**: Retry indefinido com backoff (evento ficaria pendurado se o cliente sumisse). (Origem: Diego em [09:15])
- **T-42**: Apenas 3 tentativas (considerado pouco para indisponibilidade de ~2h em manutenção planejada). (Origem: Bruno/Diego em [09:16])
- **T-43**: Marcar status "failed" na própria outbox; Diego preferiu tabela separada (`[09:18]`). (Origem: Larissa/Diego em [09:17])
- **T-44**: Entrega exactly-once (exigiria coordenação complexa dos dois lados). (Origem: Diego em [09:25])
- **T-45**: Truncar payload grande (Sofia defendeu "erra, não trunca", e Larissa confirmou). (Origem: Sofia/Larissa em [09:23])
- **T-46**: Múltiplos workers (particionar por order_id ou lock pessimista), "problema do futuro". (Origem: Diego em [09:13])
- **T-47**: Arquivamento das linhas entregues. (Origem: Diego em [09:08])
- **T-60**: Injetar o repository de webhook no OrderService (preferiu-se a função publishWebhookEvent recebendo o tx). (Origem: Bruno/Diego em [09:41])

## AMBIGUIDADES
- **T-12.1**: Em `[09:15]` Diego cita que 5 tentativas cobrem "uma janela de até 12 ou 24 horas" e em `[09:17]` cita "quase 15 horas entre primeira falha e última tentativa". Larissa fechou "Decidido: 5 tentativas" em `[09:17]`. Ambiguidade: (a) 5 no total ou (b) 1 inicial + 5 retries. (Origem: Diego/Larissa em [09:15], [09:17])
- **T-22**: Criação do processador, mas o nome do arquivo ficou ambíguo: `webhook.worker.ts` ou `webhook.processor.ts`. (Origem: Bruno em [09:28])
- **T-27.1**: Vínculo de `customer_id`: passado no body ou no path. (Origem: Larissa em [09:32])
- **T-36**: Formato do payload: event_id, event_type ("order.status_changed"), timestamp ISO 8601, order_id, order_number, from_status, to_status, customer_id e "campos básicos da order, tipo total_cents" (sem items). Ambiguidade: quais são os campos básicos. (Origem: Diego em [09:43])
- **T-63**: Depois que o evento vai pra DLQ, a linha da outbox vira "falhou" ou é removida? Em `[09:08]` lista status "falhou" na outbox, em `[09:18]` escolhe tabela webhook_dead_letter separada. No replay "recoloca na outbox como pendente". Não ficou claro o que acontece com a linha original. (Origem: Diego em [09:08], [09:18])
- **T-64**: No replay, o evento mantém o event_id original ou recebe outro? (A reunião não tratou disso; confirmado como lacuna). (Origem: Diego em [09:18])

## LACUNAS
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

## NÚMEROS
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
