"""Geração do arquivo ``.bib`` a partir da aba ``Bibliografia`` da matriz
curricular (Seção 3) — nunca um ``.bib`` estático em ``dados/``: o único
``.bib`` que existe é o gerado aqui, escrito em ``gerado/bibliografia.bib``
por ``ppcgen.geradores.latex.gerar_arquivos_latex``.

``ppcgen.utilitarios.latex.escapar`` é reaproveitado para os campos que o
BibTeX/biblatex tipografa (título, nota, autor...) — nunca em ``url``, que
vai dentro de ``\\url{...}`` (verbatim: ``%``/``_``/``&`` não precisam de
escape ali, e escapá-los quebraria o link).
"""

from __future__ import annotations

from ppcgen.modelos import EntradaBibliografica
from ppcgen.utilitarios.latex import escapar

_CAMPOS_SIMPLES = (
    ("endereco", "address"),
    ("editora", "publisher"),
    ("organizacao", "organization"),
    ("instituicao", "institution"),
    ("edicao", "edition"),
    ("serie", "series"),
    ("doi", "doi"),
    ("paginas", "pages"),
    ("ano", "year"),
    ("mes", "month"),
    ("dia", "day"),
)


def _campo(nome_bibtex: str, valor: str) -> str:
    return f"  {nome_bibtex} = {{{valor}}},\n"


def _entrada_para_bib(entrada: EntradaBibliografica) -> str:
    linhas = [f"@{entrada.tipo}{{{entrada.chave},\n"]

    if entrada.autor:
        # Duplo par de chaves: protege o nome (quase sempre institucional,
        # não "Nome Sobrenome") de recapitalização automática do biblatex.
        linhas.append(_campo("author", "{" + escapar(entrada.autor) + "}"))
    if entrada.titulo:
        linhas.append(_campo("title", escapar(entrada.titulo)))

    for atributo, nome_bibtex in _CAMPOS_SIMPLES:
        valor = getattr(entrada, atributo)
        if valor:
            linhas.append(_campo(nome_bibtex, escapar(valor)))

    if entrada.url:
        # \url{} é verbatim (pacote url/hyperref) — não escapar o conteúdo.
        linhas.append(_campo("howpublished", "Disponível em: \\url{" + entrada.url + "}"))
    if entrada.nota:
        linhas.append(_campo("note", escapar(entrada.nota)))

    linhas.append("}\n")
    return "".join(linhas)


def gerar_bibliografia_bib(entradas: list[EntradaBibliografica]) -> str:
    """Renderiza todas as ``entradas`` em texto BibTeX/biblatex válido,
    UTF-8, sem escapes de acentuação (o projeto compila com
    ``backend=biber`` + ``\\usepackage[utf8]{inputenc}`` — biber lê UTF-8
    nativamente, ao contrário do bibtex8/Latin-1 clássico)."""

    if not entradas:
        return "% Nenhuma referência bibliográfica cadastrada na aba Bibliografia da matriz.\n"
    return "\n".join(_entrada_para_bib(e) for e in entradas)
