"""Geração das tabelas LaTeX (``longtblr``) do corpo do PPC.

Ao contrário do script legado — que tinha uma função quase idêntica por
tabela (``buildTabDisciplinas``, ``buildTabDisciplinasEQUIV``,
``buildTabDisciplinasREF``, ``buildTabDisciplinasDCN``... todas repetindo o
mesmo cabeçalho/rodapé) — aqui há um pequeno conjunto de funções
parametrizáveis reaproveitadas por todos os geradores de tabela.
"""

from __future__ import annotations

from ppcgen.modelos import ComponenteCurricular, Correquisito, Equivalencia, PreRequisito
from ppcgen.utilitarios.latex import escapar
from ppcgen.utilitarios.textos import ordinal, texto_ou_travessao


def _linha(*celulas: str) -> str:
    return "    " + " & ".join(celulas) + r" \\" + "\n"


def formatar_requisito(requisito: PreRequisito | Correquisito, nomes_por_codigo: dict[str, str]) -> str:
    """Texto de um pré-requisito/correquisito para exibição em tabela.

    Um requisito pode se referir a outro componente (por código) ou a uma
    carga horária mínima acumulada (``carga_horaria_minima`` — Seção 9,
    "requisitos por carga horária modelados explicitamente") — nunca a um
    pseudo-código como ``"*"``.
    """

    carga_minima = getattr(requisito, "carga_horaria_minima", None)
    if not requisito.codigo and carga_minima is not None:
        return f"{carga_minima} horas integralizadas"
    return escapar(nomes_por_codigo.get(requisito.codigo, requisito.codigo))


def formatar_lista_requisitos(
    requisitos: list, nomes_por_codigo: dict[str, str], vazio: str = "Livre"
) -> str:
    formatados = [formatar_requisito(r, nomes_por_codigo) for r in requisitos]
    return "; ".join(f for f in formatados if f) or vazio


def tabela_componentes(
    componentes: list[ComponenteCurricular],
    titulo: str,
    label: str,
    incluir_total: bool = True,
) -> str:
    """Tabela padrão: Componente | Código | CH Teór. | CH Prát. | CH EaD | CH Ext. | CH Total."""

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[l,m,wd=58mm]Q[l,m,wd=22mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=9mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{10pt}}{{12pt}}\selectfont}},
}}
    \textbf{{Componente}} & \textbf{{Código}} & \textbf{{CH Teór.}} & \textbf{{CH Prát.}} & \textbf{{CH EaD}} & \textbf{{CH Ext.}} & \textbf{{CH Total}} \\
"""
    corpo = ""
    for c in componentes:
        ch = c.carga_horaria
        corpo += _linha(
            escapar(c.nome),
            escapar(c.codigo),
            texto_ou_travessao(ch.teorica),
            texto_ou_travessao(ch.pratica),
            texto_ou_travessao(ch.ead),
            texto_ou_travessao(ch.extensao),
            texto_ou_travessao(ch.total),
        )
    if not componentes:
        # Um `longtblr` só com cabeçalho, sem nenhuma linha de corpo, falha
        # ao compilar (tabularray espera ao menos uma linha). Uma lista
        # vazia é um estado real (ex.: nenhum componente optativo
        # cadastrado ainda), não um erro de geração — mantém a tabela
        # (com legenda e rótulo) em vez de omiti-la.
        corpo = "    \\SetCell[c=7]{c} Nenhum componente cadastrado. \\\\\n"

    rodape = ""
    if incluir_total and componentes:
        soma = lambda campo: sum((getattr(c.carga_horaria, campo) or 0) for c in componentes)  # noqa: E731
        rodape = (
            r"    \textbf{TOTAL} & & \textbf{"
            + str(soma("teorica"))
            + r"} & \textbf{"
            + str(soma("pratica"))
            + r"} & \textbf{"
            + str(soma("ead"))
            + r"} & \textbf{"
            + str(soma("extensao"))
            + r"} & \textbf{"
            + str(sum(c.carga_total for c in componentes))
            + r"} \\"
            + "\n"
        )

    return cabecalho + corpo + rodape + r"\end{longtblr}" + "\n"


def tabela_carga_por_grupo(
    grupos: dict[str, int],
    titulo: str,
    label: str,
    total_geral: int,
) -> str:
    """Tabela de carga horária total e percentual por grupo (núcleo/área/tipo)."""

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[l,m,wd=100mm]Q[c,m,wd=20mm]Q[c,m,wd=20mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{10pt}}{{12pt}}\selectfont}},
}}
    \textbf{{Componentes Curriculares}} & \textbf{{CH Total}} & \textbf{{Percentual}} \\
"""
    corpo = ""
    soma = 0
    for nome, carga in grupos.items():
        soma += carga
        percentual = (100 * carga / total_geral) if total_geral else 0
        corpo += _linha(escapar(nome), str(carga), f"{percentual:.1f}\\%".replace(".", ","))

    percentual_total = (100 * soma / total_geral) if total_geral else 0
    rodape = _linha(
        r"\textbf{TOTAL}",
        rf"\textbf{{{soma}}}",
        rf"\textbf{{{percentual_total:.1f}\%}}".replace(".", ","),
    )
    return cabecalho + corpo + rodape + r"\end{longtblr}" + "\n"


