---
name: rfc-generator
description: Elabora, revisa e audita o documento de Request for Comments (docs/RFC.md) do projeto de Webhooks de Notificação de Pedidos em duas etapas com aprovação obrigatória do usuário, a partir do template oficial (_work/templates/rfc_template.md), das ADRs aprovadas e congeladas (docs/adrs/ADR-*.md), do catálogo congelado da transcrição (_work/CATALOGO.md) e do mapa de código congelado (_work/MAPA-CODIGO.md). Use sempre que o usuário pedir para gerar, criar, planejar, revisar ou auditar a RFC (por exemplo "gere o RFC", "planeje a RFC", "revise o RFC.md"), mesmo que não mencione o nome da skill.
---

# Gerador de RFC (Request for Comments)

Elabora e audita o documento `docs/RFC.md` consolidando a proposta arquitetural da feature de Webhooks de Notificação de Pedidos a partir das ADRs aprovadas, do catálogo da transcrição e do mapa de código, respeitando a estrutura de `_work/templates/rfc_template.md`.

> **Raiz do repositório:** Identifique a raiz real do repositório no ambiente de execução verificando a presença conjunta dos diretórios esperados (`docs/`, `_work/`, `src/`, `prisma/`, `tests/`) e dos arquivos necessários ao fluxo (`_work/CATALOGO.md`, `_work/MAPA-CODIGO.md`, `_work/PLANO-ADRS.md`, `_work/templates/rfc_template.md`). Não dependa do nome da pasta, do nome do clone nem de caminhos absolutos predefinidos. Resolva todos os caminhos relativos a partir dessa raiz real identificada. Se não for possível identificar inequivocamente a raiz do repositório, interrompa a operação e solicite esclarecimento ao usuário em vez de assumir um diretório.

## Fontes obrigatórias

| Arquivo | Papel | Como usar |
| --- | --- | --- |
| `_work/templates/rfc_template.md` | Template oficial de RFC do projeto | Define a estrutura obrigatória de seções, tabelas e checklist de aprovação (não copiar placeholders) |
| `docs/adrs/ADR-001-*.md` a `ADR-007-*.md` | Decisões arquiteturais aprovadas e congeladas | Fundamentam as decisões consolidadas, alternativas, trade-offs e questões em aberto da RFC |
| `_work/ADRS.sha256` | Checksums SHA-256 das ADRs congeladas | Validar integridade antes e depois da geração (`sha256sum -c _work/ADRS.sha256`) |
| `_work/CATALOGO.md` e `_work/CATALOGO.sha256` | Fonte de verdade congelada da reunião (`[T-01]` a `[T-65]`) | Sustenta todos os fatos históricos, requisitos, restrições, descartes, adiamentos e ambiguidades |
| `_work/MAPA-CODIGO.md` e `_work/MAPA-CODIGO.sha256` | Fatos verificados do código-fonte (congelado) | Sustenta todas as referências a arquivos e linhas reais do código existente |
| `_work/PLANO-ADRS.md` e `_work/INDICE.md` | Matriz de escopo das ADRs, itens fora de escopo e lacunas | Consultar para garantir cobertura completa de alternativas descartadas, itens adiados e lacunas |
| `_work/templates/tracker_template.md` | Regras do matriz de rastreabilidade | Seguir caso seja solicitado atualizar `docs/TRACKER.md` |

## Fluxo de execução com aprovação obrigatória

A execução deve ocorrer em duas etapas distintas. A aprovação do usuário é obrigatória para avançar da primeira para a segunda etapa.

### Etapa 1 — Levantamento e proposta de estrutura

Antes de criar ou modificar a RFC:

1. Validar a integridade das fontes congeladas (`sha256sum -c _work/CATALOGO.sha256`, `sha256sum -c _work/MAPA-CODIGO.sha256` e `sha256sum -c _work/ADRS.sha256` quando disponível). Se alguma verificação falhar, interromper e avisar o usuário.
2. Localizar e ler o template oficial (`_work/templates/rfc_template.md`), as ADRs pertinentes (`docs/adrs/ADR-*.md`) e as fontes disponíveis (`_work/CATALOGO.md`, `_work/MAPA-CODIGO.md`, `_work/INDICE.md`).
3. Identificar as decisões arquiteturais aprovadas, seus vínculos com as ADRs e as evidências que sustentam a proposta.
4. Consolidar os requisitos, alternativas relevantes, impactos, riscos e questões em aberto.
5. Identificar conflitos, ambiguidades, fontes ausentes e decisões que ainda precisam de definição.
6. Propor como cada seção do template será preenchida, sem redigir ainda o documento RFC definitivo.

Apresentar ao usuário um relatório de planejamento com:

- **Fontes encontradas:** caminhos e finalidade de cada arquivo.
- **Decisões consolidadas:** decisões aprovadas e respectivas ADRs.
- **Proposta técnica:** visão resumida da abordagem que será apresentada na RFC.
- **Estrutura proposta:** conteúdo planejado para cada seção do template.
- **Alternativas relevantes:** alternativas que serão sintetizadas e suas referências.
- **Questões em aberto:** pendências, origem e etapa sugerida para resolução.
- **Riscos e impactos:** principais aspectos que precisam constar no documento.
- **Lacunas e conflitos:** informações ausentes ou inconsistências que possam comprometer a RFC.

