"""Geração do arquivo ``.bib`` a partir da aba ``Bibliografia`` da matriz
curricular (Seção 3) — nunca um ``.bib`` estático em ``dados/``: o único
``.bib`` que existe é o gerado aqui, escrito em ``gerado/bibliografia.bib``
por ``ppcgen.geradores.latex.gerar_arquivos_latex``.

``ppcgen.utilitarios.latex.escapar`` é reaproveitado para os campos que o
BibTeX/biblatex tipografa (título, nota, autor...) — nunca em ``url``: o
campo ``url`` do biblatex é declarado ``verbatim`` no datamodel padrão, e
biber o escreve no ``.bbl`` com o mecanismo ``\\verb{url}...\\endverb``
(catcodes trocados antes da leitura, terminador ``\\endverb`` — não chaves),
imune a ``%``/``_``/``&``. Não reconstruir isso manualmente com
``\\url{...}`` dentro de outro campo comum (ex.: ``howpublished``): esse
``\\url{}`` fica aninhado no argumento de ``\\field{...}{...}``, que já foi
tokenizado com os catcodes normais antes do ``\\url`` conseguir proteger
qualquer coisa — um ``%`` cru na URL (comum em URLs com acentos
percent-encoded, ex. ``%C3%A7``) já vira comentário do LaTeX e trunca o
campo, quebrando a compilação. Emitir sempre o campo ``url`` nativo e deixar
o estilo bibliográfico (``style=numeric`` em ``Main.tex``) renderizar
"Disponível em: ..." sozinho via ``brazilian.lbx``.
"""

from __future__ import annotations

from ppcgen.modelos import EntradaBibliografica, ReferencialCurricular
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
        # Campo verbatim do biblatex — ver docstring do módulo. Não escapar
        # nem embrulhar em \url{} manualmente aqui.
        linhas.append(_campo("url", entrada.url))
    if entrada.nota:
        linhas.append(_campo("note", escapar(entrada.nota)))

    linhas.append("}\n")
    return "".join(linhas)


def consolidar_entradas_bibliograficas(
    bibliografia: list[EntradaBibliografica], legislacao: list[ReferencialCurricular],
) -> list[EntradaBibliografica]:
    """Combina as abas ``Bibliografia`` e ``Legislacao`` sem chaves repetidas.

    A linha de ``Bibliografia`` preserva seus metadados completos quando há a
    mesma chave; a legislação só completa URL e campos que estejam vazios.
    Uma norma sem linha bibliográfica também vira uma entrada ``@misc``.
    """
    por_chave = {entrada.chave: entrada for entrada in bibliografia}
    resultado = list(bibliografia)
    for norma in legislacao:
        chave = norma.chave_bibliografica or norma.id
        existente = por_chave.get(chave)
        if existente is not None:
            if not existente.url:
                existente.url = norma.url
            if not existente.ano and norma.ano is not None:
                existente.ano = str(norma.ano)
            if not existente.titulo:
                existente.titulo = norma.documento or norma.nome
            continue
        entrada = EntradaBibliografica(
            chave=chave,
            tipo="misc",
            titulo=norma.documento or norma.nome,
            ano=str(norma.ano) if norma.ano is not None else "",
            url=norma.url,
            nota=norma.observacoes,
        )
        por_chave[entrada.chave] = entrada
        resultado.append(entrada)
    return resultado


def gerar_bibliografia_bib(
    entradas: list[EntradaBibliografica], legislacao: list[ReferencialCurricular] | None = None,
) -> str:
    """Renderiza todas as ``entradas`` em texto BibTeX/biblatex válido,
    UTF-8, sem escapes de acentuação (o projeto compila com
    ``backend=biber`` + ``\\usepackage[utf8]{inputenc}`` — biber lê UTF-8
    nativamente, ao contrário do bibtex8/Latin-1 clássico)."""

    consolidadas = consolidar_entradas_bibliograficas(entradas, legislacao or [])
    if not consolidadas:
        return "% Nenhuma referência bibliográfica ou legislação cadastrada na matriz.\n"
    return "\n".join(_entrada_para_bib(e) for e in consolidadas)