def tabela_enfases_formativas(
    enfases,
    titulo: str,
    label: str,
) -> str:
    """Quadro-resumo das ênfases formativas (áreas de formação optativa):
    Ênfase Formativa | Conteúdos Estruturantes | Aderência Profissional.

    Puramente descritivo — ao contrário de ``tabela_componentes``, não
    depende de nenhum componente estar vinculado a uma ênfase (o vínculo é
    inferido do nome do componente, não cadastrado aqui — ver
    ``tabela_enfase_formativa_componentes``). As duas colunas de texto
    longo usam o tipo ``X`` do próprio ``tabularray`` (equivalente ao
    ``tabularx``, sem exigir pacote adicional) para não estourar a margem
    com os textos de conteúdos/aderência, que podem ser extensos.
    """

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[l,m,wd=35mm]X[1,l,m]X[1,l,m]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{9pt}}{{11pt}}\selectfont}},
}}
    \textbf{{Ênfase Formativa}} & \textbf{{Conteúdos Estruturantes}} & \textbf{{Aderência Profissional}} \\
"""
    corpo = ""
    for enfase in enfases:
        nome = escapar(enfase.nome)
        if enfase.sigla:
            nome = f"{nome} ({escapar(enfase.sigla)})"
        corpo += _linha(
            nome,
            escapar(enfase.conteudos_estruturantes) or "--",
            escapar(enfase.aderencia_profissional) or "--",
        )
    if not enfases:
        corpo = "    \\SetCell[c=3]{c} Nenhuma ênfase formativa cadastrada. \\\\\n"

    return cabecalho + corpo + r"\end{longtblr}" + "\n"


def tabela_enfase_formativa_componentes(
    componentes: list[ComponenteCurricular],
    titulo: str,
    label: str,
) -> str:
    """Componentes de uma Ênfase Formativa: Código | Componente | CH Total |
    Natureza. Chamada só quando ``componentes`` não é vazio (quem gera
    decide isso, mesmo padrão de pular a escrita do arquivo usado por
    Competências/Conteúdos/Temas) — não tem guarda de lista vazia própria.

    ``componentes`` já deve vir ordenado por quem chama, pela posição do
    código na célula ``componentes`` da aba ``EnfasesFormativas``; esta
    função só formata, não ordena. O nome exibido é o nome completo
    cadastrado, sem reescrever nem esconder nada."""

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[l,m,wd=25mm]X[1,l,m]Q[c,m,wd=15mm]Q[c,m,wd=20mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{9pt}}{{11pt}}\selectfont}},
}}
    \textbf{{Código}} & \textbf{{Componente}} & \textbf{{CH Total}} & \textbf{{Natureza}} \\
"""
    corpo = ""
    for c in componentes:
        corpo += _linha(escapar(c.codigo), escapar(c.nome), texto_ou_travessao(c.carga_total), "Optativa")

    return cabecalho + corpo + r"\end{longtblr}" + "\n"


