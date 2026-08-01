"""Utilitários de apresentação seguros para os relatórios HTML gerados."""

from __future__ import annotations

from html import escape


def escapar_html(valor: object) -> str:
    """Converte um valor de dados em texto seguro para inserção em HTML.

    Relatórios são alimentados por planilhas e fichas, portanto seus campos
    não devem ser tratados como marcação confiável.
    """

    return escape(str(valor), quote=True)
