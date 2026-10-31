# PRD: Notificação de Mudança de Status de Pedidos via Webhooks

| Campo | Valor |
| :--- | :--- |
| **Versão** | v1.2 |
| **Data** | 2026-10-25 |
| **Responsável** | Marcos (Product Owner), Larissa (Tech Lead), Diego (Arquiteto de Software), Sofia (Engenheira de Segurança), Bruno (Desenvolvedor Backend) `[T-55]`, `[T-65]` |
| **Status** | Aprovado |
| **Documentos relacionados** | [RFC](./RFC.md) · [FDD](./FDD.md) · [ADRs](./adrs/) |

---

## 1. Resumo e contexto da feature

A funcionalidade de notificações de pedidos via webhooks permite que o sistema de gestão de pedidos (OMS) avise ativamente os sistemas de clientes corporativos B2B sempre que houver uma alteração no status de seus pedidos `[T-01]`, `[T-03]`, `[código: src/modules/orders/order.service.ts]`. Atualmente, o OMS processa e registra internamente as mudanças de estado dos pedidos, mas exige que os sistemas dos clientes consultem a API de pedidos repetidamente em loop para descobrir atualizações `[T-52]`, `[T-56]`, `[código: src/modules/orders/order.routes.ts]`. A feature entrega notificações ativas de saída (*outbound*) com meta operacional de envio inferior a 10 segundos no fluxo nominal, autogestão de assinaturas via API, assinatura criptográfica de autenticidade sobre o corpo da requisição com suporte a rotação de credenciais por 24 horas, consulta ao histórico das últimas 100 tentativas de entrega, 1 tentativa inicial seguida de até 5 retentativas automáticas escalonadas (máximo de 6 disparos HTTP automáticos) e reprocessamento manual administrativo de falhas esgotadas `[ADR-001]`, `[ADR-002]`, `[ADR-003]`, `[ADR-004]`, `[FDD: Seção 6 / FLOW-03]`, `[T-02]`, `[T-03]`, `[T-12]`, `[T-13]`, `[T-15]`, `[T-16]`, `[T-17]`, `[T-26]`, `[T-28]`, `[T-29]`.

---

## 2. Problema e motivação

- **Situação atual:** O OMS gerencia a transição de status dos pedidos, atualiza o saldo de estoque e grava o histórico de mudanças de estado, mas não possui nenhum mecanismo de notificação ativa de saída (*outbound*) para informar sistemas de clientes quando um pedido muda de status `[T-01]`, `[T-03]`, `[T-56]`, `[código: src/modules/orders/order.service.ts]`.
- **Dor 1:** Sistemas de clientes corporativos B2B (Atlas, MaxDistribuição e Nova Cargo) precisam refletir mudanças de status de pedidos em tempo real (com latência aceitável de até 10 segundos) e, por falta de notificações ativas, ficam consultando a rota de listagem de pedidos da API em loop contínuo `[T-01]`, `[T-02]`, `[T-52]`.
- **Dor 2:** As consultas repetitivas em loop realizadas pelos sistemas dos clientes geram sobrecarga constante e desnecessária de leitura sobre a API de pedidos e o banco de dados da plataforma `[T-52]`, `[código: src/modules/orders/order.routes.ts]`.
- **Por que agora:** Três clientes B2B estratégicos (Atlas, MaxDistribuição e Nova Cargo) demandam a funcionalidade para operar sem consultas em loop, e o cliente Atlas sinalizou risco direto de migração para um concorrente caso a entrega não seja concluída até o fim do trimestre (final de novembro), exigindo execução dentro do horizonte planejado de 3 sprints `[T-01]`, `[T-38]`, `[T-52]`, `[T-53]`.

---

## 3. Público-alvo e cenários de uso

### Público-alvo

- **Clientes corporativos B2B integrados via API (ex.: Atlas, MaxDistribuição e Nova Cargo):** Empresas que consomem a API autenticada do OMS e precisam cadastrar seus endpoints HTTPS de destino, filtrar quais status de pedido desejam acompanhar, receber notificações autênticas e íntegras em até 10 segundos no fluxo nominal após cada mudança de status, rotacionar suas credenciais de segurança sem indisponibilidade e consultar o histórico recente de entregas para diagnóstico de integração `[T-01]`, `[T-02]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-26]`, `[T-28]`, `[T-29]`, `[T-49]`, `[T-62]`.
- **Administradores internos da plataforma OMS (perfil `ADMIN`):** Operadores com permissão administrativa que precisam reprocessar manualmente, de forma controlada e auditada, eventos de notificação que esgotaram todas as tentativas automáticas de entrega após indisponibilidade prolongada do sistema de um cliente `[T-14]`, `[T-15]`, `[T-30]`, `[T-59]`, `[código: src/middlewares/auth.middleware.ts]`.

### Cenários de uso

- Quando o status de um pedido é alterado no OMS para um estado monitorado, o sistema do cliente B2B com assinatura ativa consegue receber automaticamente a notificação com os dados básicos do pedido em menos de 10 segundos em condições nominais, sem precisar consultar a API de pedidos em loop `[T-01]`, `[T-02]`, `[T-36]`, `[T-51]`, `[T-52]`.
- Quando configura ou atualiza sua integração, o cliente B2B autenticado consegue cadastrar uma URL HTTPS com a lista de status de interesse, receber a credencial secreta exclusiva gerada para validação de autenticidade e consultar, editar, desativar ou excluir suas assinaturas `[T-16]`, `[T-17]`, `[T-18]`, `[T-26]`, `[T-28]`, `[T-61]`, `[T-62]`.
- Quando precisa trocar a credencial de segurança de um endpoint por política interna ou suspeita de exposição, o cliente B2B consegue solicitar uma nova chave secreta pela API mantendo a chave anterior válida por 24 horas para atualizar seu sistema receptor sem interrupção de entregas `[T-17]`, `[T-49]`.
- Quando deseja auditar entregas ou diagnosticar falhas de comunicação com seu servidor, o cliente B2B consegue consultar as últimas 100 tentativas de envio da sua assinatura, visualizando se houve sucesso ou falha, o conteúdo enviado, a resposta recebida e o tempo de resposta `[T-29]`.
- Quando o endpoint de um cliente fica indisponível durante uma janela temporária de manutenção, o cliente B2B consegue receber a notificação automaticamente assim que seu sistema se recupera dentro do ciclo de 1 tentativa inicial e até 5 retentativas escalonadas (`1m, 5m, 30m, 2h, 12h`, totalizando até 6 disparos automáticos), utilizando o identificador único do evento para descartar eventuais entregas duplicadas `[ADR-003]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-03]`, `[T-12]`, `[T-13]`, `[T-20]`, `[T-37]`.
- Quando o sistema de um cliente permanece fora do ar após os 6 disparos automáticos e o evento vai para a fila de falhas esgotadas (DLQ), o administrador do OMS (`ADMIN`) consegue acionar o reprocessamento manual do evento original (preservando seu identificador `event_id`) após a normalização do cliente, ficando registrado em log de auditoria quem realizou a operação `[ADR-003]`, `[FDD: Seção 6 / FLOW-05]`, `[T-12]`, `[T-14]`, `[T-15]`, `[T-30]`, `[T-63]`, `[T-64]`.

---

## 4. Objetivos e métricas de sucesso

| Objetivo | Métrica | Meta | Origem |
| :--- | :--- | :--- | :--- |
| Entregar notificações de mudança de status dentro da expectativa de tempo real dos clientes B2B no fluxo nominal | Tempo decorrido entre a confirmação da mudança de status do pedido e a conclusão da entrega no fluxo nominal (quando o endpoint externo responde na primeira tentativa; cenários de lentidão externa, *timeout* de até 10s ou indisponibilidade entram no ciclo de retentativas) | `< 10 segundos` no fluxo nominal (com verificação assíncrona de novos eventos a cada `2 segundos`) | `[ADR-002]`, `[T-02]`, `[T-08]`, `[T-12]`, `[T-35]` |
| Limitar o tempo de espera por resposta de servidores externos lentos ou indisponíveis | Tempo máximo de espera (*timeout*) por resposta HTTP `2xx` do endpoint do cliente em cada tentativa antes de registrar falha e agendar retentativa | `<= 10 segundos` por tentativa | `[ADR-003]`, `[FDD: Seção 8]`, `[T-35]` |
| Absorver indisponibilidades temporárias e janelas de manutenção dos clientes sem perda de eventos | Política de tentativas automáticas e intervalos progressivos de espera antes do encaminhamento do evento para a fila de falhas esgotadas (DLQ) | `1 tentativa inicial + até 5 retentativas` (máximo de `6 disparos HTTP automáticos`) nos intervalos `1m, 5m, 30m, 2h e 12h` (cobrindo janela de quase `15 horas` antes de ir para a DLQ) | `[ADR-003]`, `[FDD: Seção 6 / FLOW-03]`, `[FDD: Seção 16]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-14]` |
| Viabilizar rotação de credenciais de segurança sem perda ou rejeição de notificações em trânsito | Período de tolerância em que a chave secreta antiga continua válida em paralelo após a emissão de uma nova chave pela API | `24 horas` | `[ADR-004]`, `[T-17]` |
| Garantir visibilidade de diagnóstico sobre entregas recentes de cada assinatura | Quantidade de registros recentes de tentativas de envio retornados na consulta de histórico por assinatura | Últimos `100 envios` por assinatura | `[T-29]` |
| Proteger a plataforma e os consumidores contra eventos com volume excessivo ou corrompido de dados | Tamanho máximo permitido para o conteúdo (*payload*) de cada evento de notificação em UTF-8, sem truncamento | `<= 64 KB` (`65.536 bytes` em UTF-8) por evento | `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-19]`, `[T-45]` |
| Eliminar a necessidade de consultas repetitivas em loop à API de pedidos pelos clientes B2B | Adoção do recebimento via webhook pelos clientes B2B demandantes em substituição à consulta contínua em loop na listagem de pedidos | Derivada de `[T-01]` e `[T-52]`: habilitar a migração dos 3 clientes B2B demandantes (Atlas, MaxDistribuição e Nova Cargo) do modelo de consulta em loop para notificações ativas (meta percentual exata de redução de chamadas sem origem na transcrição — não está na transcrição) | Derivada de `[T-01]`, `[T-52]` |
| Atender ao prazo comercial crítico de retenção do cliente Atlas com validação de segurança | Prazo total de entrega do desenvolvimento e janela dedicada de revisão de segurança antes da entrada em produção | Desenvolvimento em `3 sprints` e entrega até o fim de novembro (fim do trimestre), incluindo `2 dias úteis` obrigatórios de revisão de segurança pré-deploy | `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[T-38]`, `[T-38.1]`, `[T-52]`, `[T-53]` |

---

## 5. Escopo

### Incluso

