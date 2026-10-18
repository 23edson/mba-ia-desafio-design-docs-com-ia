---
name: adr-generator
description: Gera Architecture Decision Records (ADRs) do projeto de Webhooks de Notificação de Pedidos em docs/adrs/, um por vez, a partir do catálogo congelado da transcrição (_work/CATALOGO.md), do mapa de código congelado (_work/MAPA-CODIGO.md), do plano de ADRs (_work/PLANO-ADRS.md) e do template (_work/templates/adr_template.md). Use sempre que o usuário pedir para gerar, criar, escrever, refazer ou revisar um ADR (por exemplo "gere o ADR-001", "próximo ADR", "gere os ADRs", "refaça o ADR de HMAC"), mesmo que não diga "skill". Também use para validar ADRs já existentes e para atualizar as linhas de ADR no docs/TRACKER.md.
---

# Gerador de ADRs

Gera um ADR por invocação, sempre com a mesma estrutura baseada em `_work/templates/adr_template.md`, apenas com fatos rastreáveis ao catálogo da transcrição ou ao mapa do código. O usuário não escreve prompt por ADR: ele diz qual ADR quer (ou "o próximo"), e tudo o mais vem dos arquivos abaixo.

> **Raiz do repositório:** Identifique a raiz real do repositório no ambiente de execução verificando a presença conjunta dos diretórios esperados (`docs/`, `_work/`, `src/`, `prisma/`, `tests/`) e dos arquivos necessários ao fluxo (`_work/CATALOGO.md`, `_work/MAPA-CODIGO.md`, `_work/PLANO-ADRS.md`). Não dependa do nome da pasta, do nome do clone nem de caminhos absolutos predefinidos. Resolva todos os caminhos relativos e os arquivos da skill a partir dessa raiz real identificada. Se não for possível identificar inequivocamente a raiz do repositório, interrompa a operação e solicite esclarecimento ao usuário em vez de assumir um diretório.

## Fontes (leia só o que o ADR pedido precisa)

| Arquivo | Papel | Como usar |
| --- | --- | --- |
| `_work/PLANO-ADRS.md` | Lista os ADRs: número, nome do arquivo, decisão, IDs `T-xx` permitidos, âncoras de código, o que o ADR não pode decidir | Leia a entrada do ADR pedido. É o que substitui um prompt por ADR |
| `_work/templates/adr_template.md` | Template oficial de ADR do projeto | Estrutura obrigatória de seções e metadados a seguir |
| `_work/CATALOGO.md` | Fonte de verdade da reunião (congelada, somente leitura) | Leia só as linhas dos IDs permitidos pelo plano (use `grep`) |
| `_work/MAPA-CODIGO.md` | Fatos verificados do código (congelado, somente leitura) | Leia só as seções que o plano aponta |
| `_work/INDICE.md` | Itens que não entram, ambiguidades, lacunas | Consulte antes de escrever Decisão e Alternativas |
| `_work/templates/tracker_template.md` | Template e regras do tracker de rastreabilidade | Leia antes de criar ou atualizar `docs/TRACKER.md` e siga integralmente suas regras |

## Fluxo

