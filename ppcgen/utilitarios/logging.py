"""Configuração central de logging do ppcgen.

Substitui os ``print()`` de depuração espalhados pelo script original por
níveis de log padronizados (DEBUG/INFO/WARNING/ERROR), controláveis via
``--verbose`` na CLI.
"""

from __future__ import annotations

import logging
import sys

_CONFIGURADO = False


def configurar(verbose: bool = False) -> None:
    global _CONFIGURADO
    if _CONFIGURADO:
        return
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    _CONFIGURADO = True


def obter_logger(nome: str) -> logging.Logger:
    if not _CONFIGURADO:
        configurar()
    return logging.getLogger(nome)
