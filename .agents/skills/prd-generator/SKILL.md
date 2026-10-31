---
name: prd-generator
description: Cria, revisa e audita um Product Requirements Document (PRD) seguindo estritamente o template de 12 seções do projeto (_work/templates/prd_template.md). Use quando a tarefa for produzir ou revisar docs/PRD.md, transformar transcrição em requisitos de produto ou validar a consistência de um PRD. Prioriza rastreabilidade, escopo de produto e ausência de requisitos inventados.
---

# Skill: Gerador de PRD

## Objetivo

Produzir ou revisar `docs/PRD.md` para responder **por que a feature existe e o que ela precisa entregar**, em linguagem de produto/negócio. O documento deve seguir estritamente o template canônico incluído em [`_work/templates/prd_template.md`](_work/templates/prd_template.md), manter rastreabilidade até a transcrição ou ao código existente e separar claramente fatos, requisitos, metas derivadas e lacunas.

Esta skill gera o PRD — não gera automaticamente a RFC, o FDD, as ADRs, o tracker ou o código da aplicação.

## Quando usar

Use esta skill quando o usuário pedir para:
- criar ou completar um PRD;
- converter uma transcrição, briefing ou requisitos existentes em um PRD;
- auditar um PRD contra o template, a transcrição e os demais documentos;
- ajustar o PRD para manter coerência com decisões aprovadas da RFC/ADRs e com a implementação existente.

Não use para detalhar arquitetura ou implementação. Se o usuário pedir explicitamente outro artefato, respeite o pedido em vez de produzir um PRD por conta própria.

## Fontes e precedência

Descubra e leia os documentos relevantes disponíveis no workspace ou fornecidos pelo usuário. Para o desafio de design docs, procure, quando existirem:

1. **Template de PRD (`_work/templates/prd_template.md`):** fonte canônica da estrutura e das regras de redação. Não reorganize, renomeie ou remova as 12 seções sem autorização explícita.
2. **Transcrição da reunião e catálogo/tracker (`_work/CATALOGO.md`, `docs/TRACKER.md`):** fontes primárias para problemas, usuários, cenários, requisitos, números, restrições, decisões e itens descartados/adiados. Use os IDs e timestamps existentes; não invente IDs `T-xx`.
3. **Código, testes e configuração atuais (`_work/MAPA-CODIGO.md`, `src/`, `prisma/`):** usados para sustentar a descrição da situação atual e as dependências reais. Cite o caminho exato que foi verificado.
4. **RFC aprovada e ADRs aceitas (`docs/RFC.md`, `docs/adrs/ADR-*.md`):** restrições de consistência para não propor algo incompatível com decisões técnicas já adotadas. Não use esses documentos para transformar detalhes de implementação em novos requisitos de produto.
5. **FDD e outros documentos derivados (`docs/FDD.md`):** fontes secundárias para conferir alinhamento do escopo, critérios e vocabulário. Não copie para o PRD seus detalhes de implementação.
6. **PRD existente (`docs/PRD.md`):** se o arquivo já existir, revise-o antes de substituir qualquer conteúdo. Preserve informações corretas e úteis; altere apenas o que estiver incompleto, contraditório, sem suporte ou fora do template.

Se as fontes divergirem, não reconcilie silenciosamente. Dê precedência às decisões explicitamente aprovadas para limites de escopo e registre dúvidas genuínas em “Perguntas em aberto” (Seção 12), com referência ao ponto correspondente da RFC. ADRs congeladas não devem ser editadas nem reabertas por esta skill.

Não use a web para preencher lacunas de conteúdo que deveriam vir dos arquivos do desafio, a menos que o usuário solicite pesquisa externa. Não afirme ter lido arquivos ou código aos quais não teve acesso.

## Limites do PRD

O PRD responde **“por que e o quê?”**. Portanto:

