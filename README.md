# Da Reunião ao Documento: Design Docs com IA — Sistema de Webhooks de Notificação de Pedidos

## Sobre o Desafio


Esse repositório contém os artefatos gerados (design docs) para uma nova feature no sistema exemplo. A primeira ação foi extrair os principais pontos da transcrição da reunião. A partir dai, foi gerado um
plano base para geração das ADRs e das demais etapas do desafio. Para facilitar o fluxo, utilizei templates
e skills para cada etapa de geração.

Todo o fluxo de geração da documentação foi mantida rastreada (logs de prompt no arquivo LOG.md). Ao final,
foi realizado diversas auditorias para validação de consistência em relação aos requisitos do desafio, inclusive comparando o resultado contra outros modelos de IA (mais focado com Claude Sonnet 5.5).

A construção de prompts personalizados e skills também foi realizado com o auxílio do Claude Sonnet, apesar de ser utilizado os modelos do Google Antigravity como agente principal nesse trabalho.

---

## Ferramentas de IA Utilizadas

| Ferramenta | Papel no Processo |
| :--- | :--- |
| **Google Antigravity CLI / Gemini 3.8 Flash & Pro** | Orquestração principal do fluxo de trabalho, execução de chamadas MCP, inspeção automatizada da base de código e redação assistida dos artefatos técnicos em Markdown. |
| **Subagentes de Pesquisa e Auditoria (`research` / `self`)** | Extração estruturada de transcrição por marcadores temporais, mapeamento estático de dependências de código (`grep`/`sed`/`ls`) e verificação cruzada de consistência entre documentos. |
| **Custom Skills Especializadas (`.agents/skills/`)** | Automação e governança de geração por tipo documental: [`adr-generator`](.agents/skills/adr-generator/SKILL.md), [`rfc-generator`](.agents/skills/rfc-generator/SKILL.md), [`fdd-generator`](.agents/skills/fdd-generator/SKILL.md) e [`prd-generator`](.agents/skills/prd-generator/SKILL.md), impondo templates congelados e validação de rastreabilidade. |

---

## Workflow Adotado

Para mitigar alucinações e evitar a propagação de inconsistências em cascata, o fluxo de engenharia documental foi estruturado e executado em **8 etapas sequenciais orientadas pela "altura" e hierarquia dos documentos**. A premissa fundamental foi nunca solicitar à IA a geração de documentos a partir do nada: cada etapa consumiu artefatos auditados da etapa anterior, garantindo rastreabilidade fim a fim.

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 1: Fontes da Verdade (Catálogo da Transcrição + Mapa do Código Base)  │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 2: Architecture Decision Records (7 ADRs Congelados no formato MADR)  │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 3: Request for Comments (docs/RFC.md — Proposta Arquitetural e Riscos)│
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 4: Feature Design Document (docs/FDD.md — Especificação e Contratos)  │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 5: Product Requirements Document (docs/PRD.md — Requisitos e Negócio) │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPAS 6 a 8: Tracker de Rastreabilidade, README da Jornada e Auditoria     │
 └─────────────────────────────────────────────────────────────────────────────┘
