# ADR-002: Execução do worker de envio em processo Node.js separado com polling na outbox a cada 2 segundos

| Campo | Valor |
| --- | --- |
| Status | Aceito |
| Data | 2026-10-17 (data de elaboração; a reunião não registrou data) |
| Decisores | Diego (propôs polling de 2s, execução em processo separado e ordenação por `order_id` em single-worker), Larissa (fechou o polling de 2s, sugeriu a nova entry point baseada em `src/server.ts`, registrou "Anotado" para o processo separado e fechou a limitação de ordenação), Bruno (condicionou em `[09:11]` conectar no mesmo banco e usar a mesma biblioteca/configuração do Prisma client, esclarecendo em `[09:30]` que o worker cria sua própria instância de `PrismaClient` por ser outro processo conectado à mesma `DATABASE_URL`) e Marcos (validou que 2s atende à latência esperada e que clientes não pediram ordenação global) `[T-08]`, `[T-10]`, `[T-11]`, `[T-25]`, `[T-58]` |
| Origem | `[T-02]` · `[09:02]` Marcos; `[T-06]` · `[09:07]` Larissa/Diego; `[T-07]` · `[09:07]` Bruno / `[09:08]` Diego; `[T-08]` · `[09:09]` Diego / `[09:10]` Marcos, Larissa; `[T-10]`, `[T-58]` · `[09:11]` Diego, Larissa, Bruno / `[09:12]` Larissa; `[T-11]` · `[09:12]`–`[09:14]` Diego, Larissa, Marcos; `[T-25]` · `[09:30]` Bruno |

## Status

Aceito

## Contexto

Com a adoção da tabela de outbox no MySQL para registrar de forma transacional os eventos de mudança de status de pedidos, o sistema precisa de um mecanismo assíncrono que leia os registros pendentes e realize os disparos HTTP para os endpoints dos clientes dentro da latência aceitável de até 10 segundos para notificações em "tempo real" `[T-02]`, `[T-07]`, `[T-08]`. No código atual, o ponto de entrada da API HTTP está em `src/server.ts` (`src/server.ts:6-27`) — que inicializa o servidor Express via `bootstrap()`, reutiliza o cliente `prisma` exportado por `src/config/database.ts` (`src/config/database.ts:4-10`) e trata os sinais `SIGINT` e `SIGTERM` desconectando do banco (`src/server.ts:13-21`) — e não há entry point de worker (mapa, Parte C) `[T-58]`. Era necessário definir como acionar a leitura da outbox no MySQL, se o processador executaria no mesmo processo da API ou de forma separada, e qual garantia de ordenação de entrega seria oferecida `[T-08]`, `[T-10]`, `[T-11]`.

## Decisão

Decidimos executar o processador da outbox em um processo Node.js separado da API HTTP — porque, conforme Diego apontou em `[09:11]`, se o worker rodasse dentro da mesma instância da API e a API reiniciasse, perderia o worker `[T-10]` —, operando por polling constante a cada 2 segundos sobre os registros pendentes da tabela de outbox, conectado ao mesmo banco com instância própria do `PrismaClient` na mesma `DATABASE_URL` e com garantia de ordenação de entrega restrita ao escopo de um mesmo pedido (`order_id`) enquanto houver um único worker ativo `[T-08]`, `[T-10]`, `[T-11]`, `[T-25]`.

**Regras e restrições fechadas:**

