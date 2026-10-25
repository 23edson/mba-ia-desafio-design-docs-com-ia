# ADR-005: Garantia de entrega at-least-once com identificador de evento X-Event-Id para desduplicação no receptor

| Campo | Valor |
| --- | --- |
| Status | Aceito |
| Data | 2026-10-17 (data de elaboração; a reunião não registrou data) |
| Decisores | Larissa (fechou a decisão de entrega *at-least-once* com cabeçalho `X-Event-Id` para desduplicação pelo cliente e confirmou a restrição de ordenação restrita a `order_id` em single-worker), Diego (propôs a garantia *at-least-once*, a geração de UUID na outbox para o cabeçalho `X-Event-Id`, descartou *exactly-once* citando o padrão de mercado de Stripe e GitHub, e definiu os headers HTTP), Bruno (questionou como o consumidor identificaria duplicatas e validou a ausência de ordering global), Sofia (apontou a transferência de responsabilidade de idempotência para o cliente e sugeriu a inclusão de `X-Webhook-Id`) e Marcos (reforçou que os clientes não solicitaram ordering global e assumiu documentar o at-least-once e a deduplicação com destaque no portal de desenvolvedor) `[T-11]`, `[T-20]`, `[T-37]`, `[T-44]`, `[T-54]` |
| Origem | `[T-11]` · `[09:12]`, `[09:13]` Diego/Larissa, `[09:14]` Marcos; `[T-20]` · `[09:24]`, `[09:25]` Diego, `[09:26]` Larissa; `[T-37]` · `[09:44]`, `[09:45]` Diego/Sofia; `[T-44]` · `[09:25]` Diego; `[T-54]` · `[09:26]` Marcos; `[T-64]` · `[09:18]` Diego |

## Status

Aceito

## Contexto

Em sistemas de disparo de webhooks através de redes públicas sujeitas a instabilidades transitórias e reinicializações de processos, garantir que todo evento de mudança de pedido seja submetido a um ciclo confiável de entrega e tolerância a falhas exige uma política clara de entrega e resiliência `[T-20]`. O envio com retentativas progressivas (conforme estabelecido no ADR-003) assegura a retransmissão de eventos quando ocorrem erros ou timeouts na comunicação, mas introduz cenários onde uma resposta de sucesso do destinatário se perde ou onde um disparo é repetido, fazendo com que o mesmo evento seja recebido mais de uma vez pelo endpoint externo `[T-20]`. No código atual, as entidades do modelo de dados adotam identificadores únicos no formato UUID (`@id @default(uuid()) @db.Char(36)` como em `prisma/schema.prisma:26`), com nenhuma ocorrência de 'webhook' em `prisma/schema.prisma` (mapa, Parte C) `[T-20]`. Diante disso, a equipe precisou estabelecer o nível de garantia de entrega suportado pelo sistema e o mecanismo para que os clientes receptores consigam distinguir entregas legítimas de duplicações indesejadas sem gerar sobrecarga ou acoplamento inviável na infraestrutura da plataforma `[T-20]`, `[T-44]`.

## Decisão

Decidimos adotar formalmente a garantia de entrega *at-least-once* (pelo menos uma vez) para todas as notificações de webhook e transmitir em cada requisição HTTP de disparo o cabeçalho customizado `X-Event-Id` contendo um identificador único em formato UUID gerado no momento da inserção do evento na tabela de outbox, transferindo ao receptor a responsabilidade de realizar a desduplicação das mensagens processadas com base nesse identificador `[T-20]`, `[T-37]`.

**Regras e especificações fechadas:**

- **Garantia de entrega at-least-once e ciclo de retentativas:** Todos os eventos persistidos na outbox são submetidos ao mecanismo de entrega e ao ciclo de retentativas progressivas estabelecido pela plataforma (ADR-003), sendo possíveis duplicações de recebimento pelo destinatário em virtude de instabilidades transitórias de rede, repetições de envio ou timeouts `[T-20]`. Os eventos que esgotarem o teto de retentativas são encaminhados para a tabela dedicada de DLQ (`webhook_dead_letter`), de modo que a entrega efetiva desses eventos não é incondicional e passa a depender do tratamento de recuperação ou do acionamento manual do endpoint de replay por um administrador `[T-20]`.
- **Identificador único de evento via cabeçalho `X-Event-Id`:** Cada evento gerado recebe um UUID no momento em que é gravado na tabela outbox do MySQL, e esse identificador gerado na inserção é enviado obrigatoriamente no cabeçalho HTTP `X-Event-Id` de todas as tentativas de entrega daquele evento, permitindo ao cliente identificar requisições duplicadas `[T-20]`, `[T-37]`.
- **Desduplicação a cargo do receptor:** O cliente receptor deve estar preparado para receber o mesmo evento mais de uma vez e é responsável por implementar sua própria lógica de idempotência, registrando os `X-Event-Id` processados para descartar entregas subsequentes do mesmo evento `[T-20]`.
- **Cabeçalhos HTTP associados ao evento e identificador `X-Event-Id`:** O identificador único de negócio do evento é transmitido no cabeçalho HTTP `X-Event-Id`, gerado como UUID na outbox (`[T-20]`), permitindo ao cliente deduplicar notificações repetidas (`[T-20]`); os demais cabeçalhos de autenticação e metadados (`X-Signature`, `X-Timestamp` e `X-Webhook-Id`) são definidos pelo [ADR-004](./ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) e complementados com `Content-Type: application/json`, preservando a distinção funcional entre o ID do evento (`X-Event-Id`) e o identificador do cadastro do endpoint (`X-Webhook-Id`) `[T-20]`, `[T-37]`.
- **Garantia de ordenação restrita a `order_id` em single-worker:** Conforme registrado na reunião técnica como limitação conhecida e detalhado no [ADR-002](./ADR-002-worker-separado-com-polling.md), a ordenação de entrega é garantida exclusivamente por pedido individual (`order_id`) enquanto o worker operar em processo único (single-worker), inexistindo garantia de ordenação global entre diferentes pedidos na plataforma `[T-11]`. A decisão estabelece essa restrição sem definir o mecanismo interno de fila ou controle de concorrência por pedido, cuja especificação detalhada cabe ao [FDD](../FDD.md) `[T-11]`.

