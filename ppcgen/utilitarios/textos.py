"""Utilitários de normalização de texto usados pelos geradores."""

from __future__ import annotations

import re

from unidecode import unidecode


def slug(texto: str) -> str:
    """Normaliza um texto para uso como nome de arquivo/label LaTeX.

    Equivalente ao padrão usado no script legado
    (``unidecode(nome).replace(" ", "_").lower()``), mas centralizado e
    também removendo pontuação que antes era tratada caso a caso.
    """

    texto = unidecode(texto)
    texto = texto.replace(" e ", " ").replace(" de ", " ").replace(" da ", " ")
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = texto.strip().replace(" ", "_")
    return texto.lower()


def ordinal(numero: int) -> str:
    """Formata um número de período como ordinal em português (ex.: ``3º``)."""

    return f"{numero}\\textordmasculine{{}}"


def texto_ou_travessao(valor: int | None, simbolo: str = "--") -> str:
    """Formata uma carga horária opcional, usando ``simbolo`` quando ausente."""

    return simbolo if valor is None else str(valor)