1. **Integridade.** A partir da raiz real identificada do repositório, rode `sha256sum -c _work/CATALOGO.sha256` e `sha256sum -c _work/MAPA-CODIGO.sha256`. Se algum falhar, pare e avise o usuário. Não gere nada sobre uma base alterada.
2. **Escolha o ADR.** Se o usuário deu um número, use-o. Se disse "o próximo", pegue o primeiro ADR de `_work/PLANO-ADRS.md` cujo arquivo ainda não existe em `docs/adrs/`. Se disse "todos", gere um por vez, rodando a verificação (passo 6) entre eles, e pare no primeiro erro.
3. **Reúna as fontes.** Leia a entrada correspondente em `_work/PLANO-ADRS.md`, o template em `_work/templates/adr_template.md`, as linhas do catálogo com os IDs permitidos e as seções do mapa indicadas. Não leia o catálogo inteiro: isso incentiva misturar decisões de ADRs diferentes.
4. **Escreva** `docs/adrs/<arquivo do plano>` seguindo exatamente as seções do template (`_work/templates/adr_template.md`).
5. **Atualize `docs/TRACKER.md`** conforme a seção **Rastreabilidade** abaixo e as regras de `_work/templates/tracker_template.md`.
6. **Verifique (validação estrutural e revisão semântica).**
   - **Localização e execução do script:** localize o diretório real desta skill no ambiente de execução (sem pressupor um nome fixo para o repositório nem inventar caminhos) e confirme que `<diretorio-real-da-skill>/scripts/verificar_adr.py` existe antes de executá-lo. Execute o script a partir da **raiz real do repositório**: `python3 <diretorio-real-da-skill>/scripts/verificar_adr.py docs/adrs/<arquivo>`. Se não conseguir localizar ou executar o script, informe claramente a limitação ao usuário e **não declare que a validação foi concluída**. Mostre a saída, corrija os `ERRO` e regere. Os `AVISO` precisam ser lidos e justificados ao usuário. Ao terminar o último ADR, rode `--all` para conferir a contagem (de 5 a 8 arquivos) e a consistência do conjunto. O script confere: seções obrigatórias (Status, Contexto, Decisão, Alternativas consideradas, Consequências), IDs `T-xx` contra o catálogo e contra o plano, itens descartados ou adiados na Decisão, caminhos e linhas de código, placeholders esquecidos e as linhas do tracker.
   - **Revisão semântica obrigatória:** a aprovação no script não deve ser tratada como prova de correção semântica. Após executar o script, realize uma revisão semântica do ADR produzido verificando explicitamente:
     - Se cada decisão é sustentada pelos IDs permitidos no plano;
     - Se a seção "Decisão" contém apenas decisões fechadas e não incorpora itens descartados, adiados ou fora de escopo;
     - Se todas as alternativas exigidas por `_work/PLANO-ADRS.md` foram consideradas, sem remoções ou transferências indevidas;
     - Se os motivos históricos de descarte estão apoiados na transcrição;
     - Se as consequências positivas, negativas e o trade-off decorrem tecnicamente da decisão e das evidências;
     - Se afirmações absolutas distinguem corretamente persistência, entrega e processamento completo;
     - Se referências a código apontam para arquivos existentes e linhas verificáveis;
     - Se `docs/TRACKER.md` representa fielmente as afirmações do ADR e suas fontes, conforme `_work/templates/tracker_template.md`.
7. **Registre.** Acrescente ao fim de `_work/LOG.md` uma entrada com data e hora, o ADR gerado, as fontes usadas (IDs e seções do mapa), os arquivos gerados/alterados, as pendências e o campo `Correção do usuário:` em branco. Não escreva o que não aconteceu.
8. **Relate em poucas linhas**: arquivo gerado, o que ficou como questão em aberto, avisos da verificação. Pare. Não gere o ADR seguinte sem o usuário pedir, a menos que ele tenha dito "todos".

## Regras de conteúdo

1. **Toda afirmação termina com origem verificável (sem fabricar referências):** mantenha a distinção estrita entre evidência histórica, fato verificado no código e análise técnica, e nunca invente referências para satisfazer a exigência de rastreabilidade:
   - **Fatos da reunião:** devem referenciar os IDs correspondentes no formato `[T-xx]`.
   - **Fatos do código:** devem referenciar caminhos e linhas reais no formato `[código: `caminho:linha`]`, com base no mapa de código congelado (`_work/MAPA-CODIGO.md`).
   - **Inferências técnicas:** devem ser identificadas explicitamente como análise técnica e fundamentadas nas evidências disponíveis. Não devem ser atribuídas aos participantes da reunião.
   - **Afirmações sem evidência suficiente:** não devem ser apresentadas como fatos (saem do ADR ou são marcadas como "sem origem na reunião"). Registre a lacuna em "Questões em aberto", quando pertinente, e informe o usuário.