- **Processo separado e nova entry point dedicada:** Em `[09:11]`, Diego definiu que o worker deve rodar como processo separado, e não dentro da mesma instância da API, porque se a API reinicia perde-se o worker `[T-10]`. Larissa sugeriu em `[09:11]` criar uma entry point nova no projeto e um script próprio de inicialização (ainda inexistentes no código atual; nenhuma ocorrência de `'worker'` em `package.json` (mapa, Parte C)), seguindo a estrutura de inicialização (`bootstrap`) e encerramento gracioso (`shutdown` em `SIGINT` e `SIGTERM`) de `src/server.ts` (`src/server.ts:6-27`) `[T-10]`, `[T-58]`. Bruno condicionou em `[09:11]` conectar no mesmo banco e usar o "mesmo Prisma client" — expressão confirmada por Diego em `[09:11]` como mesmo banco e mesma stack em processos distintos `[T-10]` e esclarecida pelo próprio Bruno em `[09:30]` no sentido de utilizar a mesma biblioteca e configuração de conexão (`DATABASE_URL`), mas instanciando um `PrismaClient` próprio no processo do worker `[T-25]` —, e Larissa registrou "Anotado" em `[09:12]` `[T-10]`, `[T-11]`.
- **Polling constante a cada 2 segundos em lote pequeno:** O worker consultará a tabela de outbox em intervalos de 2 segundos para buscar os eventos pendentes mais antigos dentro da expectativa de latência de até 10 segundos dos clientes, lendo apenas os registros com status `pendente` em lote pequeno, apoiado por indexação no campo de `status` e em `created_at` conforme dito por Diego em `[09:08]` (análise técnica: a reunião mencionou "índice no campo de status ... e em created_at" sem decidir entre dois índices separados ou um índice composto, definição que cabe ao [FDD](../FDD.md); além disso, o intervalo de 2 segundos reduz o atraso de detecção na outbox, enquanto a entrega fim a fim depende também do processamento do lote e do tempo de resposta dos endpoints destinatários) `[T-02]`, `[T-07]`, `[T-08]`.
- **Instância dedicada do `PrismaClient`:** Embora Bruno tenha dito "usar o mesmo Prisma client" em `[09:11]`, ele explicitou em `[09:30]` que `PrismaClient` é por processo: o worker utiliza a mesma biblioteca e configuração de conexão com o banco (`DATABASE_URL`, validada em `src/config/env.ts:7`), mas cria sua própria instância de `PrismaClient` por ser executado em outro processo Node.js (a fábrica `createPrismaClient()` já existe em `src/config/database.ts:4-10`) `[T-10]`, `[T-25]`.
- **Ordenação garantida apenas por `order_id` em single-worker:** Não há garantia de ordenação global entre eventos de pedidos distintos; restringe-se a garantia de ordenação às transições de um mesmo pedido (`order_id`) enquanto houver um único worker ativo, restrição fechada por Larissa como limitação conhecida em `[09:13]` e validada por Marcos em `[09:14]` por não haver demanda dos clientes por ordenação global (análise técnica: um único processo, por si só, não assegura a ordenação e apenas evita concorrência entre múltiplos workers; o [FDD](../FDD.md) deverá definir o mecanismo de consulta, sequenciamento e envio necessário para cumprir essa garantia por pedido) `[T-11]`.

## Alternativas consideradas

### Alternativa 1: Uso de trigger no MySQL para acionamento reativo

- **Prós:** Análise técnica: o objetivo que motivou cogitar a alternativa foi buscar maior reatividade após a escrita no banco para não depender do intervalo entre ciclos de polling (sem que uma trigger isolada no MySQL tenha, contudo, capacidade de acionar diretamente um processo Node.js externo).
- **Contras:** O MySQL não possui listener nativo (como o `NOTIFY/LISTEN` do Postgres); uma trigger no banco só executa SQL e não notifica processo externo, e improvisar soluções como escrever em arquivo ou bater em um endpoint para avisar o worker "fica esquisito" `[T-09]`.
- **Motivo do descarte:** Perguntada por Bruno em `[09:09]` para tornar a leitura mais reativa e descartada por Diego em `[09:09]` porque o MySQL não tem listener nativo, uma trigger só executa SQL e não notifica processo externo, improvisar (arquivo, endpoint) "fica esquisito" e o polling de 2 segundos já atende com folga ao requisito de latência abaixo de 10 segundos `[T-02]`, `[T-08]`, `[T-09]`.

### Alternativa 2: Processar a outbox dentro do mesmo processo da API HTTP