- Descreva a necessidade do usuário, os resultados esperados e o comportamento percebido pelo usuário.
- Não descreva stack, tabelas, schemas, algoritmos, arquitetura interna, pseudocódigo, payloads HTTP ou sequência de chamadas. Esses detalhes pertencem à RFC/FDD/ADRs.
- Não transforme solução técnica em requisito de produto sem uma fonte que sustente a necessidade.
- Quando necessário para uma decisão de produto, descreva o efeito esperado sem prescrever o mecanismo interno.
- Evite duplicar conteúdo detalhado da RFC/FDD. Referencie as ADRs na Seção 8 quando necessário.
- Itens que a reunião descartou ou adiou aparecem **somente na subseção “Fora de escopo” da Seção 5** do PRD. Não use o mesmo item como conteúdo de outra seção do PRD.
- Nunca descreva uma proposta técnica como se tivesse sido decidida pela reunião.

## Regras de rastreabilidade

1. Todo requisito, número, meta, restrição, afirmação importante de contexto e decisão resumida deve terminar com uma origem identificável, quando o template exigir.
2. Use os identificadores reais da transcrição, por exemplo `[T-xx]`. Não adivinhe IDs nem timestamps.
3. Para fatos verificados no repositório, use `[código: caminho/real/do/arquivo]`. Verifique o caminho antes de citá-lo e confira o trecho relevante.
4. Para meta quantitativa que não foi dita literalmente, escreva explicitamente **“derivada de `[T-xx]`”** e explique a derivação de forma breve. Não apresente meta inferida como compromisso acordado.
5. Se um item não tiver origem identificável, remova-o ou marque exatamente **“sem origem na transcrição”**, conforme o template. Não atribua uma opinião, avaliação ou recomendação à reunião sem evidência.
6. Riscos e avaliações de probabilidade/impacto podem ser análise do documento, mas não devem ser atribuídos à reunião quando ela não os quantificou. Identifique a avaliação como análise/proposta e cite a origem do risco subjacente.
7. Números de negócio, prazos, nomes de clientes, metas de latência, percentuais e limites precisam de referência. Não invente percentuais de disponibilidade, taxa de sucesso, SLA ou metas de conversão para “completar” a tabela.

## Procedimento obrigatório

### 1. Preparar as fontes

- Confirme o caminho do repositório e localize os arquivos disponíveis.
- Leia o template canônico (`_work/templates/prd_template.md`) integralmente.
- Leia a transcrição ou seus extratos rastreáveis, com atenção especial a falas sobre problema, público-alvo, dores, cenários, prioridade, objetivos, métricas, escopo, itens descartados/adiados, riscos e validação.
- Consulte código apenas para fatos sobre o sistema atual e dependências reais; não faça uma análise de implementação extensa desnecessária para o PRD.
- Consulte RFC, ADRs e FDD para consistência, não para copiar arquitetura para o documento de produto.
- Se uma fonte essencial estiver ausente, produza a melhor versão que as fontes disponíveis sustentarem e sinalize a limitação em vez de inventar conteúdo.

### 2. Extrair e classificar os fatos

Monte internamente um registro de trabalho classificando cada item como:
- problema/dor do usuário;
- perfil de usuário ou parte interessada;
- cenário de uso;
- objetivo ou resultado esperado;
- requisito funcional;
- requisito não funcional com fonte explícita;
- métrica literal ou meta derivada;
- item incluído no escopo;
- item explicitamente descartado/adiado;
- decisão/trade-off de alto nível;
- dependência;
- risco;
- critério de aceitação;
- pergunta ainda aberta.

Diferencie fala explícita, inferência necessária e proposta do documento. Não converta toda fala da reunião em requisito: respeite o contexto, as decisões e as exclusões explícitas.

### 3. Escrever usando exatamente o template

Use [`_work/templates/prd_template.md`](_work/templates/prd_template.md) como estrutura. Preserve título, metadados, numeração, ordem e formato das 12 seções:

1. Resumo e contexto da feature
2. Problema e motivação
3. Público-alvo e cenários de uso
4. Objetivos e métricas de sucesso
5. Escopo
6. Requisitos funcionais
7. Requisitos não funcionais
8. Decisões e trade-offs principais
9. Dependências
10. Riscos e mitigação
11. Critérios de aceitação
12. Estratégia de testes e validação

