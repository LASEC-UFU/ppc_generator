"""Leitura dos referenciais configuráveis (núcleos, áreas, competências,
conteúdos, legislação e temas transversais) a partir de arquivos YAML.

Nenhuma dessas listas é fixada no código: um curso diferente troca apenas os
arquivos em ``referenciais/`` (ou os aponta via ``arquivos.referenciais`` em
``perfil.yaml``) sem precisar alterar o Python.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ppcgen.excecoes import ArquivoNaoEncontrado, FormatoInvalido
from ppcgen.modelos import (
    AreaFormacao,
    Competencia,
    Conteudo,
    NucleoCurricular,
    ReferencialCurricular,
    TemaTransversal,
)


def _ler_yaml(caminho: Path) -> dict:
    if not caminho.exists():
        raise ArquivoNaoEncontrado(f"Arquivo de referenciais não encontrado: {caminho}")
    with open(caminho, encoding="utf-8") as f:
        conteudo = yaml.safe_load(f)
    if conteudo is None:
        return {}
    if not isinstance(conteudo, dict):
        raise FormatoInvalido(f"{caminho} deve conter um mapeamento YAML na raiz.")
    return conteudo


def carregar_nucleos(caminho: Path) -> list[NucleoCurricular]:
    dados = _ler_yaml(caminho)
    return [NucleoCurricular(**item) for item in dados.get("nucleos", [])]


def carregar_areas(caminho: Path) -> list[AreaFormacao]:
    dados = _ler_yaml(caminho)
    return [AreaFormacao(**item) for item in dados.get("areas", [])]


def carregar_competencias(caminho: Path) -> list[Competencia]:
    dados = _ler_yaml(caminho)
    return [Competencia(**item) for item in dados.get("competencias", [])]


def carregar_conteudos(caminho: Path) -> list[Conteudo]:
    dados = _ler_yaml(caminho)
    return [Conteudo(**item) for item in dados.get("conteudos", [])]


def carregar_referenciais_legais(caminho: Path) -> list[ReferencialCurricular]:
    dados = _ler_yaml(caminho)
    return [ReferencialCurricular(**item) for item in dados.get("referenciais", [])]


def carregar_temas_transversais(caminho: Path) -> list[TemaTransversal]:
    dados = _ler_yaml(caminho)
    return [TemaTransversal(**item) for item in dados.get("temas", [])]


@dataclass
class ReferenciaisCurso:
    """Conjunto completo de referenciais configurados para o curso ativo."""

    nucleos: list[NucleoCurricular] = field(default_factory=list)
    areas: list[AreaFormacao] = field(default_factory=list)
    competencias: list[Competencia] = field(default_factory=list)
    conteudos: list[Conteudo] = field(default_factory=list)
    legislacao: list[ReferencialCurricular] = field(default_factory=list)
    temas_transversais: list[TemaTransversal] = field(default_factory=list)

    def ids_nucleos(self) -> set[str]:
        return {n.id for n in self.nucleos}

    def ids_areas(self) -> set[str]:
        return {a.id for a in self.areas}

    def ids_competencias(self) -> set[str]:
        return {c.id for c in self.competencias}

    def ids_conteudos(self) -> set[str]:
        return {c.id for c in self.conteudos}

    def ids_temas(self) -> set[str]:
        return {t.id for t in self.temas_transversais}


def carregar_referenciais_curso(pasta_referenciais: Path) -> ReferenciaisCurso:
    """Carrega todos os referenciais de uma pasta ``referenciais/``.

    Arquivos ausentes resultam em listas vazias (um curso pode, por exemplo,
    ainda não ter ``competencias.yaml`` definido) — apenas os arquivos
    referenciados pelos validadores como obrigatórios geram erro.
    """

    def _se_existir(nome_arquivo: str, carregador):
        caminho = pasta_referenciais / nome_arquivo
        if not caminho.exists():
            return []
        return carregador(caminho)

    return ReferenciaisCurso(
        nucleos=_se_existir("nucleos.yaml", carregar_nucleos),
        areas=_se_existir("areas_formacao.yaml", carregar_areas),
        competencias=_se_existir("competencias.yaml", carregar_competencias),
        conteudos=_se_existir("conteudos.yaml", carregar_conteudos),
        legislacao=_se_existir("legislacao.yaml", carregar_referenciais_legais),
        temas_transversais=_se_existir(
            "temas_transversais.yaml", carregar_temas_transversais
        ),
    )