- **Prós:** Análise técnica: dispensaria a criação de uma nova entry point e o gerenciamento de um segundo processo Node.js em execução.
- **Contras:** Análise técnica: o processamento da outbox e a espera por respostas HTTP dos clientes competiriam por recursos do processo da API, impactando a disponibilidade e a latência das rotas da aplicação.
- **Motivo do descarte:** Descartada por Diego em `[09:11]` porque, se o worker rodasse dentro da mesma instância da API e a API reiniciasse, perderia o worker; Larissa sugeriu criar uma nova entry point em `[09:11]` (e deu "Anotado" em `[09:12]`) e Bruno condicionou conectar no mesmo banco e usar a mesma biblioteca/configuração do Prisma client (com instância própria de `PrismaClient` por processo, conforme esclarecido em `[09:30]`) `[T-10]`, `[T-11]`, `[T-25]`.

### Alternativa 3: Fila ou streaming externo com consumidor dedicado (Redis Streams)

- **Prós:** Análise técnica: ofereceria entrega orientada a consumidor sobre estrutura dedicada de streaming, sem necessidade de polling periódico em tabela SQL.
- **Contras:** Exigiria subir mais infraestrutura além do MySQL já existente no projeto (ver [ADR-001](./ADR-001-outbox-transacional-no-mysql.md)) `[T-06]`.
- **Motivo do descarte:** Em `[09:07]`, Larissa citou Redis Streams e observou que exigiria subir mais infraestrutura; Diego descartou em `[09:07]` por serem um time pequeno e considerar *overengineering* quando a outbox no MySQL existente já resolve (conforme detalhado no [ADR-001](./ADR-001-outbox-transacional-no-mysql.md)) `[T-06]`.

## Consequências

**Positivas**

- Evita que um reinício da instância da API interrompa ou faça perder o worker de envio de webhooks, mantendo o processamento da outbox em um processo Node.js separado da API iniciada por `src/server.ts` (`src/server.ts:6-27`) `[T-10]`, `[T-58]`.
- O intervalo de polling de 2 segundos contribui para reduzir o tempo de detecção de novos eventos pendentes na outbox — ajudando a compor a meta de latência de até 10 segundos esperada pelos clientes, cuja entrega efetiva depende também do processamento do lote e do tempo de resposta dos endpoints destinatários (análise técnica) — sem exigir infraestrutura adicional além do MySQL `[T-02]`, `[T-06]`, `[T-08]`.
- Reaproveita o padrão de ciclo de vida e encerramento gracioso (`SIGINT`/`SIGTERM` com `prisma.$disconnect()`) de `src/server.ts` (`src/server.ts:13-21`) e a fábrica `createPrismaClient()` de `src/config/database.ts` (`src/config/database.ts:4-10`) `[T-25]`, `[T-58]`.

**Negativas**

- O polling realiza consultas periódicas ao MySQL a cada 2 segundos `[T-08]` (análise técnica: inclusive em períodos sem eventos pendentes) e, diante da preocupação levantada por Bruno em `[09:07]` sobre lentidão caso acumulem muitos eventos na tabela, exige indexação no campo de `status` e em `created_at` (sem decisão na reunião entre índices separados ou índice composto) e leitura apenas dos registros pendentes em lote pequeno, conforme respondido por Diego em `[09:07]`–`[09:08]` `[T-07]`, `[T-08]`.
- Restringe a garantia de ordenação ao escopo de cada `order_id` sob execução de um único worker (*single-worker*) — visto que um único processo, por si só, não assegura a ordenação sem o mecanismo de consulta, sequenciamento e envio que o [FDD](../FDD.md) deverá definir (análise técnica) — e deixa a coordenação entre múltiplos workers para evolução futura `[T-11]`, `[T-46]`.
- **Análise técnica (acoplamento de configuração e de metadados de log no código atual):** Ao reutilizar `src/config/database.ts` (`src/config/database.ts:2`) e `src/shared/logger/index.ts` (`src/shared/logger/index.ts:2`), o processo do worker carregará `src/config/env.ts` (`src/config/env.ts:7-8`, `src/config/env.ts:22`, `src/config/env.ts:27`), que exige `JWT_SECRET` com no mínimo 16 caracteres sob pena de encerrar o processo com `process.exit(1)`, além de herdar no logger o metadado fixo `service: 'order-management-api'` (`src/shared/logger/index.ts:20`).

