#!/usr/bin/env python3
"""Verifica ADRs do projeto de Webhooks contra o catalogo, o plano e o tracker.

Uso (a partir da raiz do repositorio):
    python3 scripts/verificar_adr.py docs/adrs/ADR-001-outbox-transacional-no-mysql.md
    python3 scripts/verificar_adr.py --all

Opcoes:
    --catalogo CAMINHO   padrao: _work/CATALOGO.md
    --tracker CAMINHO    padrao: docs/TRACKER.md
    --plano CAMINHO      padrao: _work/PLANO-ADRS.md

Saida: linhas ERRO, AVISO e OK. Codigo de saida 1 se houver ao menos um ERRO.
Somente biblioteca padrao do Python 3.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

NOME_ARQUIVO = re.compile(r"^ADR-(\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ID_TRANSCRICAO = re.compile(r"(?<![A-Za-z0-9])T-\d+(?:\.\d+)?")
CAMINHO_CODIGO = re.compile(
    r"`((?:src|prisma|tests)/[^`\s:]+|package\.json|vitest\.config\.ts|tsconfig[\w.]*\.json|\.env\.example)"
    r"(?::(\d+)(?:[-\u2013](\d+))?)?`"
)
MARCADORES_PROPOSTO = ("proposto", "proposta", "nao existe", "a criar", "futur")
SECOES_OBRIGATORIAS = ["status", "contexto", "decisao", "alternativas consideradas", "consequencias"]
STATUS_VALIDOS = ("aceito", "proposto", "substituido")
CATEGORIAS_FORA_DA_DECISAO = {"DESCARTADO", "ADIADO", "FORA DE ESCOPO"}

erros: list[str] = []
avisos: list[str] = []


def erro(arq: str, regra: str, msg: str) -> None:
    erros.append(f"ERRO   [{regra}] {arq}: {msg}")


def aviso(arq: str, regra: str, msg: str) -> None:
    avisos.append(f"AVISO  [{regra}] {arq}: {msg}")


def normaliza(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def divide_celulas(linha: str) -> list[str]:
    return re.split(r"(?<!\\)\|", linha)


def carrega_catalogo(caminho: Path) -> dict[str, set[str]]:
    """Devolve {id: {categorias}} lendo as linhas '| **T-xx** | ...' do catalogo."""
    ids: dict[str, set[str]] = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\*\*(T-\d+(?:\.\d+)?)\*\*\s*\|", linha)
        if not m:
            continue
        celulas = divide_celulas(linha)
        cats: set[str] = set()
        if len(celulas) > 4:
            bruto = celulas[4].replace("`", "").replace("\\|", "|")
            cats = {c.strip().upper() for c in bruto.split("|") if c.strip()}
        ids[m.group(1)] = cats
    return ids


def secao_do_plano(plano: str, numero: str) -> str | None:
    m = re.search(rf"^## ADR-{numero}\b.*?$(.*?)(?=^## |\Z)", plano, re.M | re.S)
    return m.group(1) if m else None


def separa_secoes(texto: str) -> dict[str, str]:
    secoes: dict[str, str] = {}
    atual = None
    for linha in texto.splitlines():
        if linha.startswith("## "):
            atual = normaliza(linha[3:])
            secoes[atual] = ""
        elif atual is not None:
            secoes[atual] += linha + "\n"
    return secoes


def linhas_de_conteudo(bloco: str) -> list[str]:
    saida = []
    for linha in bloco.splitlines():
        s = linha.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("```"):
            continue
        if len(s) < 30 or re.fullmatch(r"\*\*[^*]+\*\*:?", s):
            continue
        saida.append(s)
    return saida


def tem_origem(linha: str) -> bool:
    return bool(
        ID_TRANSCRICAO.search(linha)
        or re.search(r":\d+", linha)
        or re.search(r"\[c[oó]digo:", linha, re.I)
        or "sem origem" in normaliza(linha)
        or re.search(r"\[\d{2}:\d{2}\]", linha)
    )


def verifica_tracker(arq: str, numero: str, tracker: Path) -> None:
    if not tracker.exists():
        erro(arq, "tracker", f"{tracker} nao existe")
        return
    linhas = [l for l in tracker.read_text(encoding="utf-8").splitlines() if l.strip().startswith("|")]
    do_adr = []
    for linha in linhas:
        celulas = [c.strip() for c in divide_celulas(linha)[1:-1]]
        if celulas and celulas[0].startswith(f"ADR-{numero}"):
            do_adr.append(celulas)
    if not do_adr:
        erro(arq, "tracker", f"nenhuma linha ADR-{numero} em {tracker}")
        return
    for celulas in do_adr:
        if len(celulas) != 6:
            erro(arq, "tracker", f"linha {celulas[0]} tem {len(celulas)} colunas (esperado 6)")
            continue
        _id, _doc, _tipo, _resumo, fonte, loc = celulas
        fonte_n = fonte.upper().strip()
        if fonte_n == "TRANSCRICAO":
            horas = re.findall(r"\[\d{2}:\d{2}\]", loc)
            com_nome = re.findall(r"\[\d{2}:\d{2}\]\s+[A-Za-z\u00c0-\u00ff]", loc)
            if not horas or len(horas) != len(com_nome):
                erro(arq, "tracker", f"{_id}: Localizacao deve ser '[hh:mm] Nome' (veio: {loc!r})")
        elif fonte_n == "CODIGO":
            caminho = loc.strip("` ").split(":")[0]
            if not Path(caminho).exists():
                erro(arq, "tracker", f"{_id}: caminho de codigo inexistente: {caminho}")
        else:
            erro(arq, "tracker", f"{_id}: Fonte deve ser TRANSCRICAO ou CODIGO (veio: {fonte!r})")


def verifica_adr(caminho: Path, catalogo: dict[str, set[str]], plano: str | None, tracker: Path) -> None:
    arq = str(caminho)
    m = NOME_ARQUIVO.match(caminho.name)
    if not m:
        erro(arq, "nome", "nome fora do padrao ADR-NNN-titulo-em-kebab-case.md")
        numero = None
    else:
        numero = m.group(1)

    bruto = caminho.read_text(encoding="utf-8")

    if re.search(r"REGRAS \(apague", bruto):
        erro(arq, "template", "bloco de regras do template nao foi removido")
    texto = re.sub(r"<!--.*?-->", "", bruto, flags=re.S)

    if "/home/" in texto or "file:///" in texto:
        erro(arq, "privacidade", "caminho absoluto local (/home/ ou file:///) no documento")

    for marcador in ("[..]", "AAAA-MM-DD", "ADR-NNN", "[T-xx]", "[hh:mm]", "[origem]", "[nome]"):
        if marcador in texto:
            erro(arq, "template", f"marcador de template nao preenchido: {marcador}")

    secoes = separa_secoes(texto)
    for nome in SECOES_OBRIGATORIAS:
        if nome not in secoes:
            erro(arq, "secoes", f"secao obrigatoria ausente: {nome}")
    for nome in ("questoes em aberto", "referencias"):
        if nome not in secoes:
            aviso(arq, "secoes", f"secao recomendada ausente: {nome}")

    status = secoes.get("status", "").strip().splitlines()
    if status and not normaliza(status[0]).startswith(STATUS_VALIDOS):
        erro(arq, "status", f"Status invalido: {status[0]!r} (use Proposto, Aceito ou Substituido por ADR-NNN)")

    # Alternativas
    alt = secoes.get("alternativas consideradas", "")
    n_alt = len(re.findall(r"^### ", alt, re.M))
    if n_alt == 0:
        erro(arq, "alternativas", "nenhuma alternativa (### ...) em Alternativas consideradas")
    for bloco in re.split(r"^### ", alt, flags=re.M)[1:]:
        titulo = bloco.splitlines()[0]
        if "motivo do descarte" not in normaliza(bloco):
            aviso(arq, "alternativas", f"alternativa sem 'Motivo do descarte': {titulo[:60]}")

    # Consequencias
    cons = normaliza(secoes.get("consequencias", ""))
    if "negativas" not in cons:
        erro(arq, "consequencias", "faltam consequencias negativas")
    if "trade-off" not in cons:
        erro(arq, "consequencias", "falta a linha 'Trade-off aceito'")

    # IDs de transcricao
    citados = sorted(set(ID_TRANSCRICAO.findall(texto)))
    for i in citados:
        if i not in catalogo:
            erro(arq, "catalogo", f"{i} nao existe em {Path('_work/CATALOGO.md')}")

    if plano is not None and numero is not None:
        secao_plano = secao_do_plano(plano, numero)
        if secao_plano is None:
            aviso(arq, "plano", f"ADR-{numero} nao consta em PLANO-ADRS.md")
        else:
            permitidos = set(ID_TRANSCRICAO.findall(secao_plano))
            for i in citados:
                if i in catalogo and i not in permitidos:
                    erro(arq, "plano", f"{i} nao esta entre os IDs do plano para ADR-{numero}")

    # Decisao so com itens fechados
    decisao = secoes.get("decisao", "")
    for i in sorted(set(ID_TRANSCRICAO.findall(decisao))):
        cats = catalogo.get(i, set())
        if cats and cats <= CATEGORIAS_FORA_DA_DECISAO:
            erro(arq, "decisao", f"{i} e {'/'.join(sorted(cats))} no catalogo e nao pode sustentar a Decisao")
        elif "AMBIGUO" in {normaliza(c).upper() for c in cats}:
            aviso(arq, "decisao", f"{i} e AMBIGUO no catalogo: a Decisao nao deve decidir esse ponto")

    # Caminhos e linhas de codigo
    for n_linha, linha in enumerate(texto.splitlines(), start=1):
        for m2 in CAMINHO_CODIGO.finditer(linha):
            caminho_cod, ini, fim = m2.group(1), m2.group(2), m2.group(3)
            p = Path(caminho_cod)
            if not p.exists():
                marcado = any(mk in normaliza(linha) for mk in MARCADORES_PROPOSTO)
                if marcado:
                    aviso(arq, "caminho", f"linha {n_linha}: {caminho_cod} nao existe (marcado como proposto). "
                          "O criterio de entrega proibe mencionar arquivos inexistentes: prefira descrever sem o caminho")
                else:
                    erro(arq, "caminho", f"linha {n_linha}: {caminho_cod} nao existe no repositorio")
            elif ini and p.is_file():
                total = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
                alvo = int(fim or ini)
                if alvo > total:
                    faixa = f"{ini}-{fim}" if fim else ini
                    erro(arq, "linha", f"linha {n_linha}: {caminho_cod}:{faixa} excede as {total} linhas do arquivo")

    # Origem por afirmacao (heuristica)
    sem_origem = []
    for nome in ("contexto", "decisao", "consequencias", "alternativas consideradas"):
        for linha in linhas_de_conteudo(secoes.get(nome, "")):
            if normaliza(linha).startswith("**trade-off aceito"):
                continue  # sintese das consequencias ja citadas
            if not tem_origem(linha):
                sem_origem.append(linha[:90])
    if sem_origem:
        aviso(arq, "origem", f"{len(sem_origem)} trecho(s) sem [T-xx] nem caminho:linha. Exemplos: "
              + " | ".join(sem_origem[:3]))

    # Cobertura de codigo no ADR
    if not CAMINHO_CODIGO.search(texto):
        aviso(arq, "codigo", "o ADR nao cita nenhum arquivo do codigo (ok, desde que outro ADR cite)")

    if numero is not None:
        verifica_tracker(arq, numero, tracker)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivos", nargs="*", help="ADRs a verificar")
    ap.add_argument("--all", action="store_true", help="verifica todos os docs/adrs/ADR-*.md e a contagem (5 a 8)")
    ap.add_argument("--catalogo", default="_work/CATALOGO.md")
    ap.add_argument("--tracker", default="docs/TRACKER.md")
    ap.add_argument("--plano", default="_work/PLANO-ADRS.md")
    args = ap.parse_args()

    cat_path = Path(args.catalogo)
    if not cat_path.exists():
        print(f"ERRO   [catalogo] {cat_path} nao encontrado. Rode a partir da raiz do repositorio.")
        return 1
    catalogo = carrega_catalogo(cat_path)
    if not catalogo:
        print(f"ERRO   [catalogo] nenhuma linha '| **T-xx** |' lida em {cat_path}")
        return 1

    plano_path = Path(args.plano)
    plano = plano_path.read_text(encoding="utf-8") if plano_path.exists() else None
    if plano is None:
        avisos.append(f"AVISO  [plano] {plano_path} nao encontrado: IDs nao serao conferidos contra o plano")

    arquivos = [Path(a) for a in args.arquivos]
    if args.all:
        arquivos = sorted(Path("docs/adrs").glob("ADR-*.md"))
        if not 5 <= len(arquivos) <= 8:
            erros.append(f"ERRO   [contagem] docs/adrs tem {len(arquivos)} ADR(s); o desafio exige de 5 a 8")
        numeros = [NOME_ARQUIVO.match(a.name).group(1) for a in arquivos if NOME_ARQUIVO.match(a.name)]
        if len(numeros) != len(set(numeros)):
            erros.append("ERRO   [contagem] ha numeros de ADR repetidos")
    if not arquivos:
        print("Nada para verificar. Informe um ADR ou use --all.")
        return 1

    for a in arquivos:
        if not a.exists():
            erros.append(f"ERRO   [arquivo] {a} nao existe")
            continue
        verifica_adr(a, catalogo, plano, Path(args.tracker))

    for linha in erros + avisos:
        print(linha)
    print()
    print(f"Resumo: {len(arquivos)} ADR(s) verificado(s), {len(erros)} erro(s), {len(avisos)} aviso(s).")
    if not erros:
        print("OK: sem erros. Leia os avisos antes de seguir.")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
