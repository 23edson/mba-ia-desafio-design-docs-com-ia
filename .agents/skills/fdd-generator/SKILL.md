---
name: fdd-generator
description: Cria ou audita um Feature Design Document (FDD) a partir de uma RFC aprovada, ADRs, transcrição de reunião, código existente e convenções do projeto. Use ao criar, completar, revisar ou validar um FDD técnico. Preserve as decisões arquiteturais e a rastreabilidade; resolva lacunas de implementação encaminhadas ao FDD sem inventar decisões da reunião.
---

# Gerador de FDD

Crie ou revise um **Documento de Design da Feature (FDD)** pronto para orientar a implementação, usando o template incluído em `references/FDD-TEMPLATE.md`.

## Objetivo

Produzir um FDD que explique **como construir a feature em detalhes**, mantenha rastreabilidade às fontes, corresponda ao repositório real e diferencie decisões estabelecidas, propostas técnicas e aprovações ainda necessárias. O documento deve ter detalhes suficientes para que uma pessoa desenvolvedora possa iniciar a implementação assim que os pré-requisitos explicitados forem atendidos.

## Regras para definir as fontes de verdade

Use a seguinte ordem de precedência, salvo quando o usuário indicar explicitamente outra fonte de verdade:

1. RFC mais recente aprovada e decisões arquiteturais adotadas nela.
2. Arquivos ADR presentes no workspace atual. Prefira as ADRs locais a cópias remotas antigas ou provisórias quando o projeto indicar que as versões locais são as autoritativas.
3. Transcrição da reunião e suas evidências indexadas/catalogadas, para identificar o que realmente foi dito ou decidido.
4. Código-fonte real, schema, testes, manifestos de dependências, configurações e convenções do repositório, para confirmar o comportamento atual e os pontos concretos de integração.
5. FDD existente, PRD, notas de trabalho, catálogos, mapas e outros artefatos de rastreabilidade.
6. Propostas de design claramente identificadas, quando uma lacuna técnica tiver sido explicitamente encaminhada ao FDD.

Não permita que um FDD antigo, um resumo gerado desatualizado ou uma sugestão ainda não aprovada substitua uma RFC/ADR aprovada. Não use pesquisa na web para preencher lacunas dos arquivos do projeto, salvo se o usuário pedir pesquisa externa ou se uma dependência exigir documentação atualizada. Quando houver pesquisa externa, diferencie claramente os fatos externos das evidências do projeto.

## Fluxo obrigatório de trabalho

### 1. Descobrir o workspace e os artefatos existentes

- Identifique a raiz do repositório e examine sua estrutura antes de editar qualquer coisa.
- Procure o template de FDD, `docs/FDD.md`, RFC, diretório de ADRs, PRD, transcrição e artefatos de rastreabilidade, como catálogo da transcrição ou mapa do código.
- Inspecione os arquivos-fonte, schemas, testes, manifestos de dependências, configurações, middlewares, logs e registro de rotas relevantes.
- Se o repositório não estiver disponível no ambiente, use os arquivos fornecidos na conversa. Informe quais fontes estavam acessíveis; não afirme ter inspecionado código local que não foi disponibilizado.
- Não presuma que caminhos, símbolos, versões de dependências, métodos, rotas ou classes existam. Verifique cada caminho incluído no FDD no workspace (por exemplo, com `ls`, `test -e`, `rg --files` ou equivalente) e examine os trechos pertinentes.

### 2. Montar um registro de decisões e evidências

Antes de redigir, classifique as informações relevantes como:

- **Decisão aprovada:** consta na RFC aceita ou em ADR aplicável e aceita.
- **Fato/decisão da reunião:** sustentado por referências da transcrição, como `[T-xx]`.
- **Comportamento observado na implementação:** verificado diretamente no código, schema, testes ou configuração; cite como `[código: caminho]` e inclua símbolos/linhas quando útil.
- **Detalhe de implementação delegado:** foi explicitamente deixado para o FDD e, portanto, pode ser especificado como proposta de design.
- **Decisão externa necessária:** semântica de negócio, escopo de produto, aceitação de risco, aprovação de segurança ou alteração arquitetural que o FDD não pode autorizar por conta própria.
- **Excluído/adiado:** explicitamente fora de escopo, descartado ou adiado pela RFC/ADRs.

