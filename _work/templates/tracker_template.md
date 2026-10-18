# Template e Regras — Tracker de Rastreabilidade

## 1. Objetivo

Manter uma matriz única de rastreabilidade para o pacote de documentação da feature, relacionando os itens documentados às evidências disponíveis na transcrição da reunião (`TRANSCRICAO.md`) ou no código-fonte existente.

O tracker deve permitir que qualquer pessoa verifique a origem de requisitos, decisões, restrições, propostas, contratos, consequências e outros itens relevantes registrados nos documentos.

O tracker é compartilhado por todas as etapas de documentação. As skills de PRD, RFC, FDD e ADR devem seguir este contrato ao criar ou atualizar registros.

## 2. Arquivo de destino

O arquivo consolidado deve ser mantido em:

`docs/TRACKER.md`

Este template contém as regras de geração e manutenção. Ele não substitui o arquivo consolidado nem deve ser copiado integralmente para ele.

## 3. Estrutura obrigatória

O `docs/TRACKER.md` deve conter uma tabela Markdown com as seguintes colunas, nesta ordem:

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |

### Definição das colunas

- **ID:** identificador único e estável do item rastreado.
- **Documento:** caminho relativo do arquivo em que o item está documentado.
- **Tipo:** classificação do item, como Requisito Funcional, Requisito Não Funcional, Decisão, Restrição, Alternativa Descartada, Consequência, Trade-off, Questão em Aberto, Contrato, Regra de Negócio ou Risco.
- **Conteúdo (resumo):** descrição concisa e específica da afirmação rastreada.
- **Fonte:** origem principal da evidência. Usar `TRANSCRICAO` ou `CODIGO`.
- **Localização:** referência verificável que permite encontrar a evidência na fonte.

Não alterar a estrutura das seis colunas sem necessidade comprovada.

## 4. Convenção de IDs

Os IDs devem ser únicos em todo o tracker e seguir um padrão que identifique o documento e a categoria do item.

Exemplos:

- `PRD-FR-01`
- `PRD-NFR-01`
- `RFC-ALT-01`
- `RFC-OPEN-01`
- `FDD-CONTRATO-01`
- `FDD-FLUXO-01`
- `ADR-001`
- `ADR-001-RES-01`
- `ADR-001-CONS-01`
- `ADR-001-OPEN-01`

Use numeração sequencial dentro da categoria e do documento. Antes de criar um ID, verifique se ele já existe.

Uma atualização deve preservar IDs existentes sempre que o item continuar representando a mesma afirmação. Não reutilize um ID para uma afirmação diferente.

## 5. Regras para identificar a fonte

### 5.1 Fonte TRANSCRICAO

Use `TRANSCRICAO` quando a afirmação estiver sustentada por uma fala ou passagem identificável da reunião.

A localização deve conter o timestamp e o nome do participante no formato:

`[hh:mm] Nome`

Quando a afirmação depender de mais de uma passagem, informe todas as referências relevantes.

Não atribua à reunião uma decisão, justificativa, requisito ou restrição que não esteja sustentada pela transcrição.

### 5.2 Fonte CODIGO

Use `CODIGO` quando a afirmação descrever um comportamento, estrutura ou implementação efetivamente encontrada no código existente.

A localização deve indicar o caminho real do arquivo e, quando disponível, o intervalo de linhas relevante.

Exemplo:

`src/modules/orders/order.service.ts:126-179`

Verifique o caminho e o conteúdo referenciado no código atual. Não invente arquivos, classes, métodos, linhas ou comportamentos.

Código existente e implementação proposta devem ser distinguidos explicitamente. Não use o código atual como evidência de que uma funcionalidade ainda não implementada já existe.

### 5.3 Inferências técnicas

Uma inferência técnica não é uma terceira fonte documental nem deve ser apresentada como fala da reunião ou fato comprovado pelo código.

Quando uma inferência for relevante para explicar um trade-off, risco ou consequência:

1. Identifique-a explicitamente como `Inferência técnica` no resumo.
2. Registre a evidência que motivou a inferência em `Fonte` e `Localização`.
3. Não atribua à fonte uma conclusão que ela não sustenta.
4. Diferencie o fato observado da conclusão derivada dele.

Exemplo de resumo:

`Inferência técnica: adicionar uma escrita na transação pode aumentar seu tempo de execução; a transação atual é observada no código.`

