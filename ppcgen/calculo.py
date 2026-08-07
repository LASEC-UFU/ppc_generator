"""Cálculos curriculares compartilhados entre validadores e geradores.

Centralizado aqui para não duplicar a mesma fórmula em módulos diferentes
(Seção 29 — "não duplique lógica").

A carga horária "oficial" do curso — usada para conferir contra a aba
``Perfil`` da matriz e como denominador dos percentuais de EaD/extensão —
**não** é a soma bruta de todos os componentes ativos: isso incluiria o pool
inteiro de disciplinas optativas pré-aprovadas, das quais o estudante cursa
apenas um subconjunto. A carga oficial é:

    soma(componentes ativos com tipo != carga_optativa) + carga_optativa_minima

O filtro é por **tipo** (``carga_optativa``) — não existe mais um campo
``obrigatorio`` independente na fonte de dados:
``ComponenteCurricular.obrigatorio`` (``ppcgen/modelos.py``) é uma
propriedade derivada, sempre igual a ``tipo != carga_optativa``, então não
há como um componente divergir dos dois critérios (isso já foi um bug real
deste projeto — ver ``docs/MIGRAR_PERFIL.md`` — quando um campo
``obrigatorio`` próprio, mantido à parte do ``tipo``, podia ficar
inconsistente com ele).

``carga_optativa_minima`` não é um parâmetro cadastrado na aba ``Perfil``
(isso já foi um bug real deste projeto: mantida em dois lugares — a aba
``Perfil`` e o componente agregador "MÓDULO OPTATIVO" da aba
``Componentes`` —, os dois valores divergiam sempre que só um dos dois era
atualizado). A fonte única é o próprio componente agregador: ver
:func:`carga_optativa_minima`.

``Curriculo.carga_horaria_total()`` (em :mod:`ppcgen.modelos`) continua
disponível para quando a soma bruta de tudo o que está *ativo* é realmente o
que se quer (ex.: conferir se o pool de optativas oferece horas
suficientes) — mas não deve ser usada como "o" total do curso.
"""

from __future__ import annotations

import unicodedata

from ppcgen.modelos import ComponenteCurricular, Curriculo, TipoComponente

_NOMES_AGREGADOR_OPTATIVO = {"modulo optativo", "carga optativa", "pool optativo", "bloco optativo"}


def eh_agregador_optativo(nome: str) -> bool:
    """Identifica a linha-resumo (ex.: "MÓDULO OPTATIVO") que representa a
    carga horária optativa mínima do curso — não é uma disciplina cursável.
    O que a distingue de uma disciplina real é o **nome** (reconhecido
    aqui), não o campo ``ativo`` nem o ``tipo``: ela pode estar cadastrada
    como ``ativo=True`` (é uma decisão de cada perfil) sem que isso afete
    nenhum cálculo — :func:`componentes_oficiais` e a soma do pool real de
    optativas (``ppcgen.validadores.cargas``) sempre a excluem por nome,
    para que sua carga só entre uma vez, via :func:`carga_optativa_minima`."""

    normalizado = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", nome.casefold())
        if not unicodedata.combining(caractere)
    )
    normalizado = " ".join(normalizado.split())
    return normalizado in _NOMES_AGREGADOR_OPTATIVO


def carga_optativa_minima(curriculo: Curriculo) -> int | None:
    """Carga horária optativa mínima do curso, lida diretamente da
    ``carga_total`` do componente agregador ("MÓDULO OPTATIVO" ou
    equivalente) cadastrado na aba ``Componentes`` — única fonte deste
    valor (não há campo correspondente na aba ``Perfil``). Busca em todos
    os componentes, ativos ou não — o agregador pode estar ``ativo=True``
    ou ``False`` livremente, o que importa é o nome (ver
    :func:`eh_agregador_optativo`). ``None`` quando nenhum componente
    agregador está cadastrado."""

    for c in curriculo.componentes:
        if eh_agregador_optativo(c.nome):
            return c.carga_total
    return None


def carga_por_tipo(curriculo: Curriculo, tipo: TipoComponente) -> int:
    return sum(c.carga_total for c in curriculo.ativos() if c.tipo == tipo)


def componentes_oficiais(curriculo: Curriculo) -> list[ComponenteCurricular]:
    """Componentes ativos que contam integralmente no total do curso — todo
    tipo exceto ``carga_optativa`` (cujo pool só entra pelo mínimo exigido,
    ver :func:`carga_horaria_oficial`).

    Exclui também o componente agregador ("MÓDULO OPTATIVO") por nome,
    esteja ele ``ativo=True`` ou ``False`` e qualquer que seja seu
    ``tipo``: sem essa exclusão por nome, um agregador ativo (estado
    plenamente válido — o campo ``ativo`` não o distingue de uma
    disciplina real, o nome distingue) seria contado aqui E de novo via
    :func:`carga_optativa_minima`, inflando a carga horária oficial em
    exatamente a carga do agregador (bug real já visto neste projeto)."""

    return [
        c
        for c in curriculo.ativos()
        if c.tipo != TipoComponente.CARGA_OPTATIVA and not eh_agregador_optativo(c.nome)
    ]


def carga_horaria_oficial(curriculo: Curriculo) -> int:
    soma_nao_optativa = sum(c.carga_total for c in componentes_oficiais(curriculo))
    optativa_minima = carga_optativa_minima(curriculo) or 0
    return soma_nao_optativa + optativa_minima