- Cadastro de assinaturas de webhook por cliente especificando URL de destino (obrigatoriamente em HTTPS) e lista de status de transição monitorados (`PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`), com geração e retorno de chave secreta exclusiva por endpoint `[ADR-004]`, `[RFC: Deliberação B1]`, `[FDD: Seção 7]`, `[T-17]`, `[T-18]`, `[T-26]`, `[T-27]`, `[T-61]`, `[código: src/modules/orders/order.status.ts]`.
- Gestão do ciclo de vida das assinaturas de webhook (listagem, consulta, edição de URL HTTPS, status monitorados e estado ativo/inativo, e exclusão), respeitando as regras de transição definidas na Deliberação C2 da [RFC](./RFC.md) e detalhadas no [FDD](./FDD.md) `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[FDD: Seção 7]`, `[T-28]`, `[T-50]`, `[T-61]`.
- Solicitação de nova chave secreta (rotação de credencial) pela API com período de tolerância de 24 horas no qual a chave anterior permanece válida em paralelo `[ADR-004]`, `[FDD: Seção 6 / FLOW-06]`, `[T-17]`, `[T-49]`.
- Captura atômica de eventos de notificação nas mudanças de status de pedidos (sem emissão na criação inicial do pedido em estado `PENDING`, conforme Deliberação B1 da [RFC](./RFC.md)), filtrando na origem apenas assinaturas ativas do cliente que monitoram o novo status `[ADR-001]`, `[RFC: Deliberação B1]`, `[T-01]`, `[T-05]`, `[T-34]`, `[T-51]`, `[T-56]`, `[código: src/modules/orders/order.service.ts]`.
- Geração do conteúdo da notificação como fotografia imutável (*snapshot*) no momento da mudança de status, contendo os metadados do evento (`event_id`, tipo `"order.status_changed"` e `timestamp` original da transição) e os dados básicos do pedido (sem a lista de itens nem observações internas, conforme os 13 campos especificados no [FDD](./FDD.md)), respeitando o limite máximo de 64 KB (`65.536 bytes` em UTF-8) sem truncamento e com *rollback* transacional em caso de excesso (Deliberação A1 da [RFC](./RFC.md)) `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-19]`, `[T-36]`, `[T-40]`, `[T-45]`.
- Envio assíncrono de notificações de saída (*outbound*) por processador dedicado em execução separada da API principal, com verificação de novos eventos a cada 2 segundos, tempo limite de 10 segundos por chamada HTTP (considerando respostas `2xx` como sucesso) e preservação da ordem de entrega por pedido durante o ciclo ativo de envio e retentativas em processador único `[ADR-002]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-03]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-35]`.
- Autenticação e rastreabilidade das notificações via cabeçalhos padronizados: assinatura `X-Signature` com HMAC-SHA256 calculado sobre o corpo da requisição (`payload`), instante da tentativa de disparo (`X-Timestamp`), identificador único do evento para desduplicação (`X-Event-Id`) e identificador da assinatura (`X-Webhook-Id`), conforme contrato na Seção 8 do [FDD](./FDD.md) `[ADR-004]`, `[ADR-005]`, `[FDD: Seção 8]`, `[T-16]`, `[T-20]`, `[T-37]`.
- Política de retentativas automáticas composta por 1 tentativa inicial e até 5 retentativas escalonadas nos intervalos de `1m, 5m, 30m, 2h e 12h` (máximo de 6 disparos HTTP automáticos) após falhas de entrega ou tempo limite excedido, mantendo o evento esgotado com status `falhou` na fila de saída e registrando-o na fila dedicada de falhas esgotadas (DLQ) `[ADR-003]`, `[FDD: Seção 6 / FLOW-03 e FLOW-04]`, `[T-07]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-14]`, `[T-35]`, `[T-63]`.
- Reprocessamento manual administrativo de eventos da DLQ exclusivo para o perfil `ADMIN`, reativando o evento original com preservação do seu `event_id` e registrando em log de auditoria quem acionou a operação `[ADR-003]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-05]`, `[T-15]`, `[T-30]`, `[T-59]`, `[T-63]`, `[T-64]`.
- Consulta das últimas 100 tentativas de entrega de uma assinatura, exibindo indicador de sucesso ou falha, conteúdo enviado, resposta recebida e tempo de resposta `[FDD: Seção 7]`, `[T-29]`.
- Documentação no portal de desenvolvedor explicando o modelo de entrega "pelo menos uma vez" (*at-least-once*) e a obrigatoriedade de desduplicação pelo identificador único do evento (`X-Event-Id`) no receptor `[ADR-005]`, `[T-20]`, `[T-54]`.

### Fora de escopo

| Item | Situação | Motivo | Origem |
| :--- | :--- | :--- | :--- |
| Recebimento de webhooks de entrada (*inbound*) enviados por sistemas externos para o OMS | Fora de escopo | A necessidade dos clientes B2B é exclusivamente receber notificações ativas de saída (*outbound*) emitidas pelo OMS quando o status do pedido muda | `[T-03]` |
| Disparo de chamadas HTTP de forma síncrona durante a operação de mudança de status do pedido | Descartado | Clientes lentos travariam a mudança de status de outros pedidos e a indisponibilidade de um cliente externo não pode impedir nem reverter a mudança de status comercial | `[ADR-001]`, `[T-04]` |
| Adoção de Redis Streams como infraestrutura externa de fila/mensageria | Descartado | Considerado complexidade desnecessária (*overengineering*) para o porte atual da equipe e exigiria subir e manter infraestrutura adicional quando o banco de dados existente atende à necessidade | `[ADR-001]`, `[ADR-002]`, `[T-06]` |
| Uso de gatilhos nativos (*triggers*) do banco de dados para acionar o envio de forma reativa | Descartado | O banco de dados utilizado não possui mecanismo nativo de escuta/notificação para processos externos, e soluções improvisadas foram descartadas pela equipe | `[ADR-002]`, `[T-09]` |
| Retentativas automáticas por tempo indefinido sem limite máximo de tentativas | Descartado | Eventos destinados a sistemas de clientes descontinuados ou permanentemente indisponíveis ficariam pendentes indefinidamente na fila de envio | `[ADR-003]`, `[T-41]` |
| Limite reduzido de apenas 3 tentativas automáticas de entrega | Descartado | Considerado insuficiente para cobrir janelas comuns de manutenção planejada dos clientes com duração aproximada de 2 horas | `[ADR-003]`, `[T-42]` |
| Manutenção definitiva de eventos com tentativas esgotadas apenas com marcador de falha na própria fila principal, sem registro dedicado na DLQ | Descartado | A equipe optou por registrar os eventos que esgotaram o teto de retentativas em estrutura dedicada de DLQ para controle e reprocessamento administrativo | `[ADR-003]`, `[T-14]`, `[T-43]` |
| Garantia de entrega exatamente uma vez (*exactly-once*) | Descartado | Exigiria coordenação distribuída complexa entre o OMS e os sistemas externos dos clientes, adotando-se entrega *at-least-once* com identificador único de evento para desduplicação | `[ADR-005]`, `[T-20]`, `[T-44]` |
| Truncamento automático de conteúdos de notificação que ultrapassem 64 KB | Descartado | Cortar o conteúdo corromperia os dados esperados pelo cliente; definiu-se que o sistema deve rejeitar com erro em vez de truncar ("erra, não trunca") | `[ADR-007]`, `[T-19]`, `[T-45]` |
| Acoplamento direto do repositório de webhooks no serviço de pedidos | Descartado | Descartado para evitar acoplamento excessivo entre os domínios de pedidos e de webhooks | `[ADR-001]`, `[ADR-006]`, `[T-34]`, `[T-60]` |
| Execução concorrente de múltiplos processadores de envio (*multi-worker*) com particionamento por pedido ou bloqueio pessimista | Adiado (fase futura) | Classificado como evolução futura; na fase atual um único processador atende à demanda e preserva a ordenação por pedido | `[ADR-002]`, `[ADR-005]`, `[T-11]`, `[T-46]` |
| Rotina de arquivamento ou expurgo automático de eventos já entregues (ex.: após cerca de 30 dias) | Adiado (fase futura) | Mencionado como necessidade operacional futura, mas mantido fora do escopo da entrega inicial desta feature | `[ADR-001]`, `[T-47]` |
| Envio de alertas por e-mail aos clientes sobre falhas recorrentes de entrega | Adiado (fase futura) | Mantido fora do escopo desta fase inicial para priorizar o núcleo de entrega e consulta via API | `[ADR-003]`, `[T-31]` |
| Limitação de taxa de saída (*rate limiting outbound*) para chamadas aos endpoints dos clientes | Adiado (fase futura) | Marcado para avaliação futura caso surja necessidade operacional com o volume de envios em produção | `[ADR-003]`, `[T-32]` |
| Painel visual (*dashboard*) para gestão de webhooks e visualização de entregas | Fora de escopo | Definido como projeto separado sob responsabilidade da equipe de frontend; nesta entrega os clientes operam diretamente via API | `[T-33]`, `[T-62]` |

---

## 6. Requisitos funcionais

### RF-001 Cadastro de assinatura de webhook

Permitir que um usuário autenticado cadastre uma nova assinatura de webhook para um cliente informando a URL HTTPS de destino e a lista de status de pedido monitorados (`PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`), recebendo na resposta a credencial secreta exclusiva gerada para o endpoint `[ADR-004]`, `[ADR-006]`, `[RFC: Deliberação B1]`, `[FDD: Seção 7]`, `[T-17]`, `[T-18]`, `[T-26]`, `[T-27]`, `[T-50]`, `[T-61]`, `[código: src/modules/orders/order.status.ts]`.

**Fluxo principal**
1. O usuário autenticado solicita a criação de uma assinatura na API informando o identificador do cliente (`customer_id`), a URL de destino em HTTPS e os status de transição de pedido que deseja monitorar, conforme contrato na Seção 7 do [FDD](./FDD.md) `[FDD: Seção 7]`, `[T-18]`, `[T-26]`, `[T-27]`, `[T-50]`, `[T-62]`.
2. O sistema valida que a URL utiliza obrigatoriamente o protocolo HTTPS, que o cliente existe e que ao menos um status de transição válido (`PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED` ou `CANCELLED`, excluído o estado inicial `PENDING` conforme Deliberação B1 da [RFC](./RFC.md)) foi informado `[ADR-004]`, `[RFC: Deliberação B1]`, `[FDD: Seção 7]`, `[T-18]`, `[T-26]`, `[T-27]`, `[código: src/modules/orders/order.status.ts]`.
3. O sistema gera uma credencial secreta exclusiva para o endpoint e salva a assinatura como ativa para o cliente `[ADR-004]`, `[T-17]`, `[T-26]`, `[T-61]`.
4. O sistema retorna os dados da assinatura criada e a credencial secreta gerada (exibida exclusivamente no ato do cadastro) para configuração da validação de autenticidade no servidor do cliente `[ADR-004]`, `[FDD: Seção 7]`, `[T-16]`, `[T-17]`, `[T-26]`.

**Fluxos alternativos e exceções**
- Caso a URL não utilize o protocolo HTTPS (ex.: `http://`) ou tenha formato inválido, o sistema rejeita o cadastro antes de criar a assinatura `[ADR-004]`, `[T-18]`, `[T-23]`.
- **Bloqueador pré-implementação (autorização multi-tenant):** Informar `customer_id` na requisição identifica o cliente alvo, mas não é suficiente por si só para autorizar o acesso aos recursos do tenant. Embora a reunião tenha deixado o CRUD inicialmente aberto a qualquer perfil autenticado (`[T-50]`) e definido que `customer_id` não vem do JWT (`[T-27]`), a definição e aplicação da regra de autorização entre o usuário autenticado e o `customer_id` é bloqueador obrigatório antes da implementação na [RFC](./RFC.md) e na Seção 16 do [FDD](./FDD.md) `[RFC: Impacto e riscos]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`, `[T-62]`, `[código: prisma/schema.prisma]`.
- **Proposta técnica pendente de aprovação de segurança (anti-SSRF):** O bloqueio adicional contra URLs que apontem ou resolvam para endereços IP privados, de loopback, link-local ou metadados de nuvem está especificado na Seção 8 do [FDD](./FDD.md) e aguarda aprovação formal de segurança antes da implementação `[RFC: Critérios de aprovação]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-18]`, `[T-38.1]`.

**Erros previstos**
- Requisição não autenticada ou com token inválido é rejeitada com erro 401 `[T-50]`, `[T-62]`, `[código: src/middlewares/auth.middleware.ts]`.
- URL ausente, malformada ou sem protocolo HTTPS retorna erro padronizado `WEBHOOK_INVALID_URL` `[ADR-004]`, `[ADR-006]`, `[T-18]`, `[T-23]`.
- Cliente inexistente ou violação da regra de autorização multi-tenant por `customer_id` impede a criação da assinatura `[RFC: Critérios de aprovação]`, `[FDD: Seção 7]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`.

**Prioridade:** Alta  
**Origem:** `[ADR-004]`, `[ADR-006]`, `[RFC: Deliberação B1]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 7]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-17]`, `[T-18]`, `[T-23]`, `[T-26]`, `[T-27]`, `[T-50]`, `[T-61]`, `[T-62]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/middlewares/validate.middleware.ts]`, `[código: src/modules/orders/order.status.ts]`

### RF-002 Consulta, atualização e remoção de assinaturas de webhook

Permitir que um usuário autenticado liste e consulte assinaturas de webhook cadastradas, atualize parcialmente seus parâmetros (URL HTTPS, lista de status monitorados e estado ativo/inativo) e remova assinaturas existentes `[ADR-004]`, `[ADR-006]`, `[RFC: Deliberação C2]`, `[T-18]`, `[T-28]`, `[T-50]`, `[T-61]`.

**Fluxo principal**
1. O usuário autenticado solicita pela API a listagem de assinaturas de um cliente, a consulta de uma assinatura específica, a atualização parcial (`PATCH`) ou a remoção (`DELETE`) de uma assinatura, conforme os contratos da Seção 7 do [FDD](./FDD.md) `[FDD: Seção 7]`, `[T-27]`, `[T-28]`, `[T-50]`.
2. Nas operações de atualização, o sistema valida os novos parâmetros enviados, exigindo protocolo HTTPS caso uma nova URL seja informada e validando os status de transição monitorados `[ADR-004]`, `[RFC: Deliberação B1]`, `[FDD: Seção 7]`, `[T-18]`, `[T-28]`, `[código: src/modules/orders/order.status.ts]`.
3. O sistema aplica a alteração solicitada (URL, lista de status monitorados ou estado ativo/inativo) ou remove a assinatura `[T-28]`, `[T-61]`.
4. O sistema retorna os dados atualizados da assinatura (sem reexpor a credencial secreta nas consultas ou listagens, conforme especificado na Seção 7 do [FDD](./FDD.md)) ou confirma a remoção `[FDD: Seção 7]`, `[T-17]`, `[T-28]`.