Remova do documento final as regras/comentários de uso presentes no template. Não acrescente novas seções nem mude a estrutura para preferências estilísticas. Preencha apenas o que as fontes suportarem.

### 4. Requisitos funcionais

- O desafio exige **no mínimo 8 requisitos funcionais** sustentados na reunião. Gere RFs atômicos, sem misturar capacidades independentes em um único requisito apenas para reduzir a contagem.
- Use IDs sequenciais e estáveis: `RF-001`, `RF-002`, etc.
- Use exatamente o bloco do template para cada RF:
  - título curto;
  - descrição em uma frase;
  - fluxo principal numerado;
  - fluxos alternativos e exceções;
  - erros previstos do ponto de vista do usuário;
  - prioridade Alta/Média/Baixa;
  - origem com ID real da transcrição.
- Mantenha o conteúdo em linguagem de produto. Fluxos devem descrever o que o usuário faz e o que o produto deve responder, não classes, métodos, tabelas, endpoints ou pseudocódigo.
- Quando não houver erro/exceção conhecido nas fontes, escreva “Não identificado na transcrição” ou “sem origem na transcrição”, em vez de inventar cenários como fatos.
- A prioridade deve refletir a urgência/ênfase documentada. Se for uma classificação editorial inferida, não alegue que foi atribuída por um participante.

### 5. Métricas e objetivos

- Inclua pelo menos um objetivo com métrica e meta quantitativa porque o critério de aceite do desafio exige isso.
- Priorize metas explicitamente presentes na transcrição. Se a reunião definir latência inferior a 10 segundos, use exatamente essa meta e cite o ID que a sustenta.
- Se precisar derivar uma meta, identifique-a como “derivada de `[T-xx]`”; explique o raciocínio brevemente e não finja consenso explícito.
- Não invente números populares como 99,5%, 99,9%, “mil eventos por segundo”, disponibilidade mensal ou conversão.
- Cada métrica precisa ser observável na prática. Descreva a forma de medição sem detalhar ferramentas de telemetria ou implementação.

### 6. Escopo

- Separe os itens incluídos dos itens explicitamente descartados ou adiados.
- Na tabela “Fora de escopo”, inclua pelo menos dois itens realmente descartados/adiados durante a reunião, com situação, motivo e origem.
- Não confunda “não mencionado” com “descartado”. Se um tema nunca foi discutido, não o inclua como decisão de exclusão.
- Não replique itens fora de escopo noutras seções do PRD.
- Mantenha o escopo em nível de capacidade de produto, sem detalhar a implementação interna.

### 7. Requisitos não funcionais

- Inclua apenas categorias sustentadas por fontes: por exemplo, desempenho, segurança, confiabilidade, observabilidade ou compatibilidade, se houver evidência.
- Cada RNF precisa de ID (`RNF-001`, etc.), categoria, requisito e origem.
- Não preencha categorias por completude. Não use um requisito de stack como se fosse necessidade de produto, salvo quando compatibilidade com o sistema existente estiver documentada e relevante.
- Requisitos de segurança que dependam de aprovação formal devem ser descritos como condição/pré-requisito, não como aprovação já realizada.

### 8. Decisões e trade-offs principais

- Resuma decisões em linguagem de produto/negócio e explique o trade-off aceito em uma ou duas frases.
- Quando aplicável, aponte o ADR correspondente (`ADR-NNN`), sem reproduzir a decisão inteira.
- Não transforme a seção em catálogo técnico, nem repita algoritmos, tabelas, headers ou schema.
- Não reabra nem altere ADRs congeladas. Se uma questão ainda não foi decidida, não a apresente como decisão fechada.

### 9. Dependências

Use a tabela do template para dependências externas, organizacionais e técnicas. Inclua somente dependências comprovadas ou necessárias para o resultado. Cite o ID de transcrição ou caminho verificado de código. Quando uma decisão estiver pendente, diga isso claramente e descreva o impacto se faltar.