2. **Decisão só com item fechado.** A seção Decisão usa apenas IDs de categoria `DECISÃO FECHADA` (ou requisito e restrição ligados a ela). Nunca cite nela um item `DESCARTADO`, `ADIADO` ou `FORA DE ESCOPO`.
3. **Descartados e adiados** aparecem só em "Alternativas consideradas" (os descartados) e em "Questões em aberto" (os adiados).
4. **Ambiguidades não se decidem.** Se um ID permitido é `AMBÍGUO` (por exemplo `T-12.1`, `T-63`, `T-64`), apresente as leituras possíveis em "Questões em aberto" ou nas consequências, citando o ID. Isso vale também para as lacunas listadas em `_work/INDICE.md`.
5. **Preservar o escopo do plano:** a skill deve considerar as alternativas previstas em `_work/PLANO-ADRS.md` como referência de escopo. Uma alternativa não deve ser removida ou transferida apenas porque parece pertencer a outro nível de decisão. Se acrescentar uma alternativa que não foi discutida na reunião, marque `(plausível, não discutida)` no título dela. Mínimo de uma alternativa real por ADR.
6. **Separar fato de análise técnica:** o motivo histórico de descarte deve ser sustentado pela reunião. Prós, contras e consequências derivados tecnicamente podem ser incluídos, mas não devem ser apresentados como declarações dos participantes.
7. **Validar a força das afirmações:** a revisão deve detectar termos absolutos como “garante sem perda de eventos” e verificar se a garantia se refere à persistência, à entrega ou ao processamento completo.
8. **Consequências** têm lado positivo, lado negativo e uma linha "Trade-off aceito". Consequência negativa inventada para parecer equilibrada é pior que nenhuma: use só o que decorre da decisão e das fontes.
9. **Caminhos de arquivo e distinção entre proposta e implementação.** Cite apenas arquivos que existem e estão no mapa, com a linha. Componentes futuros devem ser descritos como propostas arquiteturais, nunca como implementações existentes. Para arquivos ainda inexistentes (o mapa os lista como `NÃO EXISTE`), descreva o papel sem escrever o caminho literal (por exemplo, "entry point dedicada do worker, sugerida na reunião"). Se precisar do caminho literal em último recurso, escreva `(proposto, não existe hoje)` na mesma linha. O critério de entrega do desafio proíbe documentos que mencionem arquivos inexistentes como existentes, e a rastreabilidade nunca deve ser fabricada para satisfazer requisitos de validação.
10. **Nomes de identificadores e artefatos propostos.** Funções, tabelas, módulos, endpoints e caminhos propostos não podem ser apresentados como código já implementado: `publishWebhookEvent` é "função proposta na reunião (T-34)", não código existente. O mesmo vale para tabelas, módulos e endpoints de webhook ainda não implementados.
11. **Sem números, campos ou endpoints inventados.** Parâmetros numéricos (2 s, 10 s, 64 KB, 24 h, 100 itens e outros) só entram se estiverem na tabela de números do catálogo.
12. **Data do ADR.** A reunião não registrou data. Use a data de elaboração e diga isso na tabela de metadados.
13. **Não duplique outros documentos.** O ADR justifica uma decisão. Fluxos passo a passo, schema e payloads de exemplo são do FDD. Linke, não copie.

## Rastreabilidade

Antes de criar ou atualizar o tracker, leia
`_work/templates/tracker_template.md` e siga integralmente
suas regras.

Atualize `docs/TRACKER.md` incrementalmente, preservando
os registros dos demais documentos.

Após a atualização, valide as referências e a cobertura
do ADR produzido. A validação estrutural não substitui
a revisão semântica das evidências.

## Limites

- Não altere `_work/CATALOGO.md`, `_work/MAPA-CODIGO.md`, `src/`, `prisma/`, `tests/` nem `TRANSCRICAO.md`.
- Se o ADR precisar de algo que não está no catálogo nem no mapa, não preencha. Escreva "sem origem na reunião" e avise o usuário.
- Não faça commit. O histórico é do usuário.
- Se o usuário discordar de uma decisão registrada no catálogo, não ajuste o ADR para acomodar: diga que o catálogo está congelado e que alterá-lo exige aviso, novo checksum e registro no log.

## Para refazer ou revisar

Quando o pedido for "refaça" ou "revise" um ADR existente, leia o arquivo atual, aponte o que viola as regras acima (incluindo preservação do escopo de `_work/PLANO-ADRS.md`, separação entre fato histórico da reunião e análise técnica, distinção entre proposta arquitetural e código existente, validação da força das afirmações quanto a termos absolutos e revisão semântica do ADR e do `docs/TRACKER.md` conforme `_work/templates/tracker_template.md`), corrija só isso e rode a verificação de novo. Preserve o que já está correto.
