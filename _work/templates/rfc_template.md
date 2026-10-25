# RFC: [Nome da feature]

**Autor:** [nome] · **Status:** Em revisão · **Data:** AAAA-MM-DD  
**Revisores:** [participantes da reunião, com o papel de cada um]

## TL;DR

[Em 3 a 5 linhas: o problema, a proposta técnica, o ponto central da abordagem e o que precisa ser validado ou aprovado nesta revisão.]

## Contexto e problema

[Por que a solução é necessária, qual limitação ou necessidade foi identificada e o que o sistema atual não faz.]

[Referenciar as fontes da reunião (`T-xx`) e, quando aplicável, evidências do código existente (`caminho:linha`). Distinguir fatos observados de interpretações e propostas.]

## Escopo e não escopo

### Escopo

- [Capacidades e comportamentos contemplados pela proposta.]
- [Componentes, fluxos ou integrações afetados.]

### Não escopo

- [Capacidades explicitamente excluídas desta proposta.]
- [Evoluções ou responsabilidades que serão tratadas separadamente.]

[Não inferir exclusões que não tenham sido estabelecidas. Quando necessário, identificar o item como proposta sujeita à aprovação.]

## Proposta técnica

[Descrever a solução proposta em nível arquitetural: componentes envolvidos, responsabilidades, interações e fluxo geral. Priorizar decisões e seus motivos, sem antecipar detalhes de implementação que pertencem ao FDD.]

[Referenciar as ADRs que fundamentam cada decisão. Identificar explicitamente qualquer decisão nova que ainda dependa de aprovação.]

### Fluxo da solução

[Inserir um diagrama simples, se ajudar a compreender o fluxo entre componentes. Representar apenas comportamentos e interações sustentados pelas fontes ou explicitamente definidos na proposta.]

### Decisões arquiteturais aplicadas

- [Decisão]: [como a decisão registrada na ADR se aplica à proposta]. ([ADR-XXX])
- [Decisão]: [como a decisão registrada na ADR se aplica à proposta]. ([ADR-XXX])

## Alternativas consideradas

[Consolidar as alternativas relevantes para a proposta, sem reproduzir integralmente todas as análises das ADRs.]

Para cada alternativa:

- **Alternativa:** [descrição resumida].
- **Benefícios:** [vantagens identificadas].
- **Limitações:** [custos, riscos ou desvantagens identificados].
- **Motivo da não adoção:** [justificativa sustentada pelas fontes ou pela ADR correspondente].
- **Referências:** [T-xx e/ou ADR-XXX].

[Não apresentar uma alternativa como discutida ou formalmente rejeitada se isso não estiver documentado. Distinguir alternativas avaliadas na reunião de análises técnicas complementares.]

## Impacto e riscos

### Impacto no sistema existente

- **Componentes afetados:** [módulos, serviços, banco de dados e integrações identificados].
- **Compatibilidade:** [impactos em contratos, consumidores e comportamentos existentes].
- **Operação:** [processos operacionais, monitoramento, recuperação e manutenção].
- **Segurança:** [autenticação, autorização, isolamento de dados, proteção de informações e riscos pertinentes].

### Riscos e mitigações

| Risco | Impacto potencial | Mitigação proposta | Status |
|---|---|---|---|
| [Risco identificado] | [Consequência] | [Mitigação] | [Definida / Pendente de validação] |

[Incluir somente riscos pertinentes à proposta. Diferenciar mitigações já decididas de medidas ainda propostas.]

## Questões em aberto

[Registrar os pontos não decididos, adiados ou que precisam de validação antes da implementação.]

| Questão | Motivo da pendência | Responsável pela decisão | Etapa para resolução |
|---|---|---|---|
| [Questão] | [Por que permanece aberta] | [Pessoa ou papel responsável] | [Revisão da RFC / FDD / outra etapa definida] |

[Referenciar `T-xx`, ADRs ou outras evidências pertinentes. Se o responsável ainda não estiver definido, registrar essa condição em vez de atribuir alguém arbitrariamente.]

## Critérios de aprovação

[Definir o que os revisores precisam validar para aprovar a proposta.]

- [ ] A proposta atende ao problema e respeita o escopo definido.
- [ ] As decisões arquiteturais estão alinhadas às ADRs relacionadas.
- [ ] Os impactos e riscos relevantes estão identificados e possuem tratamento definido ou explicitamente pendente.
- [ ] As questões que bloqueiam a aprovação estão resolvidas.
- [ ] As questões que podem ser detalhadas posteriormente estão identificadas e possuem uma etapa de resolução.
- [ ] A proposta fornece uma base suficiente para elaboração do FDD.

**Resultado da revisão:** [Aprovada / Aprovada com pendências / Requer revisão]

**Pendências e condições para aprovação:** [Registrar, se aplicável.]

## Decisões relacionadas

- [ADR-001 — título](./adrs/ADR-001-titulo.md)
- [ADR-002 — título](./adrs/ADR-002-titulo.md)
- [Adicionar as demais ADRs pertinentes.]

## Referências e rastreabilidade

- **Fontes da reunião:** [T-xx pertinentes].
- **Código existente:** [caminho:linha, quando aplicável].
- **Documentos relacionados:** [links relativos para documentos que fundamentam a proposta].

[Garantir que afirmações factuais tenham referências verificáveis. Identificar análises técnicas como análises, sem apresentá-las como fatos observados ou decisões da reunião.]