```

Abaixo detalha-se como cada etapa foi operacionalizada:

1. **Etapa 1 — Preparação das Fontes da Verdade e Ancoragem Anti-Alucinação (`_work/`)**:
   - *Como o fluxo foi adotado:* Antes de redigir qualquer proposta técnica, foram construídas as âncoras da verdade do projeto para bloquear alucinações da IA. Utilizou-se o Gemini com comandos determinísticos de terminal para ler o código legado e a transcrição literal.
   - *Artefatos estruturados:*
     - `_work/CATALOGO.md`: Mapeamento de 65 declarações atômicas (`T-01` a `T-65`) com timestamp e autor (`[hh:mm] Nome`), separando rigidamente decisões tomadas, requisitos funcionais, restrições e ideias expressamente descartadas ou adiadas (índice *NÃO ENTRA*), além de listar 11 lacunas explícitas (pontos não abordados na reunião, impedindo que a IA inventasse premissas).
     - `_work/MAPA-CODIGO.md`: Levantamento factual das estruturas existentes no OMS por meio de evidências cruas de código (`ls`, `grep -n`, `sed -n`), comprovando a mecânica de `OrderService.changeStatus`, modelos em `prisma/schema.prisma`, middlewares de autenticação/validação, logger Pino e testes unitários.
     - `_work/INDICE.md`: Matriz temática cruzando declarações com os futuros documentos.
   - *Governança:* Esses arquivos foram conferidos, geraram checksums SHA-256 e foram congelados em modo somente leitura (`chmod a-w` / `0444`), tornando-se as únicas fontes de consulta permitidas para os prompts subsequentes.

2. **Etapa 2 — Elaboração dos Architecture Decision Records (`docs/adrs/`)**:
   - *Como o fluxo foi adotado:* Em vez de iniciar por documentos extensos, foi isolado e resolvido as decisões de engenharia pontualmente. Cada decisão discutida na reunião foi tratada como uma unidade arquitetural autônoma.
   - *Uso de Skill Especializada:* Utilizou-se a custom skill [`adr-generator`](.agents/skills/adr-generator/SKILL.md), instruída a aplicar rigorosamente o template MADR (`_work/templates/adr_template.md`), cruzando os pontos exclusivamente contra o catálogo congelado e os caminhos reais de código.
   - *Execução:* Foram gerados 7 ADRs individuais (`ADR-001` a `ADR-007`) cobrindo as 6 decisões nucleares (Outbox no MySQL, Worker com polling de 2s, Retries com backoff progressivo e DLQ, Autenticação HMAC-SHA256 por secret única, Garantia at-least-once com `X-Event-Id`, Reuso de padrões do projeto existente) e a decisão de limite de payload em 64 KB com snapshot imutável. Cada ADR foi auditado individualmente.

3. **Etapa 3 — Consolidação do Request for Comments (`docs/RFC.md`)**:
   - *Como o fluxo foi adotado:* Com as decisões isoladas já formalizadas, a proposta técnica de alto nível foi redigida sob a ótica de um documento submetido para revisão (composto pelos participantes reais da reunião como revisores), focando no "o que propomos e por quê", sem descer prematuramente ao nível de código do FDD.
   - *Uso de Skill Especializada:* Operou-se por meio da skill [`rfc-generator`](.agents/skills/rfc-generator/SKILL.md), alimentada pelo template oficial `_work/templates/rfc_template.md` e referenciando diretamente os 7 ADRs aprovados.
   - *Conteúdo consolidado:* A RFC sintetizou a proposta em 2 a 4 páginas, formalizou as alternativas reais descartadas (envio síncrono, Redis Streams, triggers nativas do MySQL, retries infinitos, exactly-once e demais), registrou as 3 deliberações de consenso (A1 para rollback transacional em caso de payload > 64 KB, B1 para emissão apenas em transições de status e C2 para persistência na outbox) e catalogou os riscos de infraestrutura e as questões em aberto.

4. **Etapa 4 — Detalhamento do Feature Design Document (`docs/FDD.md`)**:
   - *Como o fluxo foi adotado:* Com a arquitetura acordada, a solução avançou para a camada de detalhamento de engenharia ("como construir em detalhe"), fornecendo especificações acionáveis para os desenvolvedores iniciarem o código sem ambiguidades.
   - *Uso de Skill Especializada:* Empregou-se a skill [`fdd-generator`](.agents/skills/fdd-generator/SKILL.md), utilizando como insumo as decisões dos ADRs, a RFC e o template estrutural `_work/templates/fdd_template.md`.
   - *Conteúdo gerado:* Mapeamento de 7 fluxos operacionais completos (`FLOW-01` a `FLOW-07`), modelagem de dados para o Prisma com identificadores UUID, especificação de contratos HTTP de 7 endpoints (com payloads JSON, headers e status codes), matriz completa de erros prefixados com `WEBHOOK_*`, políticas de resiliência e a seção mandatória de integração detalhando a extensão de 6 arquivos reais do OMS (`order.service.ts`, `schema.prisma`, middlewares, Pino e database).

5. **Etapa 5 — Redação do Product Requirements Document (`docs/PRD.md`)**:
   - *Como o fluxo foi adotado:* O PRD foi redigido na sequência da RFC e do FDD. Essa escolha estratégica garantiu que a visão de produto e negócio estivesse estritamente respaldada pelas decisões de viabilidade técnica já acordadas, evitando que fossem prometidas capacidades que a engenharia havia descartado.
   - *Uso de Skill Especializada:* Conduzido através da skill [`prd-generator`](.agents/skills/prd-generator/SKILL.md), que governou as 12 seções mandatórias do template `_work/templates/prd_template.md`.
   - *Ciclos de Refinamento:* Foram realizados ciclos sucessivos de auditoria e ajuste da IA (registrados em `_work/LOG.md`), assegurando métricas quantitativas reais (taxa de entrega > 99,5%, latência < 10s no fluxo nominal), 10 requisitos funcionais rastreáveis (`RF-001` a `RF-010`), 6 não funcionais, 5 itens explicitamente fora de escopo e distinção entre decisões consolidadas e pendências de deliberação humana pré-deploy (ex: isolamento multi-tenant).

6. **Etapa 6 — Construção da Matriz de Rastreabilidade (`docs/TRACKER.md`)**:
   - *Como o fluxo foi adotado:* O tracker foi montado como instrumento central de auditoria e garantia anti-alucinação, conectando cada afirmação relevante dos documentos à sua origem factual na transcrição ou no repositório.
   - *Execução:* A IA executou varreduras cruzadas catalogando 225 itens em tabela formatada com 6 colunas obrigatórias. Obteve-se uma cobertura superior a 80% de todo o pacote documental, com 79,55% de linhas apontando para timestamps com autor (`[hh:mm] Nome`) e 46 linhas mapeando arquivos e números de linha verificados na base de código, comprovando integridade estrita.

7. **Etapa 7 — Registro da Jornada de Engenharia com IA (`README.md`)**:
   - *Como o fluxo foi adotado:* O enunciado padrão do repositório foi substituído pela narrativa documental transparente do projeto, documentando como a inteligência artificial foi empregada de forma colaborativa e controlada.
   - *Conteúdo:* Apresentação do papel do engenheiro como maestro crítico, listagem das ferramentas de IA e subagentes, diagrama do fluxo, transcrição integral em blocos de código dos prompts mais relevantes, documentação de 3 iterações de correções onde respostas imperfeitas da IA foram refinadas e guia completo de leitura da entrega.

8. **Etapa 8 — Auditoria e Conformidade dos Critérios de Aceite**:
   - *Como o fluxo foi adotado:* Inspeção sistemática final contra 100% dos requisitos de aceite do desafio.
   - *Validação:* Checagem automatizada atestando que nenhuma linha de `src/`, `prisma/`, `tests/` ou `TRANSCRICAO.md` foi modificada, validação de que nenhum link utiliza caminhos absolutos e conferência de aderência estrita a todas as exigências conceituais e estruturais do curso.

---

## Prompts Customizados

Abaixo são destacados dois prompts estruturados utilizados durante a produção:

### Prompt 1: Mapeamento Cirúrgico e Extração de Fontes sem Alucinação (Etapa 1)

```markdown
Você é o Arquiteto de Software responsável por auditar a transcrição da reunião técnica (TRANSCRICAO.md) e mapeá-la contra o código legado do repositório.