**Fluxos alternativos e exceções**
- Conforme estabelecido na Deliberação C2 da [RFC](./RFC.md) e especificado no `FLOW-07` do [FDD](./FDD.md):
  - Alterações na lista de status monitorados afetam exclusivamente novas mudanças de status de pedidos, sem cancelar eventos já gerados anteriormente `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[T-28]`, `[T-40]`, `[T-51]`.
  - Alterações de URL HTTPS passam a valer imediatamente para envios pendentes, retentativas e reprocessamentos daquela assinatura `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[T-28]`.
  - A desativação ou remoção de uma assinatura impede a geração de novos eventos, cancela o envio de eventos pendentes para aquele endpoint e bloqueia o reprocessamento manual na DLQ enquanto a assinatura não estiver ativa `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[T-15]`, `[T-28]`, `[T-51]`, `[T-61]`.
- **Bloqueador pré-implementação (autorização multi-tenant):** Informar o filtro `customer_id` ou o identificador da assinatura não substitui a verificação de permissão sobre o tenant, que depende do fechamento do modelo de autorização multi-tenant registrado na [RFC](./RFC.md) e na Seção 16 do [FDD](./FDD.md) `[RFC: Critérios de aprovação]`, `[FDD: Seção 7]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`.

**Erros previstos**
- Assinatura não encontrada para o identificador informado retorna erro padronizado `WEBHOOK_NOT_FOUND` (404) `[ADR-006]`, `[FDD: Seção 9]`, `[T-23]`.
- Atualização de endereço com URL não HTTPS ou inválida retorna erro padronizado `WEBHOOK_INVALID_URL` `[ADR-004]`, `[ADR-006]`, `[T-18]`, `[T-23]`.
- Requisição sem autenticação válida é negada com erro 401 `[T-50]`, `[código: src/middlewares/auth.middleware.ts]`.

**Prioridade:** Alta  
**Origem:** `[ADR-004]`, `[ADR-006]`, `[RFC: Deliberação B1]`, `[RFC: Deliberação C2]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 6 / FLOW-07]`, `[FDD: Seção 7]`, `[FDD: Seção 9]`, `[FDD: Seção 16]`, `[T-17]`, `[T-18]`, `[T-23]`, `[T-27]`, `[T-28]`, `[T-50]`, `[T-51]`, `[T-61]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/modules/orders/order.status.ts]`

### RF-003 Rotação de credencial secreta com janela de transição de 24 horas

Permitir que o cliente solicite pela API a geração de uma nova chave secreta para sua assinatura de webhook, mantendo a chave anterior válida em paralelo por um período de tolerância de 24 horas `[ADR-004]`, `[T-17]`, `[T-49]`.

**Fluxo principal**
1. O usuário autenticado aciona o endpoint de rotação de credencial secreta para uma assinatura de webhook ativa, conforme contrato na Seção 7 do [FDD](./FDD.md) `[FDD: Seção 6 / FLOW-06]`, `[FDD: Seção 7]`, `[T-49]`, `[T-50]`.
2. O sistema gera uma nova chave secreta exclusiva para a assinatura e preserva a chave anterior como válida por uma janela de 24 horas a partir do momento da rotação `[ADR-004]`, `[T-17]`, `[T-49]`.
3. O sistema retorna a nova chave secreta gerada e a data/hora de expiração da chave anterior para que o cliente atualize a verificação em seu sistema receptor `[ADR-004]`, `[FDD: Seção 6 / FLOW-06]`, `[T-17]`, `[T-49]`.
4. Após o término do período de 24 horas, a chave secreta antiga expira e deixa de ser utilizada `[ADR-004]`, `[T-17]`.

**Fluxos alternativos e exceções**
- Durante a janela de transição de 24 horas, tanto a credencial nova quanto a anterior permanecem válidas para permitir que o cliente conclua a migração sem rejeição de notificações; o mecanismo técnico de coexistência de assinaturas no cabeçalho `X-Signature` está especificado no `FLOW-06` e na Seção 8 do [FDD](./FDD.md) e aguarda ratificação formal de segurança antes da implementação `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 6 / FLOW-06]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`.
- Conforme a Deliberação C2 da [RFC](./RFC.md), envios pendentes, retentativas e replays realizados após a rotação utilizam as credenciais vigentes no momento do disparo `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[T-17]`, `[T-49]`.
- A validação de permissão do usuário autenticado sobre a assinatura depende do modelo de autorização multi-tenant pendente de decisão pré-implementação na [RFC](./RFC.md) e na Seção 16 do [FDD](./FDD.md) `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`.

**Erros previstos**
- Solicitação de rotação para uma assinatura inexistente retorna erro padronizado `WEBHOOK_NOT_FOUND` (404) `[ADR-006]`, `[FDD: Seção 9]`, `[T-23]`.
- Ausência de credencial obrigatória em operação que a exija retorna erro padronizado `WEBHOOK_SECRET_REQUIRED` `[ADR-006]`, `[FDD: Seção 9]`, `[T-23]`.

**Prioridade:** Alta  
**Origem:** `[ADR-004]`, `[ADR-006]`, `[RFC: Deliberação C2]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 6 / FLOW-06 e FLOW-07]`, `[FDD: Seção 7]`, `[FDD: Seção 8]`, `[FDD: Seção 9]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-23]`, `[T-27]`, `[T-49]`, `[T-50]`

### RF-004 Registro transacional e filtrado de eventos na mudança de status do pedido

Registrar automaticamente um evento de notificação pendente sempre que o status de um pedido mudar no OMS para um status monitorado (`PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED` ou `CANCELLED`) e o cliente possuir ao menos uma assinatura ativa inscrita para esse novo status, gravando o evento de forma atômica na mesma transação da mudança de status do pedido `[ADR-001]`, `[ADR-007]`, `[RFC: Deliberação B1]`, `[T-01]`, `[T-05]`, `[T-34]`, `[T-51]`, `[T-56]`, `[código: src/modules/orders/order.status.ts]`.

**Fluxo principal**
1. Um operador ou integração solicita a alteração de status de um pedido existente no OMS `[T-01]`, `[T-56]`, `[código: src/modules/orders/order.service.ts]`.
2. Na mesma operação transacional que atualiza o status do pedido, ajusta o estoque (quando aplicável) e grava o histórico de transição, o sistema identifica as assinaturas ativas do cliente associado ao pedido que monitoram o novo status `[ADR-001]`, `[T-05]`, `[T-34]`, `[T-51]`, `[T-56]`, `[T-61]`, `[código: src/modules/orders/order.service.ts]`.
3. Para cada assinatura ativa compatível, o sistema gera uma fotografia imutável (*snapshot*) do evento contendo os metadados da notificação (`event_id` em UUID, tipo `"order.status_changed"` e `timestamp` original da transição em ISO 8601) e os dados básicos do pedido (identificadores do pedido e do cliente, status anterior e novo, valores financeiros de subtotal, desconto e total em centavos e datas de criação/atualização, omitindo a lista de itens e observações internas, conforme os 13 campos definidos no `FLOW-01` do [FDD](./FDD.md)) `[ADR-007]`, `[FDD: Seção 6 / FLOW-01]`, `[T-36]`, `[T-39]`, `[T-40]`, `[T-51]`, `[código: prisma/schema.prisma]`.
4. O sistema grava o evento com status inicial `pendente` na fila transacional de saída e confirma em conjunto a mudança de status do pedido e o registro do evento `[ADR-001]`, `[T-05]`, `[T-07]`, `[T-34]`.

**Fluxos alternativos e exceções**
- Se o cliente do pedido não possuir assinaturas ativas ou nenhuma assinatura ativa monitorar o status de destino da transição, nenhum evento é registrado e a mudança de status do pedido é concluída normalmente `[ADR-001]`, `[T-51]`, `[T-61]`.
- Se a transição de status do pedido for inválida ou não houver estoque suficiente, a operação é interrompida pelas regras de negócio de pedidos e nenhum evento de notificação é confirmado `[ADR-001]`, `[T-05]`, `[T-56]`, `[T-57]`, `[código: src/modules/orders/order.service.ts]`.
- Se ocorrer falha ao registrar o evento de notificação, a mudança de status do pedido, o ajuste de estoque e o histórico sofrem reversão conjunta (*rollback*), garantindo que nenhum pedido mude de status sem que o evento correspondente seja registrado `[ADR-001]`, `[T-05]`, `[T-34]`, `[código: src/modules/orders/order.service.ts]`.
- A criação inicial de um pedido (em estado inicial `PENDING`) não emite notificação de mudança de status, conforme escopo acordado para transições de status e ratificado na Deliberação B1 da [RFC](./RFC.md) `[RFC: Deliberação B1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-01]`, `[T-34]`, `[T-36]`, `[código: src/modules/orders/order.service.ts]`.
- Clientes que necessitarem dos itens detalhados do pedido consultam posteriormente o endpoint existente de detalhes do pedido (`GET /api/v1/orders/:id`) `[ADR-007]`, `[T-36]`, `[código: src/modules/orders/order.routes.ts]`.

**Erros previstos**
- Tentativa de transição para o mesmo status atual ou transição não permitida pela máquina de estados retorna erro `INVALID_STATUS_TRANSITION` (409) sem gerar notificação `[T-57]`, `[código: src/modules/orders/order.service.ts]`, `[código: src/shared/errors/http-errors.ts]`.
- Falta de estoque ao aprovar pagamento retorna erro `INSUFFICIENT_STOCK` (422) sem gerar notificação `[T-56]`, `[T-57]`, `[código: src/modules/orders/order.service.ts]`, `[código: src/shared/errors/http-errors.ts]`.

**Prioridade:** Alta  
**Origem:** `[ADR-001]`, `[ADR-007]`, `[RFC: Deliberação B1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-01]`, `[T-05]`, `[T-07]`, `[T-34]`, `[T-36]`, `[T-39]`, `[T-40]`, `[T-51]`, `[T-56]`, `[T-57]`, `[T-61]`, `[código: prisma/schema.prisma]`, `[código: src/modules/orders/order.routes.ts]`, `[código: src/modules/orders/order.service.ts]`, `[código: src/modules/orders/order.status.ts]`, `[código: src/shared/errors/http-errors.ts]`

### RF-005 Validação do limite de 64 KB para os dados da notificação

Validar que a fotografia de dados (*snapshot*) de cada evento de notificação não ultrapasse o limite máximo de 64 KB (`65.536 bytes` em UTF-8), rejeitando eventos que excedam esse teto sem truncar seu conteúdo e revertendo a transação de mudança de status `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-19]`, `[T-40]`, `[T-45]`.

**Fluxo principal**
1. No momento de gerar a fotografia imutável do evento de mudança de status (sem a lista de itens do pedido), o sistema verifica o tamanho em bytes UTF-8 do conteúdo serializado `[ADR-007]`, `[FDD: Seção 6 / FLOW-01]`, `[T-19]`, `[T-36]`, `[T-40]`.
2. Se o tamanho for igual ou inferior a `65.536 bytes` (64 KB), o evento é gravado normalmente como `pendente` na mesma transação da mudança de status do pedido `[ADR-001]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-07]`, `[T-19]`.

**Fluxos alternativos e exceções**
- Caso o tamanho do conteúdo ultrapasse `65.536 bytes` (64 KB), o sistema jamais trunca os dados ("erra, não trunca"): a operação lança erro de domínio e, conforme estabelecido na Deliberação A1 da [RFC](./RFC.md), executa o *rollback* integral da transação de mudança de status do pedido (revertendo a alteração de status, o ajuste de estoque e o histórico) `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-19]`, `[T-45]`, `[código: src/modules/orders/order.service.ts]`.

**Erros previstos**
- Evento cujo conteúdo supere `65.536 bytes` (64 KB) resulta em erro padronizado de domínio (`WEBHOOK_PAYLOAD_TOO_LARGE`, HTTP 422 conforme a Seção 9 do [FDD](./FDD.md)) e reversão completa da mudança de status `[ADR-006]`, `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 9]`, `[T-19]`, `[T-23]`, `[T-45]`.

**Prioridade:** Média (classificação de análise do documento pelo baixo risco de ocorrer em operação normal após a omissão da lista de itens do evento) `[ADR-007]`, `[T-19]`, `[T-36]`  
**Origem:** `[ADR-006]`, `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[FDD: Seção 9]`, `[T-05]`, `[T-19]`, `[T-23]`, `[T-36]`, `[T-40]`, `[T-45]`, `[código: src/modules/orders/order.service.ts]`

### RF-006 Despacho assíncrono de notificações assinadas com ordenação por pedido

Enviar de forma assíncrona as notificações pendentes para a URL HTTPS da assinatura correspondente por meio de um processador independente que verifica novos eventos a cada 2 segundos, inclui assinatura criptográfica sobre o corpo da requisição e cabeçalhos de rastreabilidade, considera respostas HTTP `2xx` como sucesso e preserva a ordem de entrega por pedido durante o ciclo ativo de envio e retentativas `[ADR-002]`, `[ADR-004]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-02]`, `[T-03]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-16]`, `[T-20]`, `[T-35]`, `[T-37]`.

