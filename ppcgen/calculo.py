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

``Curriculo.carga_horaria_total()`` (em :mod:`ppcgen.modelos`) continua
disponível para quando a soma bruta de tudo o que está *ativo* é realmente o
que se quer (ex.: conferir se o pool de optativas oferece horas
suficientes) — mas não deve ser usada como "o" total do curso.
"""

from __future__ import annotations

from ppcgen.config import Perfil
from ppcgen.modelos import ComponenteCurricular, Curriculo, TipoComponente


def carga_por_tipo(curriculo: Curriculo, tipo: TipoComponente) -> int:
    return sum(c.carga_total for c in curriculo.ativos() if c.tipo == tipo)


def componentes_oficiais(curriculo: Curriculo) -> list[ComponenteCurricular]:
    """Componentes ativos que contam integralmente no total do curso — todo
    tipo exceto ``carga_optativa`` (cujo pool só entra pelo mínimo exigido,
    ver :func:`carga_horaria_oficial`)."""

    return [c for c in curriculo.ativos() if c.tipo != TipoComponente.CARGA_OPTATIVA]


def carga_horaria_oficial(curriculo: Curriculo, perfil: Perfil) -> int:
    soma_nao_optativa = sum(c.carga_total for c in componentes_oficiais(curriculo))
    optativa_minima = perfil.curriculo.carga_optativa_minima or 0
    return soma_nao_optativa + optativa_minima