Não transforme inferências em fatos. Se duas fontes entrarem em conflito, registre o conflito exato, respeite a precedência de fontes acima e mantenha visíveis as divergências não resolvidas, em vez de conciliá-las silenciosamente.

### 3. Auditar o FDD existente antes de redigir

- Se `docs/FDD.md` existir, audite-o seção por seção comparando-o com o template, a RFC, as ADRs, a transcrição e o código-fonte.
- Preserve o conteúdo correto e útil. Corrija informações desatualizadas, sem suporte, contraditórias ou incompletas; não reescreva apenas por preferência de estilo.
- Se não existir FDD, crie-o a partir do template incluído.
- Mantenha a estrutura de 17 seções do template, salvo autorização explícita do usuário para alterá-la. Preencha cada seção de forma útil e remova as instruções/comentários do template do FDD final.

### 4. Detalhar o design

Especifique os detalhes necessários para implementar a feature com segurança, quando aplicável:

- limites entre componentes e pontos exatos de integração no código;
- campos do modelo de dados, relacionamentos, nulabilidade, unicidade, índices, retenção e semântica de exclusão;
- limites transacionais e comportamento de rollback;
- fluxos importantes e seus caminhos de falha;
- máquina de estados do worker, critérios de elegibilidade para processamento, agendamento, semântica da contagem de tentativas, recuperação de eventos presos, seleção determinística, garantias de ordenação e ciclo de vida da DLQ/replay;
- rotas públicas da API e contratos completos de request/response/erros;
- contrato HTTP de saída, payload, cabeçalhos, entrada exata da assinatura/codificação, rotação de credenciais, critérios de sucesso de entrega, retries e semântica de deduplicação;
- códigos de erro de domínio relacionados às classes de erro realmente existentes;
- limites de autorização, isolamento por tenant, proteções contra SSRF, armazenamento/mascaramento de secrets e pré-requisitos de segurança;
- logs/métricas/tracing operacional e encerramento do worker, sem inventar ferramentas ou dependências como se já existissem;
- dependências/compatibilidade, estratégia de testes, critérios de aceite mensuráveis e riscos.

Siga as convenções reais do repositório. Citar um caminho não basta para explicar a integração: especifique o método, função, classe, registro de rota, transação ou trecho do schema que deverá ser estendido.

### 5. Tratar corretamente os pontos em aberto

**Não transforme todo detalhe não especificado em uma questão pendente.** Identifique a categoria correta:

- Se a RFC/ADR já decidiu o ponto, leve a decisão para o FDD e não a reabra.
- Se a RFC delegou explicitamente o mecanismo de implementação ao FDD (por exemplo, campos para agendamento, ordenação SQL determinística, recuperação de eventos em `processando`, classificação de respostas HTTP quando houver margem para recomendação de política ou desenho de índices), apresente uma recomendação concreta e coerente. Marque-a como `(proposta de design, sem origem na reunião)` e identifique as premissas relevantes. Prefira soluções simples e compatíveis com a stack existente; não adicione infraestrutura sem evidência ou justificativa clara.
- Se o ponto alterar comportamento de negócio, modificar uma decisão arquitetural aceita, exigir aceitação formal de risco, depender de aprovação do responsável por segurança ou depender de fatos ausentes que não possam ser recuperados, mantenha-o na **Seção 16 — Questões pendentes antes da implementação**. Inclua responsável/papel, impacto e condição para encerramento.
- Requisitos que a RFC define como bloqueadores para implementação continuam sendo bloqueadores. Descrever um controle no FDD não prova que ele foi implementado, testado ou aprovado.
- Nunca afirme que um participante fictício do cenário concedeu uma aprovação real. Quando o exercício estabelecer uma decisão para o documento, descreva-a como decisão/recomendação adotada para o exercício, não como uma reunião ou aprovação real.

### 6. Manter a rastreabilidade

Use marcadores consistentes de evidência:

- `[T-xx]` — item da transcrição/catálogo.
- `[código: caminho]` — evidência do repositório; inclua símbolo ou intervalo de linhas relevante quando apropriado.
- `[RFC: seção]` — contrato arquitetural definido na RFC.
- `[ADR-00x]` — ADR aceita relacionada.
- `(proposta de design, sem origem na reunião)` — proposta nova de implementação não decidida na reunião.

Toda afirmação técnica/arquitetural relevante, valor escolhido, caminho, interface e regra não óbvia deve remeter a uma dessas fontes. Se nenhuma fonte sustentar uma afirmação e ela não estiver marcada claramente como proposta, remova-a ou explicite a lacuna. Valores como timeout, intervalos/contagem de retries, limite de payload, frequência de polling, retenção e tamanho do lote sempre precisam de origem ou do marcador de proposta.

### 7. Usar contratos e diagramas completos

- Para cada endpoint público, inclua método/caminho, autenticação/autorização, cabeçalhos, request, resposta de sucesso, códigos de erro/status, semântica e origem.
- O template recomenda pelo menos quatro contratos de API pública neste desafio. Não invente endpoints apenas para atingir uma quantidade; registre explicitamente se o escopo documentado sustentar menos.
- Cada fluxo deve apresentar o caminho nominal e os caminhos relevantes de erro/recuperação.
- Mantenha os diagramas Mermaid sintaticamente válidos e consistentes com o texto. Diagramas ajudam a explicar, mas não substituem regras detalhadas.
- Mantenha exemplos de eventos em JSON válido e consistentes com o schema e com o contrato outbound.
- Não afirme entrega exactly-once se o desenho oferece at-least-once; diferencie tentativas de envio de recebimento confirmado.

### 8. Validar antes de concluir

Faça uma revisão final de consistência:

- As 17 seções estão presentes, ou cada omissão tem justificativa explícita.
- Cada objetivo da Seção 2 está relacionado a pelo menos um critério mensurável da Seção 14.
- As decisões correspondem à RFC/ADRs; o FDD não amplia silenciosamente o escopo.
- Cada questão pendente realmente depende de decisão/aprovação externa, e não de especificação técnica delegada ao FDD.
- Rotas, tipos, valores de enum, campos do schema, classes de erro, versões de pacotes, caminhos de arquivos e referências a linhas foram verificados.
- Retries, contagem de tentativas, DLQ, replay, idempotência, ordenação de eventos, timestamps/detalhes da assinatura, exclusão/desativação e semântica transacional são coerentes entre si.
- Os requisitos de segurança estão explícitos e não são descritos como atendidos apenas porque foram documentados.
- O status do FDD não é definido como `Aprovado` sem que o usuário ou um artefato autoritativo do projeto registre essa aprovação.
- Remova placeholders, comentários de instrução do template, afirmações sem suporte e justificativas duplicadas da RFC.
- Não execute código de implementação nem modifique arquivos-fonte, salvo solicitação explícita. Não edite a RFC ou as ADRs durante uma tarefa restrita ao FDD. Não faça commits sem solicitação.
- Não afirme que testes ou comandos foram executados se isso não ocorreu; normalmente, uma tarefa de FDD não altera código nem exige executar testes.

## Saída padrão

- Em um repositório, crie/atualize `docs/FDD.md` e nada mais por padrão, salvo quando o usuário pedir explicitamente um relatório separado ou arquivos adicionais.
- Se houver apenas arquivos fornecidos na conversa, sem acesso ao repositório, crie o FDD em um caminho claramente nomeado e informe quais evidências não estavam disponíveis.
- Na resposta final, informe de forma concisa e factual: o que foi criado/atualizado; as fontes consultadas; as principais propostas técnicas incluídas; as questões remanescentes e por quê; os bloqueadores de segurança/implementação; e as validações que não foram executadas.

## Template

Leia e use [`_work/templates/rfc_template.md`](_work/templates/rfc_template.md) como estrutura canônica de 17 seções. Se o projeto já tiver um template equivalente, compare-o com esta referência e preserve as convenções específicas do projeto, a menos que entrem em conflito com as regras acima.