**Fluxo principal**
1. O processador de envios, executando em processo separado da API principal, consulta a cada 2 segundos um lote de eventos aptos para envio com status `pendente` `[ADR-002]`, `[T-07]`, `[T-08]`, `[T-10]`.
2. Para eventos de um mesmo pedido (`order_id`) destinados a uma mesma assinatura, o processador único respeita a ordem cronológica das transições e aguarda a conclusão (ou o esgotamento para a DLQ) de um evento anterior antes de disparar eventos subsequentes daquele pedido `[ADR-002]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02]`, `[T-11]`.
3. O processador marca o evento como `processando`, preserva inalterada a fotografia de dados (*snapshot*, com o `timestamp` original da transição) e calcula a assinatura criptográfica HMAC-SHA256 sobre o corpo da requisição HTTP (`payload`), conforme decisão aceita no [ADR-004](./adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md), utilizando a credencial secreta vigente da assinatura `[ADR-004]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-07]`, `[T-16]`, `[T-17]`, `[T-40]`.
4. O processador envia uma requisição HTTP `POST` ao endereço HTTPS da assinatura contendo o corpo JSON imutável do evento e os cabeçalhos padronizados (`X-Signature` com o HMAC-SHA256 do corpo, `X-Event-Id` para desduplicação, `X-Timestamp` com o instante da tentativa de disparo HTTP — distinto do `timestamp` original do evento no corpo —, `X-Webhook-Id` e `Content-Type: application/json`, detalhados na Seção 8 do [FDD](./FDD.md)), aguardando resposta por até 10 segundos `[ADR-004]`, `[ADR-005]`, `[FDD: Seção 8]`, `[T-16]`, `[T-18]`, `[T-20]`, `[T-35]`, `[T-36]`, `[T-37]`.
5. Quando o servidor do cliente responde com código HTTP na faixa `2xx` (`200` a `299`) dentro do limite de 10 segundos, o sistema atualiza o status do evento para `entregue` e registra a tentativa bem-sucedida no histórico de entregas da assinatura `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-07]`, `[T-29]`, `[T-35]`.

**Fluxos alternativos e exceções**
- Como o modelo adotado é de entrega "pelo menos uma vez" (*at-least-once*), um mesmo evento pode ser entregue mais de uma vez em cenários de falha de comunicação após o recebimento pelo destino; cabe ao cliente utilizar o cabeçalho `X-Event-Id` (e o campo `event_id` no corpo) para identificar e descartar duplicatas `[ADR-005]`, `[T-20]`, `[T-36]`, `[T-37]`, `[T-54]`.
- Não há garantia de ordenação global entre eventos de pedidos diferentes; além disso, conforme especificado no `FLOW-04` do [FDD](./FDD.md), caso um evento antigo esgote todas as retentativas automáticas e seja movido para a DLQ (`falhou`), os eventos posteriores daquele mesmo pedido deixam de ficar bloqueados e seguem para entrega normal — de modo que um eventual replay manual futuro daquele evento antigo poderá ser entregue após eventos mais recentes do mesmo pedido `[ADR-002]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02 e FLOW-04]`, `[T-11]`, `[T-14]`, `[T-15]`.

**Erros previstos**
- Se o servidor do cliente não responder em até 10 segundos (*timeout*), ocorrer erro de conexão/rede ou a resposta HTTP estiver fora da faixa `2xx`, a tentativa é registrada como falha no histórico da assinatura e o evento é encaminhado ao fluxo de retentativas automáticas `[ADR-003]`, `[FDD: Seção 8]`, `[T-12]`, `[T-29]`, `[T-35]`.

**Prioridade:** Alta  
**Origem:** `[ADR-002]`, `[ADR-003]`, `[ADR-004]`, `[ADR-005]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-02 e FLOW-04]`, `[FDD: Seção 8]`, `[T-02]`, `[T-03]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-12]`, `[T-14]`, `[T-15]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-20]`, `[T-29]`, `[T-35]`, `[T-36]`, `[T-37]`, `[T-40]`, `[T-54]`

### RF-007 Retentativas automáticas escalonadas diante de falhas ou tempo limite excedido

Reagendar automaticamente o envio de notificações que sofrerem falha (resposta HTTP fora da faixa `2xx` ou erro de rede) ou excederem o tempo limite de 10 segundos, executando 1 tentativa inicial e até 5 retentativas automáticas (máximo de 6 disparos HTTP automáticos) nos intervalos progressivos de 1 minuto, 5 minutos, 30 minutos, 2 horas e 12 horas `[ADR-003]`, `[FDD: Seção 6 / FLOW-03]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-35]`.

**Fluxo principal**
1. Uma tentativa de envio para o endpoint do cliente retorna status HTTP fora da faixa `2xx`, sofre erro de comunicação ou atinge o tempo limite de 10 segundos sem resposta `[ADR-003]`, `[FDD: Seção 8]`, `[T-12]`, `[T-35]`.
2. O sistema registra o resultado da tentativa malsucedida (incluindo código/resposta obtida, se houver, e tempo decorrido) no histórico de entregas da assinatura `[T-29]`, `[T-35]`.
3. Após a tentativa inicial (1º disparo), caso ocorram falhas sucessivas, o sistema agenda até 5 retentativas automáticas (2º ao 6º disparo) aplicando sequencialmente os intervalos de espera de `1m`, `5m`, `30m`, `2h` e `12h` (cobrindo uma janela total de quase 15 horas) `[ADR-003]`, `[FDD: Seção 6 / FLOW-03]`, `[FDD: Seção 16]`, `[T-12]`, `[T-12.1]`, `[T-13]`.
4. Quando o intervalo programado é atingido, o processador realiza novo disparo mantendo a fotografia original do evento (com seu `event_id` e `timestamp` original do evento) e o mesmo `X-Event-Id`, gerando um novo cabeçalho `X-Timestamp` correspondente ao instante da nova tentativa, utilizando a URL e as credenciais vigentes da assinatura ativa e registrando a nova tentativa no histórico `[ADR-005]`, `[ADR-007]`, `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-02, FLOW-03 e FLOW-07]`, `[T-13]`, `[T-20]`, `[T-29]`, `[T-37]`, `[T-40]`.

**Fluxos alternativos e exceções**
- Se o servidor do cliente responder com código HTTP `2xx` em até 10 segundos em qualquer uma das até 5 retentativas, o evento é atualizado para `entregue` e o ciclo de retentativas é encerrado `[ADR-003]`, `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-07]`, `[T-12]`, `[T-35]`.
- Se a assinatura for desativada ou removida enquanto o evento aguarda uma retentativa, o envio deixa de ser realizado, conforme a Deliberação C2 da [RFC](./RFC.md) `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[T-28]`, `[T-61]`.

**Erros previstos**
- Caso a 5ª retentativa (6º disparo HTTP automático no total) também falhe ou exceda o tempo limite de 10 segundos, o ciclo automático é encerrado e o evento segue para o isolamento de falhas esgotadas (DLQ) `[ADR-003]`, `[FDD: Seção 6 / FLOW-04]`, `[T-12]`, `[T-13]`, `[T-14]`, `[T-35]`.

**Prioridade:** Alta  
**Origem:** `[ADR-003]`, `[ADR-005]`, `[ADR-007]`, `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-02, FLOW-03, FLOW-04 e FLOW-07]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-07]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-14]`, `[T-20]`, `[T-28]`, `[T-29]`, `[T-35]`, `[T-37]`, `[T-40]`, `[T-61]`

### RF-008 Isolamento de eventos na DLQ após esgotamento das tentativas automáticas

Marcar o evento como `falhou` na fila de saída e registrá-lo na estrutura dedicada de falhas esgotadas (*Dead Letter Queue* — DLQ) quando a tentativa inicial e todas as 5 retentativas automáticas (6 disparos no total) falharem `[ADR-003]`, `[FDD: Seção 6 / FLOW-04]`, `[T-07]`, `[T-12]`, `[T-14]`, `[T-63]`.

**Fluxo principal**
1. O processador executa a 5ª retentativa automática (6º disparo total) de um evento e constata nova falha HTTP ou tempo limite de 10 segundos excedido `[ADR-003]`, `[FDD: Seção 6 / FLOW-04]`, `[T-12]`, `[T-13]`, `[T-35]`.
2. O sistema registra a 6ª tentativa malsucedida no histórico de entregas da assinatura `[FDD: Seção 6 / FLOW-04]`, `[T-29]`.
3. O sistema atualiza o evento original na fila de saída para o status `falhou` e cria o registro correspondente na fila dedicada de falhas esgotadas (DLQ), encerrando os disparos automáticos para aquele evento `[ADR-001]`, `[ADR-003]`, `[FDD: Seção 6 / FLOW-04]`, `[T-07]`, `[T-12]`, `[T-14]`, `[T-63]`.

**Fluxos alternativos e exceções**
- Uma vez marcado como `falhou` e registrado na DLQ, o evento deixa de sofrer tentativas automáticas e aguarda ação administrativa manual de replay `[ADR-003]`, `[FDD: Seção 6 / FLOW-04 e FLOW-05]`, `[T-14]`, `[T-15]`.
- Ao entrar em estado `falhou` (DLQ), o evento esgotado deixa de bloquear o envio de eventos subsequentes do mesmo pedido (`order_id`), evitando que um único evento problemático paralise indefinidamente as notificações seguintes daquele pedido `[FDD: Seção 6 / FLOW-04]`, `[T-11]`, `[T-14]`.

**Erros previstos**
- A falha da última retentativa consolida o motivo do erro e a quantidade total de 6 tentativas realizadas no registro da DLQ para inspeção e diagnóstico `[FDD: Seção 6 / FLOW-04]`, `[T-12]`, `[T-14]`, `[T-29]`.

**Prioridade:** Alta  
**Origem:** `[ADR-001]`, `[ADR-003]`, `[FDD: Seção 6 / FLOW-04 e FLOW-05]`, `[T-07]`, `[T-11]`, `[T-12]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-29]`, `[T-35]`, `[T-63]`

### RF-009 Reprocessamento manual administrativo com registro de auditoria

Permitir que um usuário autenticado com perfil `ADMIN` acione manualmente o reprocessamento (`POST /api/v1/admin/webhooks/dead-letter/:id/replay`) de um evento retido na DLQ, reativando o evento original como `pendente` com preservação do seu `event_id` e registrando em log de auditoria quem executou a ação `[ADR-003]`, `[ADR-005]`, `[ADR-006]`, `[FDD: Seção 6 / FLOW-05]`, `[T-15]`, `[T-30]`, `[T-59]`, `[T-63]`, `[T-64]`.

**Fluxo principal**
1. Um administrador autenticado com perfil `ADMIN` envia requisição para o endpoint administrativo de replay informando o identificador do registro na DLQ `[ADR-003]`, `[FDD: Seção 7]`, `[T-15]`, `[T-30]`.
2. O sistema valida a autenticação do usuário e exige obrigatoriamente o perfil `ADMIN` `[ADR-003]`, `[ADR-006]`, `[T-30]`, `[T-59]`, `[código: src/middlewares/auth.middleware.ts]`.
3. O sistema verifica que o registro da DLQ existe, que a assinatura de webhook vinculada permanece ativa e que o evento não se encontra já reenfileirado para envio `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-05 e FLOW-07]`, `[FDD: Seção 9]`, `[T-15]`, `[T-28]`, `[T-61]`.
4. O sistema reativa o evento original na fila de saída com status `pendente` e contador de tentativas reiniciado para um novo ciclo completo de envio, preservando integralmente o `event_id` (`X-Event-Id`) original e a fotografia imutável do evento `[ADR-003]`, `[ADR-005]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-05]`, `[T-15]`, `[T-20]`, `[T-40]`, `[T-63]`, `[T-64]`.
5. O sistema registra no log estruturado da aplicação um evento de auditoria identificando qual administrador acionou o reprocessamento manual e retorna confirmação ao solicitante `[ADR-003]`, `[ADR-006]`, `[FDD: Seção 6 / FLOW-05]`, `[T-24]`, `[T-30]`, `[código: src/shared/logger/index.ts]`.