Ao final, registrar a etapa em `_work/LOG.md` e solicitar aprovação explícita para prosseguir.

Não criar, sobrescrever ou modificar `docs/RFC.md` nesta etapa. Não interpretar silêncio, ausência de resposta ou solicitações de esclarecimento como aprovação.

### Ponto de aprovação

Aguardar a resposta do usuário.

- **Se aprovado:** avançar para a Etapa 2, respeitando integralmente o planejamento aprovado.
- **Se aprovado com ajustes:** incorporar os ajustes ao planejamento e apresentá-lo novamente para aprovação, quando alterarem materialmente a proposta.
- **Se houver pedido de alteração:** revisar o planejamento e aguardar a aprovação correspondente.
- **Se rejeitado:** não gerar a RFC. Perguntar como o usuário deseja proceder, se necessário.

A aprovação do planejamento autoriza a geração da RFC, mas não equivale à aprovação técnica final da RFC.

### Etapa 2 — Geração e auditoria

Somente após a aprovação explícita:

1. Gerar `docs/RFC.md` utilizando o template oficial (`_work/templates/rfc_template.md`) e o planejamento aprovado.
2. Preservar a rastreabilidade das decisões, requisitos e afirmações factuais (`[T-xx]` e caminhos verificados no código).
3. Respeitar integralmente as ADRs aprovadas e registrar todas as questões ainda pendentes sem resolvê-las por suposição.
4. Executar as verificações de consistência, referências, links, renderização Markdown e estrutura previstas na seção **Verificações de auditoria** desta skill.
5. Corrigir os problemas encontrados e repetir as verificações aplicáveis até zerar falhas.
6. Registrar a execução ao final de `_work/LOG.md` e entregar o documento informando o caminho do arquivo, as fontes utilizadas, as verificações efetivamente executadas (distinguindo-as das não realizadas) e as pendências identificadas.

Se, durante a geração, surgir uma contradição material, uma decisão arquitetural nova ou uma lacuna que altere significativamente a proposta aprovada, interromper a geração e solicitar orientação antes de prosseguir.

Não declarar a RFC aprovada tecnicamente. Sua aprovação final depende da revisão formal dos participantes e o documento deve manter o status `Em revisão`.

## Regras de conteúdo e formatação

1. **Rastreabilidade estrita e vedação à invenção:**
   - **Fatos da reunião:** devem referenciar os IDs correspondentes no formato `` `[T-xx]` ``.
   - **Fatos do código existente:** devem referenciar caminhos relativos e linhas verificadas em `_work/MAPA-CODIGO.md` (ex.: `src/modules/orders/order.service.ts:126-179`).
   - **Análises técnicas:** inferências arquiteturais devem ser identificadas explicitamente como `Análise técnica:` e nunca atribuídas como falas dos participantes da reunião.
   - **Lacunas:** o que não tiver origem na transcrição nem no código deve ser declarado como "não está na transcrição" e encaminhado à seção `## Questões em aberto`.
2. **Proibição de caminhos absolutos locais:**
   - Nunca citar caminhos absolutos de máquina (`/home/...`) nem URLs com esquema `file:///` dentro de arquivos `.md` do repositório.
   - Usar exclusivamente caminhos relativos ao repositório para código (`src/...`, `prisma/...`) e links Markdown convencionais `[texto](caminho-relativo)` para documentos relacionados (a partir de `docs/RFC.md`: `./adrs/ADR-00X-...`, `./adrs/README.md`, `./FDD.md`, `../_work/...`).
3. **Preservação das ADRs e separação de escopo:**
   - Não introduzir novas decisões arquiteturais na RFC nem alterar as ADRs congeladas.
   - Itens `DESCARTADO`, `ADIADO` ou `FORA DE ESCOPO` em `_work/CATALOGO.md` e `_work/INDICE.md` nunca entram como requisitos de escopo; devem figurar exclusivamente em `### Não escopo`, `## Alternativas consideradas` ou `## Questões em aberto`.