## Alternativas consideradas

### Alternativa 1: Garantia de entrega exactly-once com coordenação distribuída bidirecional (`[T-44]`)

- **Prós:** Análise técnica: Em uma garantia teórica *exactly-once*, o receptor teria a expectativa de receber cada notificação apenas uma vez na camada de entrega, simplificando significativamente o processamento no destino e reduzindo a dependência de lógica de desduplicação pelo receptor `[T-44]`.
- **Contras:** Análise técnica: Exigiria coordenação distribuída síncrona entre a plataforma e sistemas externos fora do seu controle operacional, introduzindo alto acoplamento, fragilidade perante latências de rede e indisponibilidades de terceiros `[T-44]`.
- **Motivo do descarte:** Descartada expressamente por Diego em `[09:25]` ao apontar que "garantir exactly-once exigiria coordenação dos dois lados e fica muito mais complexo", optando-se pelo padrão consagrado de mercado adotado por grandes referências como Stripe e GitHub ("at-least-once com event_id resolve 99% dos casos") `[T-44]`.

### Alternativa 2: Garantia de entrega at-most-once sem retentativas em caso de falha (plausível, não discutida)

- **Prós:** Análise técnica: Implementação substancialmente mais simples na plataforma e no cliente, pois cada evento seria disparado uma única vez sem ciclo de retentativas ou backoff, dispensando mecanismos de controle de duplicatas no receptor `[T-20]`.
- **Contras:** Análise técnica: Quedas momentâneas de rede ou indisponibilidades transitórias do endpoint receptor resultariam na perda definitiva da notificação, tornando a integração de pedidos inaceitavelmente instável para as operações de negócio dos clientes `[T-20]`.
- **Motivo do descarte:** Análise técnica: Essa abordagem não foi proposta nem discutida na reunião, constando aqui como contraponto conceitual de arquitetura de mensageria; a equipe priorizou a confiabilidade de entrega, fechando at-least-once apoiado pela outbox e política de retentativas (`[T-20]`).

## Consequências

**Positivas**

- A garantia *at-least-once* simplifica a arquitetura da plataforma e do worker, dispensando protocolos complexos de coordenação distribuída com sistemas de terceiros `[T-20]`, `[T-44]`.
- O fornecimento de um identificador estável `X-Event-Id` no formato UUID em cada envio viabiliza que qualquer cliente implemente desduplicação robusta e determinística com baixo custo de desenvolvimento `[T-20]`, `[T-37]`.
- Segue o padrão de interoperabilidade amplamente consolidado na indústria de pagamentos e webhooks (como Stripe e GitHub), facilitando a integração por equipes externas já familiarizadas com esse modelo `[T-20]`.
- O envio de `X-Event-Id` (para identificação unívoca do evento e suporte à desduplicação) em conjunto com `X-Timestamp` (como referência temporal do instante do envio) e `X-Webhook-Id` (para identificação do endpoint) fornece metadados claros de auditoria e correlação, preservando a distinção entre evento e cadastro sem presumir que tais cabeçalhos confiram proteção automática contra ataques de repetição `[T-37]`.
- A transparência sobre a ordenação restrita ao `order_id` alinha as expectativas técnicas com os clientes, que não demandaram ordenação global de mensagens `[T-11]`.

**Negativas**

- Transfere para os clientes integradores a obrigação de projetar endpoints com tratamento de idempotência, gerando atrito para desenvolvedores inexperientes que esperavam entregas estritamente únicas `[T-20]`, `[T-54]`.
- Requer esforço documental dedicado para detalhar o modelo *at-least-once* e instruir os consumidores sobre estratégias de deduplicação via portal de desenvolvedor antes do lançamento `[T-54]`.
- Entregas duplicadas consomem chamadas HTTP e recursos computacionais adicionais tanto no worker quanto na infraestrutura dos receptores `[T-20]`.
- Limitação de ordenação: a ausência de ordering global e a dependência de um processo worker único restringem a concorrência na entrega de múltiplos pedidos em alta volumetria `[T-11]`.