**Fluxos alternativos e exceções**
- Se o usuário autenticado possuir perfil `OPERATOR` (não sendo `ADMIN`), o sistema nega a operação com erro de permissão insuficiente (403) `[ADR-003]`, `[ADR-006]`, `[T-30]`, `[T-59]`, `[código: src/middlewares/auth.middleware.ts]`.
- Conforme a Deliberação C2 da [RFC](./RFC.md), se a assinatura vinculada ao evento estiver inativa ou tiver sido removida, o sistema bloqueia o replay para impedir disparos para um endpoint desativado `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-05 e FLOW-07]`, `[T-15]`, `[T-28]`, `[T-61]`.
- Caso outros eventos posteriores do mesmo pedido já tenham sido entregues durante o período em que o evento antigo permaneceu na DLQ, o replay reenviará a fotografia imutável do evento antigo preservando seu `event_id` (`X-Event-Id`) e seu campo `timestamp` original do evento no corpo JSON, enquanto o cabeçalho HTTP `X-Timestamp` refletirá o instante da nova tentativa de disparo `[FDD: Seção 6 / FLOW-02, FLOW-04 e FLOW-05]`, `[T-11]`, `[T-15]`, `[T-36]`, `[T-37]`, `[T-40]`.

**Erros previstos**
- Usuário sem autenticação válida recebe erro 401 e usuário autenticado sem perfil `ADMIN` recebe erro 403 `[ADR-006]`, `[T-30]`, `[T-59]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/shared/errors/http-errors.ts]`.
- Registro inexistente na DLQ retorna erro padronizado `WEBHOOK_DEAD_LETTER_NOT_FOUND` (404) `[ADR-006]`, `[FDD: Seção 6 / FLOW-05]`, `[FDD: Seção 9]`, `[T-15]`, `[T-23]`.
- Tentativa de replay para assinatura inativa retorna erro `WEBHOOK_INACTIVE` (409) e tentativa de replay de evento que já está reenfileirado na fila de saída retorna erro `WEBHOOK_ALREADY_QUEUED` (409), conforme especificado na Seção 9 do [FDD](./FDD.md) `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-05]`, `[FDD: Seção 9]`, `[T-15]`, `[T-23]`, `[T-61]`.

**Prioridade:** Alta  
**Origem:** `[ADR-003]`, `[ADR-005]`, `[ADR-006]`, `[ADR-007]`, `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-02, FLOW-04, FLOW-05 e FLOW-07]`, `[FDD: Seção 7]`, `[FDD: Seção 9]`, `[T-11]`, `[T-14]`, `[T-15]`, `[T-20]`, `[T-23]`, `[T-24]`, `[T-28]`, `[T-30]`, `[T-36]`, `[T-37]`, `[T-40]`, `[T-59]`, `[T-61]`, `[T-63]`, `[T-64]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/shared/errors/http-errors.ts]`, `[código: src/shared/logger/index.ts]`

### RF-010 Consulta do histórico das últimas 100 tentativas de entrega por assinatura

Permitir que o usuário autenticado consulte os últimos 100 registros de tentativas de entrega de uma assinatura de webhook (`GET /api/v1/webhooks/:id/deliveries`), contendo indicação de sucesso ou falha, conteúdo enviado (*payload*), resposta recebida (*response*) e tempo de resposta `[FDD: Seção 7]`, `[T-29]`.

**Fluxo principal**
1. O usuário autenticado envia requisição de consulta do histórico de entregas informando o identificador da assinatura de webhook `[FDD: Seção 7]`, `[T-29]`, `[T-50]`.
2. O sistema verifica a existência da assinatura solicitada `[T-23]`, `[T-29]`.
3. O sistema recupera até os 100 registros mais recentes de tentativas de entrega realizadas para aquela assinatura, abrangendo tanto entregas bem-sucedidas (respostas `2xx`) quanto tentativas que resultaram em falha ou tempo limite excedido `[FDD: Seção 7]`, `[FDD: Seção 8]`, `[T-29]`, `[T-35]`.
4. O sistema retorna a lista ordenada das tentativas mais recentes contendo, para cada tentativa, o indicador de sucesso/falha, o conteúdo enviado, a resposta obtida do servidor de destino e o tempo de resposta em milissegundos `[FDD: Seção 7]`, `[T-29]`.

**Fluxos alternativos e exceções**
- Caso a assinatura exista mas ainda não possua nenhuma tentativa de entrega realizada, o sistema retorna uma lista vazia sem erro `[FDD: Seção 7]`, `[T-29]`.
- Caso a assinatura já tenha superado 100 tentativas ao longo do tempo, a consulta retorna exatamente as 100 tentativas mais recentes `[T-29]`.
- **Bloqueador pré-implementação (autorização multi-tenant):** Informar o identificador `:id` da assinatura na rota não é suficiente por si só para autorizar a visualização: o isolamento de acesso para garantir que um usuário consulte apenas o histórico de entregas de assinaturas do seu próprio cliente depende do modelo de autorização multi-tenant pendente de decisão pré-implementação na [RFC](./RFC.md) e na Seção 16 do [FDD](./FDD.md) `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-29]`, `[T-50]`.

**Erros previstos**
- Consulta para um identificador de assinatura inexistente retorna erro padronizado `WEBHOOK_NOT_FOUND` (404) `[ADR-006]`, `[FDD: Seção 9]`, `[T-23]`, `[T-29]`.
- Requisição sem autenticação válida é rejeitada com erro 401 `[T-50]`, `[código: src/middlewares/auth.middleware.ts]`.

**Prioridade:** Média (classificação de análise do documento por tratar-se de capacidade de visibilidade e diagnóstico complementar ao fluxo de entrega) `[T-29]`  
**Origem:** `[ADR-006]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 7]`, `[FDD: Seção 8]`, `[FDD: Seção 9]`, `[FDD: Seção 16]`, `[T-23]`, `[T-27]`, `[T-29]`, `[T-35]`, `[T-50]`, `[código: src/middlewares/auth.middleware.ts]`

---

## 7. Requisitos não funcionais

| ID | Categoria | Requisito | Origem |
| :--- | :--- | :--- | :--- |
| RNF-001 | Desempenho | As notificações de mudança de status devem ter meta operacional de entrega inferior a 10 segundos no fluxo nominal (quando o endpoint do cliente responde prontamente na primeira tentativa), apoiada por verificação assíncrona de eventos pendentes a cada 2 segundos | `[ADR-002]`, `[T-02]`, `[T-07]`, `[T-08]` |
| RNF-002 | Desempenho | Cada chamada HTTP de notificação para o endpoint de um cliente deve ter tempo limite (*timeout*) máximo de 10 segundos; respostas HTTP na faixa `2xx` (`200`–`299`) dentro desse prazo contam como sucesso, enquanto *timeouts*, falhas de rede ou respostas fora de `2xx` devem ser tratadas como falha sujeita à política de retentativas | `[ADR-003]`, `[FDD: Seção 8]`, `[T-12]`, `[T-35]` |
| RNF-003 | Desempenho | O tamanho do conteúdo (*payload*) de cada evento de notificação não pode exceder 64 KB (`65.536 bytes` em UTF-8), sendo proibido truncar o conteúdo e devendo o excesso resultar em erro e reversão integral (*rollback*) da transação de mudança de status | `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-19]`, `[T-45]` |
| RNF-004 | Segurança | **Comportamento já definido:** Todas as URLs cadastradas ou editadas para assinaturas de webhook devem utilizar obrigatoriamente o protocolo HTTPS, com validação sintática na entrada. **Proposta técnica ainda não aprovada (bloqueador pré-implementação):** controles anti-SSRF no cadastro e na resolução DNS do envio (especificados na Seção 8 do [FDD](./FDD.md)) aguardam aprovação formal da engenharia de segurança antes da implementação | `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-18]`, `[T-38.1]`, `[código: src/middlewares/validate.middleware.ts]` |
| RNF-005 | Segurança | **Comportamento já definido:** Todas as notificações enviadas devem conter assinatura criptográfica HMAC-SHA256 no cabeçalho `X-Signature` calculada sobre o corpo da requisição HTTP (`payload`, conforme decisão congelada no [ADR-004](./adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md)) usando chave secreta exclusiva por endpoint, acompanhada dos cabeçalhos `X-Timestamp` (instante da tentativa de disparo HTTP, distinto do `timestamp` original do evento no JSON e não protegido criptograficamente pelo HMAC no contrato vigente), `X-Event-Id` e `X-Webhook-Id`, suportando rotação de chave com validade simultânea da chave antiga por 24 horas. **Proposta técnica ainda não aprovada (pendente pré-implementação):** codificação textual de `X-Signature` e mecanismo de coexistência de assinaturas durante a janela de 24 horas (especificados na Seção 8 do [FDD](./FDD.md)) aguardam ratificação formal de segurança; eventual mudança para assinar `${timestamp}.${payload}` exigiria revisão formal do ADR-004 | `[ADR-004]`, `[ADR-005]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 6 / FLOW-06]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-20]`, `[T-36]`, `[T-37]`, `[T-49]`, `[T-54]` |
| RNF-006 | Segurança | **Comportamento já definido:** O endpoint de replay manual da DLQ deve exigir exclusivamente o perfil `ADMIN`. **Bloqueador pré-implementação:** embora a reunião tenha registrado abertura inicial do CRUD a qualquer perfil autenticado (`[T-50]`) e que `customer_id` não vem do JWT (`[T-27]`), informar `customer_id` na requisição não autoriza por si só o acesso ao tenant, sendo obrigatório fechar o modelo de autorização e isolamento multi-tenant entre usuários e clientes antes da implementação. **Proposta técnica ainda não aprovada (pendente pré-implementação):** proteção criptográfica das chaves secretas em repouso e ampliação do mascaramento de segredos nos logs para ocultar `secret` e `X-Signature` (especificadas nas Seções 5, 11 e 12 do [FDD](./FDD.md)) aguardam aprovação formal de segurança | `[ADR-003]`, `[ADR-004]`, `[ADR-006]`, `[RFC: Impacto e riscos]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-17]`, `[T-24]`, `[T-27]`, `[T-30]`, `[T-50]`, `[T-59]`, `[T-61]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/shared/logger/index.ts]` |
| RNF-007 | Segurança | **Requisito obrigatório pré-deploy (ainda não realizado):** A entrada em produção depende obrigatoriamente de uma janela prévia de 2 dias úteis reservada para revisão de segurança do código implementado conduzida pela engenharia de segurança (Sofia) | `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-38.1]`, `[T-65]` |
| RNF-008 | Confiabilidade | A gravação do evento de notificação na fila de saída deve ser atômica em relação à mudança de status do pedido no banco de dados: se a validação ou gravação do evento falhar, a mudança de status sofre reversão integral (*rollback*) | `[ADR-001]`, `[RFC: Deliberação A1]`, `[T-05]`, `[T-34]`, `[código: src/modules/orders/order.service.ts]` |
| RNF-009 | Confiabilidade | O sistema deve operar sob garantia de entrega "pelo menos uma vez" (*at-least-once*) enviando o identificador único `X-Event-Id` (UUID) em todas as chamadas, executando 1 tentativa inicial e até 5 retentativas automáticas (máximo de 6 disparos HTTP automáticos) nos intervalos `1m, 5m, 30m, 2h, 12h`, mantendo o evento esgotado como `falhou` na fila de saída e registrando-o na DLQ para replay manual com preservação do `event_id` original | `[ADR-003]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-03, FLOW-04 e FLOW-05]`, `[T-07]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-20]`, `[T-37]`, `[T-63]`, `[T-64]` |
| RNF-010 | Confiabilidade | O processador de envios deve executar em processo separado da API HTTP com encerramento gracioso e deve preservar a ordem de entrega dos eventos por pedido (`order_id`) em instância única enquanto os eventos estiverem pendentes ou em ciclo de retentativas automáticas (sem garantia de ordenação global entre pedidos distintos e com a ressalva de que eventos esgotados na DLQ desbloqueiam eventos seguintes do mesmo pedido, podendo ser reprocessados posteriormente via replay manual) | `[ADR-002]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02, FLOW-04 e FLOW-05]`, `[T-10]`, `[T-11]`, `[T-14]`, `[T-15]`, `[T-25]`, `[T-58]`, `[código: src/server.ts]` |
| RNF-011 | Observabilidade | O sistema deve reutilizar o logger estruturado da aplicação, registrar em log de auditoria o usuário `ADMIN` que acionar o replay manual da DLQ e disponibilizar os últimos 100 registros de tentativas de entrega por assinatura (métricas de telemetria e *tracing* distribuído não estão na transcrição) | `[ADR-003]`, `[ADR-006]`, `[T-24]`, `[T-29]`, `[T-30]`, `[código: src/shared/logger/index.ts]`, `[código: package.json]` |
| RNF-012 | Compatibilidade | O novo módulo deve seguir os padrões arquiteturais já adotados no repositório (organização modular, rotas sob `/api/v1`, erros de domínio padronizados com prefixo `WEBHOOK_`, tratamento centralizado de erros, validação com Zod e identificadores em UUID, conforme detalhado na Seção 12 do [FDD](./FDD.md)) | `[ADR-001]`, `[ADR-006]`, `[FDD: Seção 12]`, `[T-18]`, `[T-21]`, `[T-23]`, `[T-24]`, `[T-25]`, `[T-39]`, `[T-48]`, `[T-57]`, `[T-58]`, `[T-59]`, `[código: src/app.ts]`, `[código: src/routes/index.ts]`, `[código: src/middlewares/error.middleware.ts]`, `[código: src/shared/errors/app-error.ts]`, `[código: prisma/schema.prisma]` |

