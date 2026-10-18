# Modelo de PRD (Product Requirements Document)

Este é o modelo padrão de PRD que deve ser estritamente seguido durante a execução do desafio para o documento `docs/PRD.md`.

---

# PRD: [Nome da feature]

| Campo | Valor |
| :--- | :--- |
| **Versão** | v1 |
| **Data** | AAAA-MM-DD |
| **Responsável** | [nome] |
| **Status** | Rascunho / Em revisão / Aprovado |
| **Documentos relacionados** | RFC · FDD · ADRs |

> **REGRAS DE USO (apague este bloco no documento final):**
> - O PRD responde "por que e o quê?". Não descreva stack, tabelas, algoritmos ou payloads (isso é RFC/FDD).
> - Todo requisito, número e restrição termina com a origem: `[T-xx]` (transcrição) ou `[código: caminho]`.
> - Sem origem identificável: escreva "sem origem na transcrição" ou remova o item.
> - Itens descartados ou adiados na reunião aparecem SOMENTE em "Fora de escopo".

---

## 1. Resumo e contexto da feature

Parágrafo curto (3 a 5 linhas): o que é a feature, onde ela se encaixa no sistema atual e qual resultado entrega.

---

## 2. Problema e motivação
- **Situação atual:** [o que existe hoje e qual é a lacuna] `[origem]`
- **Dor 1:** [problema priorizado] `[origem]`
- **Dor 2:** [problema priorizado] `[origem]`
- **Por que agora:** [motivação] `[origem]`

---

## 3. Público-alvo e cenários de uso

### Público-alvo
- **[Perfil 1]:** [o que precisa] `[origem]`
- **[Perfil 2]:** [o que precisa] `[origem]`

### Cenários de uso
- Quando [situação], o [perfil] consegue [resultado] `[origem]`
- Quando [situação], o [perfil] consegue [resultado] `[origem]`

---

## 4. Objetivos e métricas de sucesso

| Objetivo | Métrica | Meta | Origem |
| :--- | :--- | :--- | :--- |
| [objetivo] | [como medir] | [valor quantitativo] | `[T-xx]` ou "derivada de `[T-xx]`" |

*Metas derivadas (não ditas literalmente na reunião) devem ser marcadas como "derivada" com a fala de onde saíram.*

---

## 5. Escopo

### Incluso
- [item] `[origem]`
- [item] `[origem]`

### Fora de escopo
| Item | Situação | Motivo | Origem |
| :--- | :--- | :--- | :--- |
| [item] | Descartado | [por que] | `[T-xx]` |
| [item] | Adiado (fase futura) | [por que] | `[T-xx]` |

---

## 6. Requisitos funcionais

### RF-001 [Título curto]

[Descrição em uma frase.]

**Fluxo principal**
1. [passo]
2. [passo]

**Fluxos alternativos e exceções**
- [situação e comportamento esperado]

**Erros previstos**
- [erro do ponto de vista do usuário]

**Prioridade:** Alta / Média / Baixa  
**Origem:** `[T-xx]`

<!-- Repita o bloco para RF-002, RF-003... (mínimo de 8 no desafio) -->

---

## 7. Requisitos não funcionais

| ID | Categoria | Requisito | Origem |
| :--- | :--- | :--- | :--- |
| RNF-001 | Segurança | [requisito] | `[T-xx]` |
| RNF-002 | Confiabilidade | [requisito] | `[T-xx]` |
| RNF-003 | Desempenho | [requisito] | `[T-xx]` |
| RNF-004 | Observabilidade | [requisito] | `[T-xx]` |
| RNF-005 | Compatibilidade | [requisito, ex.: reuso de padrões existentes] | `[código: caminho]` |

*Use só categorias que tenham origem. Não preencha categorias por completude.*

---

## 8. Decisões e trade-offs principais

Resumo em linguagem de produto. O detalhe fica nos ADRs.

- **[Decisão em uma frase]**
  - **Justificativa:** [por que] `[T-xx]`
  - **Trade-off:** [o que se aceita perder]
  - **Detalhe:** ADR-NNN

---

## 9. Dependências

| Tipo | Dependência | Impacto se faltar | Origem |
| :--- | :--- | :--- | :--- |
| Externa | [equipe/sistema/terceiro] | [impacto] | `[origem]` |
| Organizacional | [decisão ou definição pendente] | [impacto] | `[origem]` |
| Técnica | [componente existente] | [impacto] | `[código: caminho]` |

---

## 10. Riscos e mitigação

### [Risco 1]
- **Probabilidade:** Baixa / Média / Alta
- **Impacto:** Baixo / Médio / Alto
- **Mitigação:** [ação]
- **Plano de contingência:** [o que fazer se acontecer]
- **Origem:** `[T-xx]`

<!-- Mínimo de 2 riscos com probabilidade, impacto e mitigação -->

---

## 11. Critérios de aceitação
- [ ] [condição verificável, ligada a um RF] (RF-001)
- [ ] [condição verificável] (RF-002)
- [ ] [condição verificável, ligada a um RNF] (RNF-001)

*Cada critério deve ser verificável por teste ou inspeção, sem adjetivos vagos.*

---

## 12. Estratégia de testes e validação

### Tipos de teste
- **Unitários:** [o que cobrem]
- **Integração:** [o que cobrem]
- **Segurança:** [o que cobrem]
- **Carga/resiliência:** [o que cobrem, se aplicável]

### Validação
- [QA manual, ambiente de teste, validação com consumidor etc.]

### Perguntas em aberto (opcional)
- [ponto levantado e não decidido, com link para a seção equivalente no RFC] `[T-xx]`