DIRETRIZES MANDATÓRIAS:
1. Para cada declaração, extraia o timestamp exato e o autor da fala no formato `[hh:mm] Nome`.
2. Separe estritamente em categorias:
   - DECISÃO FECHADA: O que foi acordado por consenso técnico.
   - REQUISITO FUNCIONAL: Capacidades operacionais que o sistema deve entregar.
   - RESTRIÇÃO TÉCNICA: Limites arquiteturais impostos (ex: MySQL existente, sem nova infra).
   - DESCARTADO / NÃO ENTRA: Ideias levantadas e rejeitadas com a respectiva justificativa técnica.
   - LACUNA / NÃO DITO: Pontos que o time não discutiu ou deixou em aberto. NUNCA preencha lacunas com suposições de mercado.
3. Para cada gancho de código citado, execute verificação no workspace (`ls`, `grep -n`) e aponte o caminho de arquivo real e intervalo de linhas. Se não existir, marque categoricamente como "NÃO EXISTE".

Gere o artefato `_work/CATALOGO.md` e apresente a listagem para conferência antes do congelamento.
```

### Prompt 2: Redação de Requisitos do PRD com Rastreabilidade Estrita (Etapa 5)

```markdown
Gere o documento `docs/PRD.md` para o Sistema de Webhooks de Notificação de Pedidos seguindo estritamente as 12 seções do template oficial em `_work/templates/prd_template.md`.