---

## 8. Decisões e trade-offs principais

- **Registrar os eventos de notificação de forma atômica na mesma transação da mudança de status do pedido, filtrando apenas assinaturas ativas que monitoram o novo status**
  - **Justificativa:** Garante que nenhum pedido mude de status sem que a notificação correspondente seja registrada para envio e evita gravar eventos desnecessários para status não monitorados, sem depender da disponibilidade imediata do servidor do cliente nem exigir nova infraestrutura de mensageria `[ADR-001]`, `[T-05]`, `[T-34]`, `[T-51]`.
  - **Trade-off:** Adiciona a verificação de assinaturas e o registro do evento à transação de mudança de status e acumula registros entregues no banco enquanto não houver rotina de arquivamento `[ADR-001]`, `[T-05]`, `[T-07]`, `[T-47]`, `[T-51]`, `[código: src/modules/orders/order.service.ts]`.
  - **Detalhe:** [ADR-001](./adrs/ADR-001-outbox-transacional-no-mysql.md) `[ADR-001]`, `[T-05]`

- **Executar o processador de envios em processo separado da API, verificando eventos pendentes a cada 2 segundos em instância única**
  - **Justificativa:** Impede que reinicializações da API interrompam o envio de webhooks, viabiliza a meta operacional inferior a 10 segundos no fluxo nominal sem infraestrutura extra e preserva a ordenação de entrega por pedido (`order_id`) durante o ciclo ativo de envio `[ADR-002]`, `[T-02]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-25]`.
  - **Trade-off:** Introduz um segundo processo para operar e monitorar, realiza consultas periódicas a cada 2 segundos e restringe a ordenação ao escopo de cada pedido individual em processador único `[ADR-002]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-11]`.
  - **Detalhe:** [ADR-002](./adrs/ADR-002-worker-separado-com-polling.md) `[ADR-002]`, `[T-08]`, `[T-10]`

- **Realizar 1 tentativa inicial e até 5 retentativas escalonadas (`1m, 5m, 30m, 2h, 12h`) com timeout de 10 segundos por chamada e isolar falhas esgotadas em DLQ com replay manual restrito a `ADMIN`**
  - **Justificativa:** Absorve desde oscilações rápidas de rede até janelas planejadas de manutenção nos clientes (cobrindo quase 15 horas em até 6 disparos automáticos) sem travar o processador em chamadas lentas, preservando eventos não entregues para reprocessamento administrativo auditado `[ADR-003]`, `[FDD: Seção 6 / FLOW-03 e FLOW-04]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-30]`, `[T-35]`.
  - **Trade-off:** Exige manter uma fila dedicada de falhas esgotadas e operação manual de replay após o 6º disparo sem sucesso; além disso, eventos esgotados na DLQ desbloqueiam eventos posteriores do mesmo pedido, podendo ser reprocessados depois de transições mais recentes `[ADR-003]`, `[FDD: Seção 6 / FLOW-04 e FLOW-05]`, `[T-11]`, `[T-14]`, `[T-15]`, `[T-30]`.
  - **Detalhe:** [ADR-003](./adrs/ADR-003-retry-com-backoff-e-dlq.md) `[ADR-003]`, `[T-12]`, `[T-14]`, `[T-15]`

- **Assinar o corpo de cada notificação com HMAC-SHA256 usando chave secreta exclusiva por endpoint, exigir HTTPS e suportar rotação de chave com janela de 24 horas**
  - **Justificativa:** Garante ao cliente receptor que a notificação foi emitida pelo OMS e que seu corpo não foi adulterado em trânsito (acompanhado do cabeçalho `X-Timestamp` como referência temporal da tentativa de disparo), isola o impacto caso a credencial de um endpoint seja comprometida e permite substituir chaves sem interromper a integração `[ADR-004]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-37]`, `[T-49]`, `[T-61]`.
  - **Trade-off:** Aumenta a complexidade de gestão do ciclo de vida de credenciais (mantendo chave atual e anterior válidas por 24 horas), não protege criptograficamente o cabeçalho `X-Timestamp` quando o HMAC incide apenas sobre o corpo e exige controles adicionais de proteção em repouso, mascaramento de logs e revisão de segurança dedicada `[ADR-004]`, `[T-16]`, `[T-17]`, `[T-24]`, `[T-37]`, `[T-38.1]`, `[T-49]`, `[T-61]`.
  - **Detalhe:** [ADR-004](./adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) `[ADR-004]`, `[T-16]`, `[T-17]`, `[T-18]`

- **Adotar semântica de entrega "pelo menos uma vez" (*at-least-once*) com envio e preservação do identificador único do evento (`X-Event-Id`)**
  - **Justificativa:** Viabiliza confirmação confiável de entrega sobre chamadas HTTP externas sujeitas a quedas de conexão e *timeouts*, fornecendo ao cliente um identificador único (UUID) estável inclusive em retentativas e replays manuais para descartar duplicatas `[ADR-005]`, `[FDD: Seção 6 / FLOW-05]`, `[T-20]`, `[T-37]`, `[T-64]`.
  - **Trade-off:** Transfere aos sistemas receptores dos clientes B2B a responsabilidade de implementar tratamento idempotente de eventos duplicados, exigindo documentação clara no portal de desenvolvedor `[ADR-005]`, `[T-20]`, `[T-54]`.
  - **Detalhe:** [ADR-005](./adrs/ADR-005-entrega-at-least-once-com-event-id.md) `[ADR-005]`, `[T-20]`, `[T-37]`

- **Construir o módulo de webhooks reutilizando os padrões e convenções existentes na plataforma**
  - **Justificativa:** Reduz o risco de entrega dentro do prazo comercial de 3 sprints ao reaproveitar a estrutura modular, o padrão de erros `WEBHOOK_`, o logger estruturado, a validação de entrada e a autorização por perfil (`ADMIN`) já consolidados no projeto `[ADR-006]`, `[T-18]`, `[T-21]`, `[T-23]`, `[T-24]`, `[T-25]`, `[T-38]`, `[T-48]`, `[T-57]`, `[T-58]`, `[T-59]`.
  - **Trade-off:** Exige adequar o mascaramento de segredos nos logs e fechar a decisão de negócio/segurança sobre o isolamento multi-tenant entre usuários autenticados e `customer_id`, que não existe hoje no modelo atual `[ADR-006]`, `[RFC: Impacto e riscos]`, `[T-24]`, `[T-27]`, `[T-50]`, `[código: prisma/schema.prisma]`, `[código: src/shared/logger/index.ts]`.
  - **Detalhe:** [ADR-006](./adrs/ADR-006-reuso-dos-padroes-do-projeto.md) `[ADR-006]`, `[T-21]`, `[T-48]`

- **Gravar o conteúdo do evento como fotografia imutável (*snapshot*) no momento da mudança de status, sem lista de itens e com limite máximo de 64 KB (`65.536 bytes`)**
  - **Justificativa:** Preserva os dados exatos da transição de status no instante em que ela ocorreu (mesmo que o pedido sofra novas alterações antes do envio ou durante retentativas) e mantém o pacote enxuto ao omitir os itens do pedido `[ADR-007]`, `[T-19]`, `[T-36]`, `[T-40]`.
  - **Trade-off:** Clientes que necessitarem dos itens detalhados do pedido precisam consultá-los separadamente na API (`GET /api/v1/orders/:id`), e qualquer evento que ultrapasse `65.536 bytes` é rejeitado com erro e reversão integral da transação de mudança de status conforme a Deliberação A1 da [RFC](./RFC.md) `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-19]`, `[T-36]`, `[T-40]`, `[T-45]`, `[código: src/modules/orders/order.routes.ts]`.
  - **Detalhe:** [ADR-007](./adrs/ADR-007-payload-snapshot-e-limite-de-64kb.md) `[ADR-007]`, `[T-19]`, `[T-36]`, `[T-40]`

---

## 9. Dependências

| Tipo | Dependência | Impacto se faltar | Origem |
| :--- | :--- | :--- | :--- |
| Externa | Disponibilidade de endpoints HTTPS nos sistemas dos clientes B2B (Atlas, MaxDistribuição e Nova Cargo) respondendo com status `2xx` em até 10 segundos e implementação, pelo receptor, da validação de assinatura (`X-Signature`) e da desduplicação por `X-Event-Id` | Sem endpoints HTTPS válidos ou sem tratamento de idempotência no cliente, as entregas falharão até a DLQ ou poderão gerar processamento duplicado no sistema do cliente em retentativas | `[ADR-004]`, `[ADR-005]`, `[FDD: Seção 8]`, `[T-01]`, `[T-16]`, `[T-18]`, `[T-20]`, `[T-35]`, `[T-54]` |
| Organizacional | Atualização do portal de desenvolvedor documentando o contrato do webhook, os cabeçalhos enviados, o comportamento na rotação de chave de 24h, a garantia *at-least-once* e a deduplicação obrigatória pelo `X-Event-Id` | Clientes integradores podem assumir entrega única ou falhar na validação de assinaturas durante a rotação de credenciais | `[ADR-004]`, `[ADR-005]`, `[T-17]`, `[T-20]`, `[T-37]`, `[T-54]` |
| Organizacional | Decisão de negócio e segurança sobre o modelo de autorização e isolamento multi-tenant entre usuários autenticados (`User`) e clientes (`Customer` / `customer_id`) antes do início da implementação | Bloqueio do início da implementação ou risco de acesso cruzado indevido entre clientes na gestão de assinaturas e consulta de entregas | `[ADR-006]`, `[RFC: Impacto e riscos]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`, `[T-62]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]` |
| Organizacional | Aprovação formal pré-implementação pela engenharia de segurança (Sofia) das especificações técnicas propostas no [FDD](./FDD.md) para anti-SSRF, proteção de credenciais em repouso, mascaramento de segredos em logs, codificação textual de `X-Signature` e formato de coexistência de chaves na janela de rotação de 24h | Impossibilidade de iniciar a implementação dos controles críticos de segurança com conformidade validada | `[ADR-004]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[T-37]`, `[T-38.1]`, `[código: src/shared/logger/index.ts]` |
| Organizacional | Alocação obrigatória de 2 dias úteis da engenharia de segurança (Sofia) para revisão do código antes do deploy em produção e revisão do design doc pela liderança técnica (Larissa, Diego e Bruno) | Impossibilidade de liberar a funcionalidade em produção dentro do prazo comercial do fim de novembro | `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-38.1]`, `[T-53]`, `[T-65]` |
| Técnica | Fluxo transacional existente de mudança de status de pedidos e máquina de estados de pedidos no OMS | Sem o fluxo transacional único de mudança de status, não é possível garantir a captura atômica de todos os eventos de transição | `[ADR-001]`, `[T-05]`, `[T-34]`, `[T-56]`, `[código: src/modules/orders/order.service.ts]`, `[código: src/modules/orders/order.status.ts]` |
| Técnica | Infraestrutura compartilhada existente da aplicação: autenticação JWT e controle de perfil `ADMIN`, validação de schemas, tratamento padronizado de erros e logger estruturado | Necessária para cumprir a diretriz de reuso arquitetural do projeto, a proteção da rota administrativa de replay e o registro de auditoria | `[ADR-006]`, `[T-18]`, `[T-23]`, `[T-24]`, `[T-25]`, `[T-30]`, `[T-48]`, `[T-57]`, `[T-59]`, `[código: src/middlewares/auth.middleware.ts]`, `[código: src/middlewares/error.middleware.ts]`, `[código: src/middlewares/validate.middleware.ts]`, `[código: src/shared/errors/app-error.ts]`, `[código: src/shared/logger/index.ts]` |

---

## 10. Riscos e mitigação

### Risco 1: Perda do cliente Atlas por atraso na entrega além do fim de novembro
- **Probabilidade:** Média *(análise/proposta do documento com base no prazo estimado de 3 sprints mais os bloqueadores pré-implementação e os 2 dias úteis de revisão de segurança pré-deploy)* `[T-38]`, `[T-38.1]`
- **Impacto:** Alto *(análise/proposta do documento com base na ameaça explícita de migração para concorrente até o fim do trimestre/novembro)* `[T-52]`, `[T-53]`
- **Mitigação:** Manter o escopo enxuto reutilizando os padrões e o banco de dados existentes no projeto (3 sprints estimadas), destravar imediatamente as aprovações pré-implementação de segurança/multi-tenancy e reservar com antecedência os 2 dias úteis de revisão de segurança com Sofia `[ADR-001]`, `[ADR-006]`, `[RFC: Critérios de aprovação]`, `[T-05]`, `[T-38]`, `[T-38.1]`, `[T-48]`, `[T-52]`, `[T-53]`, `[T-65]`.
- **Plano de contingência:** Priorizar a homologação assistida com a equipe técnica da Atlas assim que o fluxo principal de envio assíncrono e validação HMAC estiver operacional, mantendo acompanhamento direto pelo Product Owner (Marcos) `[T-01]`, `[T-52]`, `[T-53]`.
- **Origem:** `[ADR-001]`, `[ADR-006]`, `[RFC: Critérios de aprovação]`, `[T-01]`, `[T-38]`, `[T-38.1]`, `[T-52]`, `[T-53]`, `[T-65]`

