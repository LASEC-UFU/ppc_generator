"""Geração da representação gráfica do fluxo curricular (diagrama em blocos
por período, usando os macros TikZ ``\\ccheader``/``\\ccbloco`` definidos em
``templates/latex/configuracoes/Estilos.tex`` — reaproveitados do template original
porque já eram genéricos, sem nenhuma referência a Engenharia de Computação).
"""

from __future__ import annotations

from ppcgen.config import Perfil
from ppcgen.geradores.fluxo import montar_grupos_fluxo
from ppcgen.modelos import Curriculo
from ppcgen.utilitarios.latex import escapar


def gerar_representacao_grafica(curriculo: Curriculo, perfil: Perfil) -> str:
    grupos = montar_grupos_fluxo(curriculo, perfil.curso.numero_periodos)

    numero = 1
    enumeracao: dict[str, int] = {}
    ordem_colunas = [str(p) for p in range(1, perfil.curso.numero_periodos + 1) if str(p) in grupos]
    ordem_colunas += [chave for chave in grupos if not chave.isdigit()]
    for chave in ordem_colunas:
        for c in grupos[chave]:
            enumeracao[c.codigo] = numero
            numero += 1

    def ref(codigo: str) -> str:
        n = enumeracao.get(codigo)
        return f"{n:02d}" if n else ""

    colunas_tex = []
    for chave in ordem_colunas:
        componentes = grupos[chave]
        cht = sum((c.carga_horaria.teorica or 0) for c in componentes)
        chp = sum((c.carga_horaria.pratica or 0) for c in componentes)
        chd = sum((c.carga_horaria.ead or 0) for c in componentes)
        che = sum((c.carga_horaria.extensao or 0) for c in componentes)
        tot = sum(c.carga_total for c in componentes)
        titulo = f"{chave}\\textordmasculine{{}}" if chave.isdigit() else escapar(chave)
        colunas_tex.append(rf"\ccheader{{{titulo} }}{{{cht}}}{{{chp}}}{{{chd}}}{{{che}}}{{{tot}}}")
    linha_cabecalho = " & ".join(colunas_tex) + r"\\" + "\n"

    maior_coluna = max((len(grupos[c]) for c in ordem_colunas), default=0)
    linhas_corpo = ""
    for idx in range(maior_coluna):
        celulas = []
        for chave in ordem_colunas:
            componentes = grupos[chave]
            if idx < len(componentes):
                c = componentes[idx]
                ch = c.carga_horaria
                preq = " ".join(sorted(ref(p.codigo) for p in c.pre_requisitos if ref(p.codigo)))
                creq = " ".join(sorted(ref(cr.codigo) for cr in c.correquisitos if ref(cr.codigo)))
                celulas.append(
                    rf"\ccbloco{{({enumeracao[c.codigo]:02d})}}{{{escapar(c.nome)}}}"
                    rf"{{{ch.teorica if ch.teorica is not None else '--'}}}"
                    rf"{{{ch.pratica if ch.pratica is not None else '--'}}}"
                    rf"{{{ch.ead if ch.ead is not None else '--'}}}"
                    rf"{{{ch.extensao if ch.extensao is not None else '--'}}}"
                    rf"{{{c.carga_total}}}{{{preq}}}{{{creq}}}"
                )
            else:
                celulas.append(" ")
        linhas_corpo += " & ".join(celulas) + r"\\" + "\n"

    n_colunas = len(ordem_colunas)
    # Diagramas com muitas linhas podem ultrapassar a altura útil mesmo
    # depois de ajustados à largura. Nesses casos, o segundo argumento limita
    # também a altura; perfis menores preservam a proporção original.
    altura = r"0.78\textheight" if maior_coluna > 10 else "!"
    return (
        r"\begin{center}"
        "\n"
        rf"\resizebox{{\linewidth}}{{{altura}}}{{\begin{{tabular}}{{|{'c|' * n_colunas}}}"
        "\n\\hline\n"
        + linha_cabecalho
        + r"\hline"
        + "\n"
        + linhas_corpo
        + r"\hline\end{tabular}}"
        + "\n"
        + r"\end{center}"
        + "\n"
    )