**Trade-off aceito:** aceita-se operar um segundo processo Node.js com consultas de polling no MySQL a cada 2 segundos e garantia de ordenação restrita ao mesmo `order_id` com um único worker ativo, em troca de não perder o worker caso a API reinicie e de reduzir o tempo de detecção de eventos (contribuindo para a meta de até 10 segundos, sujeita ao tempo de processamento e de resposta dos endpoints) sem introduzir infraestrutura externa de mensageria `[T-02]`, `[T-06]`, `[T-08]`, `[T-10]`, `[T-11]`.

## Questões em aberto

- **Nome do arquivo do processador no módulo de webhooks (`[T-22]`, ambíguo):** Em `[09:28]`, Bruno mencionou a criação do processador dentro do módulo de webhooks citando dois nomes possíveis para o arquivo (terminado em `.worker.ts` ou `.processor.ts`), sem que a reunião fixasse qual dos dois será adotado `[T-22]`.
- **Escalonamento para múltiplos workers (`[T-46]`, adiado):** Diego apontou que escalar para múltiplos workers concorrentes exigiria particionamento por `order_id` ou lock pessimista para não quebrar a ordenação por pedido, mas o tema foi classificado como "problema do futuro" e adiado na reunião `[T-11]`, `[T-46]`.
- **Tamanho exato do lote (*batch*) lido a cada ciclo de polling (Lacuna 7, sem origem na reunião):** A reunião definiu que o worker lê apenas os registros pendentes em "batch pequeno", mas a quantidade exata de itens buscados por consulta não está na transcrição `[T-07]`.
- **Recuperação de eventos presos no status `processando` em caso de queda do worker (Lacuna 8, sem origem na reunião):** Embora o status `processando` tenha sido previsto para os registros da outbox `[T-07]`, a estratégia para destravar ou reprocessar eventos caso o processo do worker caia durante um envio não está na transcrição `[T-07]`.
- **Resolução do acoplamento do worker a `JWT_SECRET` em `env.ts` e ao nome fixo do serviço no logger (Achados 5 e 6 do mapa de código, sem origem na reunião):** Como `loadEnv()` em `src/config/env.ts` (`src/config/env.ts:7-8`, `src/config/env.ts:22`, `src/config/env.ts:27`) exige `JWT_SECRET` na carga do módulo e `createLogger()` em `src/shared/logger/index.ts` (`src/shared/logger/index.ts:20`) fixa `base: { service: 'order-management-api' }`, a forma como o worker lidará com essas dependências permanece como definição de implementação para o FDD.

## Referências

- Transcrição: `[09:02]` Marcos (`[T-02]`); `[09:07]` Larissa, Diego e Bruno (`[T-06]`, `[T-07]`); `[09:08]` Diego (`[T-07]`); `[09:09]`–`[09:10]` Bruno, Diego, Marcos e Larissa (`[T-08]`, `[T-09]`); `[09:11]`–`[09:12]` Diego, Larissa e Bruno (`[T-10]`, `[T-58]`); `[09:12]`–`[09:14]` Diego, Bruno, Larissa e Marcos (`[T-11]`, `[T-46]`); `[09:28]` Bruno (`[T-22]`); `[09:30]` Bruno (`[T-25]`)
- Código: `src/server.ts:6-27`, `src/server.ts:13-21`, `src/config/database.ts:2`, `src/config/database.ts:4-10`, `src/config/env.ts:7`, `src/config/env.ts:7-8`, `src/config/env.ts:22`, `src/config/env.ts:27`, `src/shared/logger/index.ts:2`, `src/shared/logger/index.ts:20`
- Documentos relacionados: [Plano de ADRs](../../_work/PLANO-ADRS.md) · [README de ADRs](./README.md) · [ADR-001](./ADR-001-outbox-transacional-no-mysql.md) · [RFC](../RFC.md) · [FDD](../FDD.md)