### Risco 2: Processamento duplicado de eventos nos sistemas dos clientes B2B
- **Probabilidade:** Alta *(análise/proposta do documento, pois retentativas após timeouts de 10s, oscilações de rede ou replays manuais mantendo o mesmo `event_id` são inerentes ao modelo at-least-once)* `[ADR-005]`, `[FDD: Seção 6 / FLOW-05]`, `[T-12]`, `[T-20]`, `[T-35]`, `[T-64]`
- **Impacto:** Médio *(análise/proposta do documento, podendo causar inconsistências no sistema receptor caso o cliente não descarte duplicatas)* `[T-20]`, `[T-54]`
- **Mitigação:** Incluir obrigatoriamente um identificador único por evento (`X-Event-Id` no cabeçalho e `event_id` no corpo) preservado em todas as retentativas e replays, e documentar com destaque no portal de desenvolvedor a responsabilidade de desduplicação pelo cliente receptor `[ADR-005]`, `[FDD: Seção 6 / FLOW-05]`, `[T-20]`, `[T-36]`, `[T-37]`, `[T-54]`, `[T-64]`.
- **Plano de contingência:** Utilizar o histórico das últimas 100 entregas (`GET /api/v1/webhooks/:id/deliveries`) para apoiar o diagnóstico junto ao cliente e orientar a implementação do filtro de idempotência pelo `X-Event-Id` `[FDD: Seção 7]`, `[T-20]`, `[T-29]`, `[T-54]`.
- **Origem:** `[ADR-005]`, `[FDD: Seção 6 / FLOW-05]`, `[FDD: Seção 7]`, `[T-20]`, `[T-29]`, `[T-35]`, `[T-36]`, `[T-37]`, `[T-54]`, `[T-64]`

### Risco 3: Acesso cruzado entre clientes na gestão de assinaturas e consulta de entregas (Isolamento multi-tenant pendente)
- **Probabilidade:** Alta *(análise/proposta do documento enquanto a decisão de isolamento estiver pendente, pois o `customer_id` não vem do JWT, a reunião deixou o CRUD aberto a qualquer role autenticada inicialmente e não há relação entre `User` e `Customer` no banco atual)* `[T-27]`, `[T-50]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`
- **Impacto:** Alto *(análise/proposta do documento, pois permitiria a um usuário autenticado visualizar, alterar ou desativar assinaturas e consultar entregas de outro cliente)* `[T-27]`, `[T-28]`, `[T-29]`, `[T-50]`
- **Mitigação:** Manter o fechamento do modelo de autorização e isolamento por `customer_id` como bloqueador obrigatório pré-implementação (conforme [RFC](./RFC.md) e Seção 16 do [FDD](./FDD.md)) e validar a implementação durante a revisão de segurança pré-deploy de 2 dias úteis `[RFC: Impacto e riscos]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-38.1]`, `[T-50]`, `[T-62]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`.
- **Plano de contingência:** Caso o vínculo formal entre usuários externos e `customer_id` não seja aprovado a tempo no modelo de dados, restringir a operação das rotas de webhooks exclusivamente a operadores internos autorizados da plataforma até a evolução do modelo de autenticação `[RFC: Questões em aberto]`, `[FDD: Seção 16]`, `[T-30]`, `[T-50]`, `[código: src/middlewares/auth.middleware.ts]`.
- **Origem:** `[RFC: Impacto e riscos]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-30]`, `[T-38.1]`, `[T-50]`, `[T-62]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`

### Risco 4: Latência superior a 10s em falhas externas e entrega fora de ordem em replay tardio da DLQ
- **Probabilidade:** Média *(análise/proposta do documento, dado que endpoints externos podem demorar até 10 segundos para falhar, acionar retentativas de 1m a 12h ou esgotar para a DLQ enquanto o pedido continua avançando)* `[T-08]`, `[T-10]`, `[T-13]`, `[T-14]`, `[T-35]`
- **Impacto:** Médio *(análise/proposta do documento, podendo postergar entregas de endpoints instáveis e fazer com que um replay manual tardio ocorra após eventos mais novos do mesmo pedido)* `[FDD: Seção 6 / FLOW-04 e FLOW-05]`, `[T-02]`, `[T-11]`, `[T-13]`, `[T-15]`
- **Mitigação:** Aplicar tempo limite estrito de 10 segundos por chamada HTTP, manter os eventos do mesmo pedido sequenciados durante o ciclo ativo de retentativas e enviar o `timestamp` original do evento e os status de origem/destino (`from_status`, `to_status`) no *snapshot* JSON (além do `X-Timestamp` do disparo no cabeçalho HTTP) para que o cliente reconheça a cronologia real mesmo em caso de replay tardio da DLQ `[ADR-003]`, `[ADR-005]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-02, FLOW-04 e FLOW-05]`, `[T-02]`, `[T-11]`, `[T-13]`, `[T-35]`, `[T-36]`, `[T-37]`, `[T-40]`.
- **Plano de contingência:** Consultar o histórico das últimas 100 entregas para diagnosticar endpoints lentos e coordenar com o cliente antes de acionar o replay administrativo na DLQ `[T-14]`, `[T-15]`, `[T-29]`, `[T-30]`.
- **Origem:** `[ADR-003]`, `[ADR-005]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-02, FLOW-04 e FLOW-05]`, `[T-02]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-13]`, `[T-14]`, `[T-15]`, `[T-29]`, `[T-30]`, `[T-35]`, `[T-36]`, `[T-37]`, `[T-40]`

### Risco 5: Exposição de credenciais secretas ou uso de URLs externas para chamadas indevidas à rede interna (SSRF)
- **Probabilidade:** Média *(análise/proposta do documento, visto que a configuração atual do logger não mascara `secret`/`X-Signature` e a validação apenas de esquema HTTPS não bloqueia endereços IP internos por si só)* `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[código: src/shared/logger/index.ts]`
- **Impacto:** Alto *(análise/proposta do documento, por envolver comprometimento de credenciais de assinatura de clientes ou acesso indevido a serviços internos)* `[T-17]`, `[T-18]`, `[T-38.1]`
- **Mitigação:** Obter a aprovação formal da engenharia de segurança sobre as propostas técnicas do [FDD](./FDD.md) (proteção de credenciais em repouso nas Seções 5 e 12, mascaramento de `secret` e `X-Signature` nos logs nas Seções 11 e 12 e validação anti-SSRF no cadastro e na resolução DNS do envio na Seção 8) antes da implementação, além de cumprir os 2 dias úteis obrigatórios de revisão de segurança pré-deploy por Sofia `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[T-38.1]`, `[T-61]`, `[código: src/shared/logger/index.ts]`.
- **Plano de contingência:** Acionar imediatamente a rotação da credencial secreta da assinatura afetada pela API e desativar assinaturas que apontem para endereços suspeitos ou inválidos `[ADR-004]`, `[T-17]`, `[T-28]`, `[T-49]`, `[T-61]`.
- **Origem:** `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[T-28]`, `[T-38.1]`, `[T-49]`, `[T-61]`, `[código: src/shared/logger/index.ts]`

---

## 11. Critérios de aceitação

- [ ] O cadastro de uma assinatura de webhook com URL HTTPS válida e lista de status monitorados (`PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`) persiste a assinatura ativa associada ao `customer_id` e retorna a chave secreta exclusiva gerada (RF-001, RNF-004, RNF-005) `[ADR-004]`, `[RFC: Deliberação B1]`, `[FDD: Seção 7]`, `[T-17]`, `[T-18]`, `[T-26]`, `[T-61]`, `[código: src/modules/orders/order.status.ts]`.
- [ ] O cadastro ou a atualização de uma assinatura informando URL com protocolo `http://` ou formato inválido é rejeitado com erro padronizado `WEBHOOK_INVALID_URL` e não persiste a alteração (RF-001, RF-002, RNF-004, RNF-012) `[ADR-004]`, `[ADR-006]`, `[T-18]`, `[T-23]`.
- [ ] As operações de listagem/consulta (`GET`), edição (`PATCH` de URL HTTPS, status monitorados e estado ativo) e remoção (`DELETE`) de assinaturas refletem o estado atualizado, ocultam a chave secreta nas leituras, retornam `WEBHOOK_NOT_FOUND` quando o identificador não existir e respeitam a Deliberação C2 da [RFC](./RFC.md): a edição de status monitorados afeta apenas novas mudanças de status, a edição de URL aplica-se a envios pendentes e a desativação/remoção interrompe envios pendentes e bloqueia replay na DLQ (RF-002, RF-009, RNF-012) `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-07]`, `[FDD: Seção 7]`, `[T-23]`, `[T-28]`, `[T-51]`, `[T-61]`.
- [ ] A solicitação de rotação de credencial secreta pela API gera e retorna uma nova chave secreta para a assinatura, mantendo a chave anterior válida em paralelo durante a janela de tolerância de 24 horas (RF-003, RNF-005) `[ADR-004]`, `[FDD: Seção 6 / FLOW-06]`, `[T-17]`, `[T-49]`.
- [ ] Ao alterar o status de um pedido para um status monitorado por uma assinatura ativa do respectivo cliente, um evento `pendente` com identificador único UUID (`event_id`) e fotografia imutável dos 13 campos especificados no [FDD](./FDD.md) (metadados do evento com `timestamp` original da transição e dados básicos do pedido sem a lista de itens) é gravado na mesma transação da mudança de status, enquanto a criação inicial do pedido (`PENDING`) não gera evento (RF-004, RNF-008, RNF-012) `[ADR-001]`, `[ADR-007]`, `[RFC: Deliberação B1]`, `[FDD: Seção 6 / FLOW-01]`, `[T-05]`, `[T-34]`, `[T-36]`, `[T-39]`, `[T-40]`, `[T-51]`, `[código: src/modules/orders/order.service.ts]`.
- [ ] Ao alterar o status de um pedido para um status que não esteja na lista monitorada da assinatura do cliente, ou quando a assinatura estiver inativa, nenhum evento é gravado para aquela assinatura (RF-004) `[ADR-001]`, `[T-51]`, `[T-61]`.
- [ ] Se a transação de mudança de status falhar (por transição inválida, estoque insuficiente ou falha na gravação do evento na fila de saída), nem a mudança de status do pedido nem o evento de notificação são confirmados no banco de dados (RF-004, RNF-008) `[ADR-001]`, `[T-05]`, `[T-34]`, `[T-56]`, `[T-57]`, `[código: src/modules/orders/order.service.ts]`.
- [ ] Um evento cuja fotografia de dados ultrapasse o limite de 64 KB (`65.536 bytes` em UTF-8) é rejeitado com erro (`WEBHOOK_PAYLOAD_TOO_LARGE`), sem truncar o conteúdo e revertendo integralmente a transação de mudança de status do pedido conforme a Deliberação A1 da [RFC](./RFC.md) (RF-005, RNF-003, RNF-008) `[ADR-007]`, `[RFC: Deliberação A1]`, `[FDD: Seção 6 / FLOW-01]`, `[FDD: Seção 9]`, `[T-05]`, `[T-19]`, `[T-45]`.
- [ ] O processador de envios executa em processo separado da API principal, verifica eventos pendentes a cada 2 segundos, dispara requisições HTTP para a URL HTTPS da assinatura contendo os cabeçalhos `X-Signature` (HMAC-SHA256 calculado sobre o corpo `payload`), `X-Event-Id` (UUID), `X-Timestamp` (instante do disparo HTTP), `X-Webhook-Id` e `Content-Type: application/json`, e marca o evento como `entregue` ao receber resposta HTTP `2xx` em até 10 segundos (RF-006, RNF-001, RNF-002, RNF-005, RNF-009, RNF-010) `[ADR-002]`, `[ADR-004]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02]`, `[FDD: Seção 8]`, `[T-07]`, `[T-08]`, `[T-10]`, `[T-16]`, `[T-20]`, `[T-35]`, `[T-37]`.
- [ ] Múltiplas mudanças de status de um mesmo pedido (`order_id`) são entregues pelo processador único na mesma ordem em que ocorreram enquanto os eventos estiverem pendentes ou em ciclo de retentativas automáticas, liberando eventos subsequentes apenas se um evento anterior esgotar todas as retentativas e for movido para a DLQ (RF-006, RF-008, RNF-010) `[ADR-002]`, `[ADR-005]`, `[FDD: Seção 6 / FLOW-02 e FLOW-04]`, `[T-11]`, `[T-14]`.
- [ ] Quando o endpoint de destino não responde em até 10 segundos (*timeout*), ocorre erro de comunicação ou retorna status HTTP fora da faixa `2xx`, a tentativa é registrada como falha no histórico da assinatura e o evento cumpre até 5 retentativas automáticas após a tentativa inicial (máximo de 6 disparos HTTP automáticos) nos intervalos de `1m, 5m, 30m, 2h e 12h` (RF-006, RF-007, RNF-002, RNF-009) `[ADR-003]`, `[FDD: Seção 6 / FLOW-03]`, `[FDD: Seção 8]`, `[T-12]`, `[T-12.1]`, `[T-13]`, `[T-29]`, `[T-35]`.
- [ ] Quando a 5ª retentativa automática (6º disparo total) falha, o evento permanece na fila de saída com status `falhou`, é registrado na estrutura dedicada de DLQ e deixa de sofrer disparos automáticos (RF-008, RNF-009) `[ADR-003]`, `[FDD: Seção 6 / FLOW-04]`, `[T-07]`, `[T-12]`, `[T-14]`, `[T-63]`.
- [ ] Uma chamada autenticada com perfil `ADMIN` para o endpoint administrativo de replay da DLQ reativa o evento original na fila de saída como `pendente` preservando seu `event_id` (`X-Event-Id`) e `timestamp` original no *snapshot* e grava log de auditoria identificando o administrador responsável; chamadas de usuários sem perfil `ADMIN` (ex.: `OPERATOR`) são negadas com erro 403, registros inexistentes na DLQ retornam `WEBHOOK_DEAD_LETTER_NOT_FOUND` (404) e replays de assinaturas inativas ou eventos já enfileirados retornam 409 (`WEBHOOK_INACTIVE` / `WEBHOOK_ALREADY_QUEUED`) (RF-009, RNF-006, RNF-009, RNF-011) `[ADR-003]`, `[ADR-005]`, `[ADR-006]`, `[RFC: Deliberação C2]`, `[FDD: Seção 6 / FLOW-05]`, `[FDD: Seção 9]`, `[T-15]`, `[T-20]`, `[T-23]`, `[T-30]`, `[T-59]`, `[T-61]`, `[T-63]`, `[T-64]`, `[código: src/middlewares/auth.middleware.ts]`.
- [ ] A consulta ao histórico de entregas de uma assinatura retorna até os 100 registros mais recentes de tentativas de envio, apresentando para cada tentativa o indicador de sucesso/falha, o conteúdo enviado, a resposta recebida e o tempo de resposta (RF-010, RNF-011) `[FDD: Seção 7]`, `[T-29]`.
- [ ] Credenciais secretas de assinaturas (`secret`) e cabeçalhos `X-Signature` não são exibidos em texto claro nos logs gerados pela aplicação e pelo processador, e os pré-requisitos de segurança da [RFC](./RFC.md) (autorização multi-tenant por cliente, anti-SSRF, proteção de segredos em repouso e revisão de 2 dias úteis por Sofia) são cumpridos antes da entrada em produção (RNF-004, RNF-005, RNF-006, RNF-007, RNF-011) `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[T-27]`, `[T-38.1]`, `[T-50]`, `[código: src/shared/logger/index.ts]`.

