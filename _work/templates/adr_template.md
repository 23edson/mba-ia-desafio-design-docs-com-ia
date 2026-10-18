# ADR-NNN: [Decisão em uma frase]

| Campo | Valor |
| --- | --- |
| Status | Proposto / Aceito / Substituído por ADR-NNN |
| Data | AAAA-MM-DD (data de elaboração; a reunião não registrou data) |
| Decisores | [quem fechou a decisão, conforme o catálogo] |
| Origem | [T-xx] · [hh:mm] Nome |

<!--
REGRAS (apague este bloco no documento final)
- Um ADR = uma decisão. Fluxos, schema e payloads de exemplo ficam no FDD.
- Toda afirmação termina com [T-xx] (transcrição) ou [código: `caminho:linha`] (código verificado no mapa).
- Alternativa não discutida na reunião: marque "(plausível, não discutida)" no título dela.
- Decisão cita só itens fechados. Descartados e adiados ficam em Alternativas ou Questões em aberto.
- Ambiguidades e lacunas não se decidem: apresente as leituras e registre em Questões em aberto.
- Consequências têm lado negativo e uma linha de trade-off explícito.
-->

## Status

Aceito

<!-- Valores possíveis: Proposto, Aceito, Substituído por ADR-NNN. Decisão fechada na reunião = Aceito. -->

## Contexto

Qual problema ou necessidade levou a esta decisão, e quais restrições existiam (da reunião e do código). De 3 a 6 linhas. [origem]

## Decisão

Decidimos [escolha], porque [motivo principal]. [origem]

## Alternativas consideradas

### Alternativa 1: [nome]

- **Prós:** [..] [origem]
- **Contras:** [..] [origem]
- **Motivo do descarte:** [..] [origem]

### Alternativa 2: [nome] (plausível, não discutida)

- **Prós:** [..]
- **Contras:** [..]
- **Motivo do descarte:** [..]

## Consequências

**Positivas**

- [..] [origem]

**Negativas**

- [..] [origem]

**Trade-off aceito:** [o que se ganha em troca do que se perde, em uma frase]

## Questões em aberto

- [ponto ambíguo, lacuna ou adiado que toca esta decisão, com o ID do catálogo] [T-xx]

## Referências

- Transcrição: [hh:mm] Nome
- Código: `caminho/real/do/arquivo.ts:linha` (somente arquivos que existem e estão no mapa)
- Documentos relacionados: [RFC](../RFC.md) · [FDD](../FDD.md) · [ADR-NNN](./ADR-NNN-titulo.md)