4. **Rigor semântico e vedação a afirmações absolutas indevidas:**
   - **Latência (< 10s):** tratar a latência inferior a 10 segundos (`[T-02]`) como meta operacional a validar em fluxo nominal (até existir definição formal de SLO), diferenciando-a da garantia efetiva da arquitetura diante de timeouts de até 10s (`[T-35]`), fila sequencial e retentativas (`[T-13]`).
   - **Ordenação por pedido e retentativas:** explicitar que a leitura sequencial em *single-worker* (`[T-07]`, `[T-11]`) mantém ordenação apenas no caminho nominal sem falhas; durante retentativas (`[T-13]`), eventos posteriores do mesmo `order_id` podem ultrapassar eventos em retry, mantendo o contrato de ordenação sob falha como questão aberta.
   - **Semântica de tentativas e ciclo de vida da DLQ:** não tratar "5 tentativas" como decisão integralmente fechada quanto à contagem (manter aberta a ambiguidade `[T-12.1]` entre 5 tentativas totais vs 1 envio inicial + 5 retries) e não usar expressões que impliquem exclusão ou movimentação definitiva da linha original da outbox ao registrar na DLQ (manter aberta a ambiguidade `[T-63]`).
   - **Segurança (Multi-tenancy, SSRF, Replay Attack e HMAC):**
     - Incluir explicitamente na análise de riscos a quebra de isolamento multi-tenant (sem pressupor que `customer_id` enviado pelo cliente é confiável `[T-27]`, `[T-50]`), o risco de *Server-Side Request Forgery* (SSRF, deixando claro que HTTPS e validação Zod `[T-18]` não bloqueiam IPs internos/privados) e ataques de repetição (*replay attack*).
     - Não tratar `X-Timestamp` (`[T-37]`) isoladamente como proteção pronta contra replay attack nem antecipar que o timestamp já compõe o HMAC; manter a participação do timestamp nos bytes assinados, a serialização do snapshot para o HMAC, a codificação de `X-Signature` e os controles anti-SSRF como especificações pendentes para o FDD.
     - Usar terminologia adequada a criptografia simétrica para o `X-Signature` (código de autenticação de mensagem / assinatura simétrica HMAC-SHA256 `[T-16]`, evitando o termo impróprio "assinatura digital").
   - **Alternativas (Redis Streams e Exactly-Once):** não afirmar que Redis Streams ou entrega *exactly-once* exigem universalmente *two-phase commit* (2PC); diferenciar o problema técnico de *dual-write* das opções arquiteturais para mitigá-lo e descrever a necessidade de coordenação bilateral em chamadas HTTP externas `[T-06]`, `[T-44]`.
   - **Classificação de riscos:** diferenciar o que está efetivamente decidido na reunião (`Definida` ou `Parcialmente definida`) do que depende de especificação ou validação no FDD (`Pendente de validação`). No risco de bloqueio do worker, diferenciar a limitação de duração de uma chamada individual pelo timeout de 10s (`[T-35]`) do gargalo sequencial em *single-worker*, registrando eventual concorrência controlada de I/O apenas como proposta a avaliar no FDD em conjunto com o contrato de ordenação por pedido (`[T-11]`, `[T-32]`).
5. **Qualidade da sintaxe Markdown:**
   - Garantir linhas em branco antes e depois de títulos (`#`, `##`, `###`, `####`), listas, tabelas e blocos de código cercados (` ```text `).
   - Não utilizar escapes indevidos (`\[`, `\]`, `\*`, `\_`, `\|`, `\``) nem inserir formatação Markdown (`**`, `` ` ``) dentro de blocos de código cercados onde ela não será renderizada.

## Verificações de auditoria (Etapa 2)

Antes de concluir a entrega na Etapa 2 (ou após qualquer revisão corretiva de `docs/RFC.md`), executar obrigatoriamente:

1. **Verificação com parser Markdown real:** processar `docs/RFC.md` com um parser Markdown real (por exemplo `markdown-it` com suporte a tabelas) e inspecionar a árvore sintática (AST) e o HTML gerado para confirmar que todos os títulos (`<h1>`–`<h4>`), listas (`<ul>`, `<ol>`, `<li>`), tabelas (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`), blocos de código (`<pre>`, `<code>`), destaques (`<strong>`, `<em>`) e links (`<a>`) foram interpretados sem sintaxe Markdown residual em nós de texto.
2. **Verificação de resolução de links relativos:** extrair todos os destinos de links do documento e verificar no sistema de arquivos (a partir do diretório `docs/`) que 100% dos caminhos apontam para arquivos existentes, incluindo os 7 links das ADRs (`./adrs/ADR-001-...` a `./adrs/ADR-007-...`).
3. **Verificação de ausência de caminhos absolutos:** executar busca por `/home/` e `file:///` em `docs/RFC.md` garantindo zero ocorrências.
4. **Verificação de integridade dos artefatos congelados:** executar `sha256sum -c _work/CATALOGO.sha256`, `sha256sum -c _work/MAPA-CODIGO.sha256` e `sha256sum -c _work/ADRS.sha256` confirmando que nenhum arquivo congelado foi modificado.
5. **Auditoria semântica e de coerência interna:** verificar a consistência entre `## Escopo e não escopo`, `## Proposta técnica`, `## Alternativas consideradas`, `## Impacto e riscos` e `## Questões em aberto`, confirmando que nenhuma decisão pendente foi antecipada como fechada e que o status permanece `Em revisão`.

## Limites

- Nunca alterar `src/`, `prisma/`, `tests/`, `TRANSCRICAO.md`, `_work/CATALOGO.md`, `_work/MAPA-CODIGO.md` nem os ADRs congelados em `docs/adrs/`.
- Sempre registrar cada interação concluída ao final de `_work/LOG.md` (sem sobrescrever entradas anteriores).
- Não realizar commits a menos que o usuário solicite explicitamente.