---

## 12. Estratégia de testes e validação

### Tipos de teste

- **Unitários:** Validação das regras de aceitação e rejeição de URLs (obrigatoriedade de HTTPS), cálculo e verificação da assinatura criptográfica HMAC-SHA256 sobre o corpo da requisição (incluindo a janela de tolerância de 24 horas na rotação de chave), validação do limite máximo de 64 KB (`65.536 bytes` em UTF-8) sem truncamento, filtragem de status monitorados por assinatura ativa e cálculo dos 5 intervalos progressivos de retentativa (`1m, 5m, 30m, 2h, 12h`, totalizando até 6 disparos automáticos) `[ADR-003]`, `[ADR-004]`, `[ADR-007]`, `[FDD: Seção 6 / FLOW-01 e FLOW-03]`, `[FDD: Seção 8]`, `[T-12.1]`, `[T-13]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-19]`, `[T-51]`.
- **Integração:** Verificação contra o banco de dados real da atomicidade entre a mudança de status do pedido e a gravação do evento (incluindo reversão integral da mudança de status em caso de erro de estoque, transição inválida, falha na fila de saída ou excesso do limite de `65.536 bytes` conforme Deliberação A1 da [RFC](./RFC.md)), ausência de emissão de evento na criação inicial do pedido (Deliberação B1), regras de ciclo de vida da assinatura (Deliberação C2), operações completas de cadastro, consulta, edição, rotação de chave e remoção de assinaturas, ciclo de coleta e envio pelo processador com sucesso em respostas `2xx`, manutenção de status `falhou` na fila de saída e registro na DLQ após a 5ª retentativa sem sucesso, consulta das últimas 100 entregas e replay administrativo reativando o evento original com preservação do `event_id` `[RFC: Deliberações A1, B1 e C2]`, `[FDD: Seção 6 / FLOW-01 a FLOW-07]`, `[FDD: Seção 8]`, `[T-05]`, `[T-07]`, `[T-14]`, `[T-15]`, `[T-19]`, `[T-20]`, `[T-26]`, `[T-28]`, `[T-29]`, `[T-49]`, `[T-56]`, `[T-63]`, `[T-64]`, `[código: tests/orders.test.ts]`, `[código: tests/setup.ts]`.
- **Segurança:** Verificação da exigência de autenticação em todas as rotas de webhooks, bloqueio de usuários sem perfil `ADMIN` no endpoint de replay da DLQ (403), registro do log de auditoria no replay administrativo, rejeição de URLs não HTTPS, validação dos pré-requisitos obrigatórios da [RFC](./RFC.md) (isolamento multi-tenant por `customer_id`, bloqueio anti-SSRF contra redes internas, proteção de chaves secretas em repouso e mascaramento de `secret` e `X-Signature` nos logs) e revisão dedicada de segurança de 2 dias úteis antes do deploy `[ADR-004]`, `[ADR-006]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[T-27]`, `[T-30]`, `[T-38.1]`, `[T-50]`, `[T-59]`, `[código: tests/auth.test.ts]`.
- **Carga/resiliência:** Simulação de endpoints de clientes lentos (que demoram mais de 10 segundos para responder) e indisponíveis (retornando status fora de `2xx` ou falhas de conexão) para comprovar a aplicação do *timeout* de 10 segundos, o escalonamento das 5 retentativas após a tentativa inicial até a DLQ, a preservação da ordem de entrega por `order_id` durante o ciclo ativo de retentativas em processador único (e o desbloqueio de eventos posteriores após ida para a DLQ) e a continuidade do processador de envios quando a API principal é reiniciada `[ADR-002]`, `[ADR-003]`, `[FDD: Seção 6 / FLOW-02, FLOW-03 e FLOW-04]`, `[FDD: Seção 8]`, `[T-02]`, `[T-08]`, `[T-10]`, `[T-11]`, `[T-12]`, `[T-13]`, `[T-14]`, `[T-35]`.

### Validação

- Revisão técnica conjunta do documento de design da feature entre Larissa, Diego e Bruno antes do início da implementação `[T-65]`.
- Fechamento das decisões pendentes de segurança/isolamento multi-tenant e aprovação formal pré-implementação dos controles de segurança especificados no [FDD](./FDD.md), seguidos da auditoria e revisão de código de segurança com duração obrigatória de 2 dias úteis conduzida por Sofia antes da liberação em produção `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-38.1]`, `[T-65]`.
- Publicação e conferência da documentação no portal de desenvolvedor detalhando o comportamento *at-least-once*, os cabeçalhos enviados (`X-Event-Id`, `X-Signature`, `X-Timestamp`, `X-Webhook-Id`), a transição de chaves na rotação de 24 horas e a implementação de desduplicação pelo cliente `[ADR-004]`, `[ADR-005]`, `[T-17]`, `[T-20]`, `[T-37]`, `[T-54]`.
- Validação fim a fim do fluxo de assinatura, recebimento em menos de 10 segundos no cenário nominal e consulta do histórico das últimas 100 entregas para atendimento aos clientes B2B (Atlas, MaxDistribuição e Nova Cargo) dentro do prazo do fim de novembro `[T-01]`, `[T-02]`, `[T-29]`, `[T-52]`, `[T-53]`.

### Perguntas em aberto (opcional)

- **1. [Bloqueador pré-implementação] Modelo definitivo de autorização e isolamento multi-tenant entre usuários (`User`) e clientes (`Customer` / `customer_id`):** Na reunião, definiu-se que o `customer_id` não vem do token JWT (`[T-27]`) e que o CRUD ficaria aberto a qualquer perfil autenticado inicialmente (`[T-50]`), mas o banco de dados atual não possui vínculo entre `User` e `Customer`. Informar `customer_id` ou `:id` na requisição não é suficiente por si só para autorizar o acesso aos recursos de um cliente: depende de decisão humana entre produto, arquitetura e segurança (registrada na [RFC](./RFC.md#questões-em-aberto) e na [Seção 16 do FDD](./FDD.md#16-questões-pendentes-antes-da-implementação)) escolher entre vincular usuários autenticados a um `customer_id` específico ou restringir a gestão a operadores internos autorizados nesta fase `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-27]`, `[T-50]`, `[T-62]`, `[código: prisma/schema.prisma]`, `[código: src/middlewares/auth.middleware.ts]`.
- **2. [Detalhes criptográficos não formalizados / Proposta técnica ainda não aprovada (pendente pré-implementação)] Codificação textual de `X-Signature` e mecanismo de coexistência de chaves durante a rotação de 24 horas:** O comportamento já definido e congelado no [ADR-004](./adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) estabelece o cálculo do HMAC-SHA256 sobre o corpo da requisição HTTP (`payload`) e o envio do cabeçalho `X-Timestamp` com o instante da tentativa de disparo (sem proteção criptográfica do `X-Timestamp` pelo HMAC no contrato vigente; qualquer eventual mudança para assinar `${timestamp}.${payload}` exigiria revisão formal do ADR-004) (`[T-16]`, `[T-37]`). Permanece pendente de aprovação humana pela engenharia de segurança, antes da implementação e da publicação no portal de desenvolvedor (`[T-54]`), ratificar a proposta técnica da [Seção 8 do FDD](./FDD.md#8-contrato-outbound-chamada-enviada-ao-cliente) para a codificação textual da assinatura (`sha256=<hex>`) e o envio de ambas as assinaturas durante as 24 horas de rotação (`[T-17]`) `[ADR-004]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 6 / FLOW-06]`, `[FDD: Seção 8]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-37]`, `[T-54]`.
- **3. [Proposta técnica ainda não aprovada (bloqueador pré-implementação)] Aprovação formal pela engenharia de segurança dos controles de anti-SSRF, proteção de credenciais em repouso e mascaramento de logs:** O comportamento definido na reunião exige URLs HTTPS (`[T-18]`), chave secreta exclusiva por endpoint (`[T-17]`) e reuso do logger com mascaramento (`[T-24]`). As propostas técnicas detalhadas no [FDD](./FDD.md) — bloqueio anti-SSRF no cadastro e na resolução DNS do envio (Seção 8), criptografia das chaves secretas em repouso (Seções 5 e 12) e extensão do mascaramento de logs para ocultar `secret` e `X-Signature` (Seções 11 e 12) — ainda dependem de aprovação formal pré-implementação por Sofia — ver [Questões em aberto na RFC](./RFC.md#questões-em-aberto) e [Seção 16 do FDD](./FDD.md#16-questões-pendentes-antes-da-implementação) `[ADR-004]`, `[RFC: Questões em aberto]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 5]`, `[FDD: Seção 8]`, `[FDD: Seção 11]`, `[FDD: Seção 12]`, `[FDD: Seção 16]`, `[T-16]`, `[T-17]`, `[T-18]`, `[T-24]`, `[código: src/shared/logger/index.ts]`.
- **4. [Requisito obrigatório pré-deploy] Execução da revisão de código de segurança de 2 dias úteis antes da entrada em produção:** Conforme aprovado no [ADR-004](./adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) e nos [Critérios de aprovação da RFC](./RFC.md#critérios-de-aprovação), nenhuma versão da funcionalidade pode ser promovida para produção sem a conclusão da janela obrigatória de 2 dias úteis de auditoria e revisão de código conduzida pela engenharia de segurança (Sofia) sobre geração/rotação de credenciais, cálculo de HMAC, controles anti-SSRF, mascaramento de logs e isolamento multi-tenant `[ADR-004]`, `[RFC: Critérios de aprovação]`, `[FDD: Seção 16]`, `[T-38.1]`, `[T-65]`.
