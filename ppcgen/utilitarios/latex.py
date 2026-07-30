"""Utilitários de geração de LaTeX: escape de caracteres especiais e cabeçalho
de arquivo gerado automaticamente.
"""

from __future__ import annotations

from datetime import datetime

_MAPA_ESCAPE = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escapar(texto: str | None) -> str:
    """Escapa caracteres especiais do LaTeX em ``texto`` puro (não-LaTeX).

    Não deve ser aplicado a strings que já contenham comandos LaTeX
    propositais (ex.: textos de capítulos manuais) — apenas a dados brutos
    vindos da matriz curricular/fichas (nomes, ementas, códigos etc.).
    """

    if not texto:
        return ""
    saida = []
    for char in texto:
        saida.append(_MAPA_ESCAPE.get(char, char))
    return "".join(saida)


def cabecalho_gerado(fonte: str, versao_curricular: str = "") -> str:
    """Aviso padrão inserido no topo de todo arquivo gerado automaticamente."""

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        "% ARQUIVO GERADO AUTOMATICAMENTE.",
        "% NAO EDITE MANUALMENTE.",
        f"% Fonte: {fonte}",
        f"% Gerado em: {agora}",
    ]
    if versao_curricular:
        linhas.append(f"% Versao curricular: {versao_curricular}")
    return "\n".join(linhas) + "\n"
