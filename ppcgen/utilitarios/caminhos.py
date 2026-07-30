"""Resolução de caminhos independente do diretório de trabalho atual.

O sistema antigo (``py/gen_docs.py``) abria arquivos com caminhos relativos
codificados (ex.: ``open("py/PPC_disciplinas_final.csv")``), o que só
funcionava se o processo fosse iniciado exatamente na raiz do repositório.
Aqui, a raiz é localizada a partir da própria instalação do pacote.
"""

from __future__ import annotations

from pathlib import Path

_MARCADORES = ("pyproject.toml", ".git")


def raiz_projeto() -> Path:
    """Retorna a raiz do projeto, independente do diretório atual do terminal."""

    atual = Path(__file__).resolve().parent
    for candidato in [atual, *atual.parents]:
        if any((candidato / marcador).exists() for marcador in _MARCADORES):
            return candidato
    # Fallback: dois níveis acima de ppcgen/utilitarios/
    return Path(__file__).resolve().parents[2]