def tabela_prerequisitos(
    componentes: list[ComponenteCurricular],
    titulo: str,
    label: str,
    nomes_por_codigo: dict[str, str],
) -> str:
    """Tabela: Período | Componente | Código | Pré-requisitos | Correquisitos."""

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[c,m,wd=10mm]Q[l,m,wd=43mm]Q[l,m,wd=19mm]Q[l,m,wd=31mm]Q[l,m,wd=31mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{9pt}}{{11pt}}\selectfont}},
}}
    \textbf{{Período}} & \textbf{{Componente}} & \textbf{{Código}} & \textbf{{Pré-requisitos}} & \textbf{{Correquisitos}} \\
"""
    corpo = ""
    for c in componentes:
        periodo = ordinal(c.periodo) if c.periodo is not None else "--"
        preq = formatar_lista_requisitos(c.pre_requisitos, nomes_por_codigo)
        creq = formatar_lista_requisitos(c.correquisitos, nomes_por_codigo)
        corpo += _linha(periodo, escapar(c.nome), escapar(c.codigo), preq, creq)
    return cabecalho + corpo + r"\end{longtblr}" + "\n"


def tabela_referencia(
    componentes: list[ComponenteCurricular],
    titulo: str,
    label: str,
    nota_referencia: str,
) -> str:
    """Tabela simples: Período | Componente | Código, com nota de referência normativa."""

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
    remark{{\small \textbf{{Referência}}}} = {{\small {escapar(nota_referencia)}}}
]{{
    colspec = {{Q[c,m,wd=17mm]Q[l,m,wd=91mm]Q[l,m,wd=23mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{10pt}}{{12pt}}\selectfont}},
}}
    \textbf{{Período}} & \textbf{{Componente}} & \textbf{{Código}} \\
"""
    corpo = ""
    for c in componentes:
        periodo = ordinal(c.periodo) if c.periodo is not None else "Optativa"
        corpo += _linha(periodo, escapar(c.nome), escapar(c.codigo))
    return cabecalho + corpo + r"\end{longtblr}" + "\n"


def tabela_equivalencias(
    equivalencias: list[Equivalencia],
    por_codigo: dict[str, ComponenteCurricular],
    titulo: str,
    label: str,
) -> str:
    """Tabela: Componente (origem) | Código | CH Total | Equivale a.

    A origem tipicamente não está mais na matriz atual (componente de um
    currículo anterior — Seção 23); quando ausente, usa o próprio código e
    a observação registrada como descrição, em vez de omitir a linha.
    """

    cabecalho = rf"""\begin{{longtblr}}[
    theme = ppc,
    caption = {{{titulo}}},
    label = {{tab:{label}}},
]{{
    colspec = {{Q[l,m,wd=43mm]Q[l,m,wd=22mm]Q[c,m,wd=13mm]Q[l,m,wd=53mm]}},
    colsep = 2pt,
    rowhead = 1,
    row{{odd}} = {{bg=CinzaClaro}},
    row{{1}} = {{bg=AzulEscuro, fg=white}},
    cells = {{font=\fontsize{{9pt}}{{11pt}}\selectfont}},
}}
    \textbf{{Componente}} & \textbf{{Código}} & \textbf{{CH Total}} & \textbf{{Equivale a}} \\
"""
    corpo = ""
    for equivalencia in equivalencias:
        origem = por_codigo.get(equivalencia.codigo_origem)
        destino = por_codigo.get(equivalencia.codigo_destino)
        nome_origem = origem.nome if origem is not None else escapar(equivalencia.observacao) or "--"
        carga = texto_ou_travessao(origem.carga_total if origem is not None else None)
        descricao_destino = (
            f"{equivalencia.codigo_destino} {destino.nome}" if destino is not None else equivalencia.codigo_destino
        )
        corpo += _linha(
            escapar(nome_origem),
            escapar(equivalencia.codigo_origem),
            carga,
            escapar(descricao_destino),
        )
    return cabecalho + corpo + r"\end{longtblr}" + "\n"