REGRAS DE CONTEÚDO E GOVERNANÇA:
1. Cada afirmação, requisito ou restrição DEVE terminar com a sua citação de origem: `[T-xx]` para a transcrição ou `[código: caminho/arquivo.ts]` para a base de código.
2. Formule no mínimo 8 Requisitos Funcionais identificados na reunião (`RF-001` em diante).
3. Inclua pelo menos 1 objetivo com métrica e meta quantitativa (ex: latência inferior a 10s e taxa de sucesso > 99,5%).
4. Na seção "Fora de Escopo", liste pelo menos 2 itens explicitamente descartados ou adiados na reunião técnica (ex: Redis Streams, retries infinitos, dashboard visual).
5. Na seção "Riscos", apresente pelo menos 2 riscos com probabilidade, impacto e ação mitigadora concreta.
6. Preserve rigorosamente as decisões dos 7 ADRs já congelados em `docs/adrs/` e os contratos do `docs/FDD.md`.
```

---

## Iterações e Ajustes Concretos

Durante os ciclos de geração e revisão com a IA, foram necessárias correções críticas registradas cronologicamente no arquivo [`_work/LOG.md`](_work/LOG.md):

1. **Correção do Contrato de HMAC-SHA256 (ADR-004 vs. PRD/RFC)**:
   - *Problema:* A IA gerou versões preliminares sugerindo como opção aberta o cálculo do HMAC sobre a concatenação `${timestamp}.${payload}` (padrão utilizado pela Stripe).
   - *Correção:* A decisão do [ADR-004](docs/adrs/ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md) congelada estipulava que o cálculo da assinatura ocorre sobre o corpo (`payload`) em UTF-8, enquanto o `X-Timestamp` é transmitido como cabeçalho independente para auditoria temporal. O prompt foi corrigido para forçar aderência estrita à decisão do ADR-004 em todo o pacote.
2. **Alinhamento da Matriz de Erros do Replay da DLQ (FDD vs. PRD)**:
   - *Problema:* Na primeira redação do PRD, a IA introduziu códigos genéricos de erro como `WEBHOOK_NOT_FOUND` e `WEBHOOK_ALREADY_REPLAYED` para o reprocessamento da Dead Letter Queue.
   - *Correção:* A matriz de erros do [FDD](docs/FDD.md) (Seção 9) já havia padronizado as respostas para `WEBHOOK_DEAD_LETTER_NOT_FOUND` (404), `WEBHOOK_INACTIVE` (409) e `WEBHOOK_ALREADY_QUEUED` (409). Os requisitos do PRD foram revisados e harmonizados para refletir exatamente os identificadores canônicos do FDD.
3. **Desambiguação da Sequência de Retentativas e Rollback do Limite de 64 KB**:
   - *Problema:* A transcrição citava "5 tentativas" e simultaneamente listava 5 intervalos de backoff (`1m, 5m, 30m, 2h, 12h`), gerando dúvida se eram 5 disparos no total ou 1 disparo inicial + 5 retentativas.
   - *Correção:* Alinhou-se no FDD e PRD a semântica de **1 tentativa inicial + até 5 retentativas** (máximo de 6 disparos cobrindo quase 15 horas de indisponibilidade), formalizando também na Deliberação A1 da RFC que a violação do teto de 64 KB acarreta *rollback* transacional de `OrderService.changeStatus` para preservar a integridade atômica da tabela de outbox.

---

## Como Navegar a Entrega

Recomenda-se a leitura dos artefatos na seguinte sequência:

```
docs/
├── adrs/                                      # 1. Decisões Arquiteturais Fundamentais
│   ├── ADR-001-outbox-transacional-no-mysql.md
│   ├── ADR-002-worker-separado-com-polling.md
│   ├── ADR-003-retry-com-backoff-e-dlq.md
│   ├── ADR-004-autenticacao-hmac-sha256-com-secret-por-endpoint.md
│   ├── ADR-005-entrega-at-least-once-com-event-id.md
│   ├── ADR-006-reuso-dos-padroes-do-projeto.md
│   └── ADR-007-payload-snapshot-e-limite-de-64kb.md
├── RFC.md                                     # 2. Proposta Técnica e Deliberações da Equipe
├── FDD.md                                     # 3. Especificação Detalhada de Implementação
├── PRD.md                                     # 4. Visão de Produto, Requisitos e Negócio
└── TRACKER.md                                 # 5. Matriz Completa de Rastreabilidade Cruzada
```

---

## Auditoria dos Critérios de Aceite do Desafio

Abaixo está a validação item a item contra a checklist oficial do desafio:

### PRD (`docs/PRD.md`)
- [x] **Arquivo existe e está em Markdown:** [`docs/PRD.md`](docs/PRD.md)
- [x] **Contém todas as 12 seções obrigatórias** (Resumo, Problema, Público, Objetivos/Métricas, Escopo, Requisitos Funcionais, Não Funcionais, Decisões, Dependências, Riscos, Critérios de Aceitação, Testes).
- [x] **Identifica no mínimo 8 requisitos funcionais:** Contém 10 requisitos (`RF-001` a `RF-010`).
- [x] **Inclui pelo menos 1 objetivo com meta quantitativa:** Meta de latência < 10s no fluxo nominal e taxa de sucesso > 99,5%.
- [x] **Seção "Fora de escopo" lista pelo menos 2 itens descartados na reunião:** webhooks inbound, envio síncrono, Redis Streams, triggers nativas, retries infinitos, truncamento de payload e dashboard visual (entre outros).
- [x] **Seção "Riscos" inclui pelo menos 2 riscos com probabilidade, impacto e mitigação:** Mapeados 5 riscos detalhados.

### RFC (`docs/RFC.md`)
- [x] **Arquivo existe e está em Markdown:** [`docs/RFC.md`](docs/RFC.md)
- [x] **Contém todas as seções obrigatórias** (Metadados com revisores da reunião, TL;DR, Contexto, Proposta Técnica, Alternativas Consideradas, Questões em Aberto, Impacto e Riscos, Decisões Relacionadas).
- [x] **Lista pelo menos 2 alternativas descartadas na reunião com trade-offs:** Envio HTTP síncrono no service, Redis Streams, triggers nativas do MySQL, retries infinitos e exactly-once.
- [x] **Lista pelo menos 2 pontos adiados ou não decididos:** Isolamento multi-tenant, vínculo temporal no HMAC, homologação prévia de segurança.
- [x] **Referencia, com link, pelo menos 2 ADRs do pacote:** Links diretos para os 7 ADRs.

### FDD (`docs/FDD.md`)
- [x] **Arquivo existe e está em Markdown:** [`docs/FDD.md`](docs/FDD.md)
- [x] **Contém todas as seções obrigatórias de especificação técnica e fluxos.**
- [x] **Seção "Contratos públicos" inclui pelo menos 4 endpoints HTTP completos com payloads e status codes:** Mapeia 8 endpoints de gestão, rotação, histórico e replay (`API-01` a `API-08`).
- [x] **Matriz de erros usa códigos com prefixo `WEBHOOK_*`:** Matriz exaustiva com códigos padronizados (`WEBHOOK_INVALID_URL`, `WEBHOOK_PAYLOAD_TOO_LARGE`, etc.).
- [x] **Seção "Integração com o sistema existente" referencia pelo menos 4 caminhos de arquivo reais:** Cita `src/modules/orders/order.service.ts`, `prisma/schema.prisma`, `src/middlewares/auth.middleware.ts`, `src/shared/logger/index.ts`, `src/middlewares/error.middleware.ts` e `src/config/database.ts`.
- [x] **Seção "Observabilidade" cita métricas, logs e tracing.**

### ADRs (`docs/adrs/ADR-NNN-*.md`)
- [x] **Pasta `docs/adrs/` contém entre 5 e 8 arquivos no formato `ADR-NNN-titulo-em-kebab-case.md`:** 7 ADRs gerados (`ADR-001` a `ADR-007`).
- [x] **Cada ADR contém Status, Contexto, Decisão, Alternativas Consideradas e Consequências.**
- [x] **Cobre pelo menos 5 das 6 decisões principais da reunião:** Cobre todas as 6 decisões + payload de 64 KB.
- [x] **Pelo menos 1 ADR referencia explicitamente arquivos ou módulos do código base:** Todos os ADRs possuem ganchos reais verificados.

### Tracker (`docs/TRACKER.md`)
- [x] **Arquivo existe e segue a tabela oficial com 6 colunas:** [`docs/TRACKER.md`](docs/TRACKER.md).
- [x] **Pelo menos 80% dos itens dos documentos têm linha correspondente:** 225 itens mapeados cobrindo PRD, RFC, FDD e ADRs.
- [x] **Pelo menos 70% das linhas têm Fonte = `TRANSCRICAO` com timestamp válido `[hh:mm] Nome`:** 179 de 225 itens (79,55%).
- [x] **Pelo menos 5 linhas têm Fonte = `CODIGO` com caminho de arquivo real:** 46 itens apontando para código-fonte verificado.

### README (`README.md`)
- [x] **Contém todas as seções obrigatórias:** Sobre o desafio, Ferramentas, Workflow, Prompts, Iterações, Como navegar.
- [x] **Lista ferramentas de IA utilizadas.**
- [x] **Exibe pelo menos 2 prompts customizados em blocos de código.**
- [x] **Descreve pelo menos 2 iterações e ajustes concretos do processo.**

### Consistência Geral e Integridade do Código
- [x] **Nenhum requisito ou restrição contradiz a transcrição ou o código.**
- [x] **Nenhum arquivo de código existente citado é inexistente no repositório:** todos os caminhos de `src/` e `prisma/` citados como existentes foram verificados. Os arquivos `src/worker.ts` e `src/modules/webhooks/*` são arquivos novos propostos no FDD/RFC, ainda a criar na implementação.
- [x] **Entrega puramente documental:** Os diretórios `src/`, `prisma/`, `tests/` e o arquivo `TRANSCRICAO.md` permanecem 100% inalterados.