### 10. Riscos e mitigação

- Inclua no mínimo dois riscos, conforme o desafio.
- Cada risco tem título, probabilidade, impacto, mitigação, plano de contingência e origem.
- Separe a fonte do risco da avaliação qualitativa de probabilidade/impacto feita durante a elaboração.
- Proponha mitigação proporcional e ligada ao contexto real. Não apresente controle proposto como implementado ou aprovado.

### 11. Critérios de aceitação

- Escreva condições verificáveis por teste ou inspeção, vinculadas a pelo menos um RF ou RNF.
- Evite termos vagos como “intuitivo”, “rápido”, “robusto” ou “seguro” sem uma condição objetiva.
- Garanta cobertura para as necessidades centrais e exceções relevantes identificadas nas fontes.
- Critérios não podem introduzir comportamento novo que não apareça nos requisitos ou nas fontes.

### 12. Testes e perguntas em aberto

- Descreva os tipos de validação adequados ao comportamento esperado: unitária, integração, segurança, carga/resiliência, QA manual ou validação com consumidor externo, apenas quando aplicáveis.
- No PRD, descreva **o que precisa ser validado**, não a implementação detalhada dos testes.
- Use “Perguntas em aberto” apenas para perguntas reais ainda não decididas. Faça link para a seção correspondente da RFC e cite a origem da pergunta.
- Não reabra questões decididas na RFC/ADRs apenas porque existe uma alternativa técnica possível.

## Checklist de validação antes de entregar

Confira todos os itens abaixo:

- [ ] O documento usa exatamente as 12 seções, na ordem do template.
- [ ] O bloco de instruções do template foi removido do PRD final.
- [ ] Há no mínimo 8 requisitos funcionais (`RF-001` em diante).
- [ ] Cada RF tem fluxo principal, alternativas/exceções, erros previstos, prioridade e origem.
- [ ] Há pelo menos um objetivo com meta quantitativa; metas não literais estão identificadas como derivadas.
- [ ] A seção “Fora de escopo” contém pelo menos dois itens realmente descartados/adiados na reunião.
- [ ] Itens descartados/adiados aparecem somente na seção 5 do PRD.
- [ ] A seção de RNFs contém apenas categorias justificadas por fonte.
- [ ] Há no mínimo dois riscos com probabilidade, impacto, mitigação, contingência e origem.
- [ ] Critérios de aceitação verificáveis estão ligados a RFs/RNFs.
- [ ] Toda afirmação importante, número ou restrição tem origem válida ou está marcada como derivada/sem origem.
- [ ] Não foram inventados IDs `T-xx`, timestamps, nomes, percentuais, compromissos ou aprovações.
- [ ] Não há stack, schema, algoritmos, contratos HTTP ou detalhes de implementação indevidos para um PRD.
- [ ] As decisões de alto nível não contradizem RFC/ADRs aprovadas; nenhum ADR foi alterado.
- [ ] Caminhos de código citados existem e sustentam a afirmação.
- [ ] O status do documento não é `Aprovado` sem aprovação explícita do usuário ou registro autoritativo.
- [ ] O PRD está em português, é objetivo e não tem placeholders, comentários de template ou frases genéricas.

Se um critério não puder ser verificado com os arquivos disponíveis, não declare a validação como concluída; registre a limitação na resposta final.

## Saída padrão

- Em um repositório de projeto, crie ou atualize **somente `docs/PRD.md`**, salvo pedido explícito para gerar arquivos adicionais.
- Se não houver workspace acessível, gere um arquivo Markdown com nome claro e entregue o caminho verificável.
- Não modifique `src/`, `prisma/`, `tests/`, configurações, RFCs ou ADRs durante uma tarefa limitada ao PRD.
- Não faça commit/push, não implemente código e não diga que testes foram executados se não foram.
- Ao concluir, resuma o arquivo criado, as fontes consultadas, a quantidade de RFs/RNFs e eventuais lacunas que permaneceram abertas.