**Trade-off aceito:** aceita-se a possibilidade de entregas duplicadas e a transferência da responsabilidade de desduplicação para o cliente consumidor em troca de dispensar transações distribuídas bidirecionais complexas e assegurar a confiabilidade do processo de despacho de eventos mesmo sob instabilidades de rede `[T-20]`, `[T-44]`, `[T-54]`.

## Questões em aberto

- **Manutenção ou renovação do `event_id` no replay manual da DLQ (`[T-64]`):** A transcrição definiu a existência do endpoint de replay da DLQ (`POST /admin/webhooks/dead-letter/:id/replay`), mas não estabeleceu se o evento reinserido na outbox mantém o `event_id` original gerado na criação ou se recebe um novo UUID `[T-64]`. Se mantiver o identificador original, clientes com controle estrito de idempotência que processaram o evento anteriormente (mesmo com timeout na resposta) ignorarão a retentativa; se gerar um novo `event_id`, o cliente pode processar uma ação repetida sem perceber que se tratava de um reprocessamento `[T-64]`. A definição da estratégia fica como pendência para o FDD.
- **Relação estrutural entre `event_id` e a chave primária da outbox (sem origem na reunião):** Diego definiu que o `X-Event-Id` receberá um UUID gerado quando o evento entra na outbox (`[T-20]`). O [ADR-001](./ADR-001-outbox-transacional-no-mysql.md) já fecha a adoção de chave primária UUID (`id`) na tabela de outbox alinhada ao padrão das entidades do Prisma (`[T-39]`), mas a reunião não especificou se o `X-Event-Id` utilizará diretamente essa chave primária `id` da tabela de outbox ou uma coluna separada `event_id` dedicada à idempotência externa `[T-20]`, `[T-39]`. O FDD e o schema do Prisma deverão definir essa modelagem `[T-20]`.
- **Estratégia e janela de armazenamento de chaves de deduplicação no cliente (sem origem na reunião):** A plataforma exige que o cliente faça a desduplicação pelo `event_id` (`[T-20]`), porém não define recomendações sobre o tempo de retenção do cache de IDs ou mecanismos de bloqueio no consumidor, cabendo ao portal de desenvolvedor fornecer orientações e boas práticas `[T-20]`, `[T-54]`.
- **Preservação da ordenação por `order_id` durante retentativas (risco técnico / pendência para o FDD):** A reunião estabeleceu a ordenação por `order_id` restrita a worker único (`[T-11]`, ver [ADR-002](./ADR-002-worker-separado-com-polling.md)), mas as fontes não definiram como a ordem sequencial de um mesmo pedido deve ser preservada se um evento anterior falhar e entrar no ciclo de retentativas com backoff (ADR-003) enquanto novos eventos do mesmo `order_id` forem gerados `[T-11]`. Como análise técnica, sem um mecanismo explícito no FDD (como enfileiramento estrito ou bloqueio de eventos subsequentes do mesmo pedido até a resolução do anterior), eventos posteriores poderiam ultrapassar eventos em retry `[T-11]`.
- **Evolução da garantia de ordenação para múltiplos workers concorrentes (`[T-11]`):** Ficou estabelecido que o ordering é garantido apenas por `order_id` sob um único worker ativo `[T-11]`. Estratégias para preservar ordenação sob concorrência (como particionamento por pedido ou locks pessimistas) foram expressamente adiadas por Diego como "problema do futuro" `[T-11]`.
- **Vínculo criptográfico de `X-Timestamp` e mitigação de replay attack (questão registrada no ADR-004):** O envio de `X-Timestamp` fornece ao cliente a referência temporal do envio `[T-37]`. Conforme registrado no ADR-004, a efetiva proteção contra ataques de repetição requer a vinculação do timestamp à assinatura HMAC e a validação ativa com tolerância temporal pelo receptor, permanecendo como responsabilidade e especificação de segurança detalhada no ADR-004 e no FDD `[T-37]`.

## Referências

- Transcrição: `[09:12]`, `[09:13]` Diego e Larissa (`[T-11]`); `[09:14]` Marcos (`[T-11]`); `[09:18]` Diego (`[T-64]`); `[09:24]` Diego e Larissa (`[T-20]`); `[09:25]` Diego e Bruno (`[T-20]`, `[T-44]`); `[09:25]` Sofia e Diego (`[T-20]`, `[T-44]`); `[09:26]` Marcos e Larissa (`[T-20]`, `[T-54]`); `[09:44]` Diego, Bruno e Sofia (`[T-37]`); `[09:45]` Diego (`[T-37]`)
- Código: `prisma/schema.prisma:26`
- Documentos relacionados: [Plano de ADRs](../../_work/PLANO-ADRS.md) · [README de ADRs](./README.md) · [ADR-001](./ADR-001-outbox-transacional-no-mysql.md) · [ADR-002](./ADR-002-worker-separado-com-polling.md) · [ADR-003](./ADR-003-retry-com-backoff-e-dlq.md) · [ADR-004](./ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) · [RFC](../RFC.md) · [FDD](../FDD.md)