Fonte: `CODIGO`

Localização: `src/modules/orders/order.service.ts:126-179`

A evidência deve ser real e pertinente. A inferência não deve ser apresentada como uma decisão aprovada.

Se uma afirmação não tiver sustentação suficiente, não invente uma fonte para preencher a tabela. Registre a lacuna no documento ou no processo de revisão apropriado.

## 6. Regras de granularidade

Cada linha deve rastrear um item identificável e verificável.

- Separe afirmações quando elas tiverem origens diferentes ou precisarem de verificações independentes.
- Não agrupe vários requisitos ou decisões independentes em uma única linha apenas para reduzir o tamanho do tracker.
- Não crie uma linha para cada frase trivial: priorize requisitos, decisões, restrições, regras, contratos, riscos, alternativas, consequências e demais afirmações relevantes para implementação ou revisão.
- O resumo deve corresponder ao conteúdo efetivamente registrado no documento indicado.
- A referência de origem deve sustentar o resumo completo, não apenas uma parte dele.
- Quando uma afirmação depender de várias fontes, liste todas as referências relevantes ou divida a afirmação em itens menores.

## 7. Regras específicas por tipo de documento

### PRD

Rastrear os requisitos funcionais e não funcionais, métricas, itens de escopo, exclusões, dependências e riscos relevantes.

### RFC

Rastrear a proposta arquitetural, alternativas consideradas, trade-offs, riscos e questões em aberto relevantes.

### FDD

Rastrear contratos de API, fluxos, regras de negócio, validações, códigos de erro, mecanismos de resiliência e integrações com o código existente.

### ADRs

Rastrear decisões, contexto relevante, alternativas, restrições, consequências, trade-offs e questões em aberto.

As categorias acima são orientações de cobertura. Cada skill deve avaliar quais itens são identificáveis e relevantes em seu documento, sem criar registros artificiais para cumprir uma quantidade.

## 8. Manutenção incremental do tracker

Ao gerar ou revisar um documento:

1. Leia o `docs/TRACKER.md` existente, se houver.
2. Identifique os itens rastreáveis do documento em trabalho.
3. Confira cada item contra sua fonte.
4. Crie os registros ausentes e atualize os registros afetados.
5. Preserve os registros dos demais documentos.
6. Verifique IDs duplicados, caminhos, referências e consistência dos resumos.
7. Não remova registros de outras skills durante a atualização.
8. Se um item for removido ou deixar de ser válido, revise o registro correspondente em vez de manter uma afirmação desatualizada.
9. Ao final, confira a cobertura global do tracker em relação ao pacote documental.

O tracker pode ser montado incrementalmente durante a geração dos documentos ou consolidado após a produção deles. Em ambos os casos, a versão final deve cobrir o pacote completo.

## 9. Validação obrigatória

Antes de considerar a atualização concluída, verificar:

- [ ] A tabela contém exatamente as seis colunas obrigatórias.
- [ ] Todos os IDs são únicos.
- [ ] Todos os caminhos de documentos apontam para arquivos existentes.
- [ ] As referências da transcrição existem e correspondem ao timestamp e participante indicados.
- [ ] Os caminhos de código existem e sustentam as afirmações registradas.
- [ ] Nenhuma implementação proposta foi descrita como comportamento existente.
- [ ] Inferências estão identificadas e não são atribuídas indevidamente à transcrição ou ao código.
- [ ] Cada resumo é sustentado pela localização indicada.
- [ ] Os registros de outros documentos foram preservados.
- [ ] A cobertura mínima exigida pelo desafio foi verificada sobre o conjunto completo de documentos.

## 10. Critérios de aceite do desafio

A versão final de `docs/TRACKER.md` deve cumprir os critérios definidos no enunciado:

- Pelo menos 80% dos itens identificáveis dos documentos devem ter uma linha correspondente.
- Pelo menos 70% das linhas devem usar `Fonte = TRANSCRICAO` com localização no formato `[hh:mm] Nome`.
- Pelo menos cinco linhas devem usar `Fonte = CODIGO` e apontar para caminhos reais do código.

Esses percentuais devem ser calculados sobre a tabela consolidada. Não invente registros, fontes ou referências para atingir as metas.

O cumprimento dos percentuais não substitui a revisão semântica: uma referência só é válida quando realmente sustenta a afirmação rastreada.