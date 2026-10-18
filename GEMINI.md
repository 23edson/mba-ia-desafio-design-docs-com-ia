_work/ contém os artefatos de trabalho da feature e é versionada diretamente no repositório (comitando apenas artefatos definitivos, sem espelhar skills, arquivos congelados ou checksums sha256). Não há pasta processo/.

# Regras do projeto

- Entrega é só documental: nunca alterar `src/`, `prisma/`, `tests/` nem `TRANSCRICAO.md`.
- Toda afirmação nos docs termina com `[T-xx]` (transcrição) ou `[código: caminho]`.
- Sem origem identificável: escrever "não está na transcrição". Nunca preencher lacunas.
- Itens DESCARTADOS ou ADIADOS aparecem só em "Fora de escopo", "Alternativas" ou "Questões em aberto".
- Templates em `_work/templates/` definem só estrutura. Não copiar conteúdo, números ou nomes deles.
- Só citar caminhos de arquivo verificados com `ls`.
- Gerar um documento (ou uma seção) por vez.

## Log do processo (_work/LOG.md)
Todo prompt do usuário, a partir de agora, deve obrigatoriamente ser registrado no log.
Ao concluir cada tarefa, acrescente ao FINAL de `_work/LOG.md` (nunca reescreva entradas antigas) uma entrada:

### [AAAA-MM-DD HH:MM] [documento ou etapa]
- **Prompt (resumo):** o que foi pedido, em 1 a 2 linhas
- **Fontes usadas:** T-xx e caminhos de código consultados
- **Arquivos gerados/alterados:** caminhos
- **Pendências ou dúvidas:** o que ficou sem origem ou ambíguo
- **Correção do usuário:** (deixar em branco; o usuário preenche)

Regras: registre só o que de fato aconteceu nesta sessão. Se o usuário apontar um erro seu, acrescente na entrada correspondente: o que estava errado, como foi corrigido e por que a primeira versão falhou. Nunca invente iterações.

## Regras do Catálogo (Fonte de Verdade)
- `_work/CATALOGO.md` é a fonte de verdade e é somente leitura. Nenhum documento pode afirmar algo sem um T-xx dele ou um caminho verificado no código.
- Se um documento precisar de algo que não está no catálogo, o item vai para a seção de pendências do próprio documento, marcado "sem origem na reunião". Não se altera o catálogo para acomodar o documento.
- Itens do índice NÃO ENTRA nunca viram requisito.
- Alterar o catálogo exige aviso prévio meu e um novo checksum.
