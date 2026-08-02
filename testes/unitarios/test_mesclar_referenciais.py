"""Testes de ``cli._mesclar_referenciais`` (Seção 9 — herança de perfis via
``extends``): entradas de catálogo com o mesmo id/cargo no perfil atual
sobrescrevem as do perfil base; o restante do base é herdado.
"""

from __future__ import annotations

from ppcgen.cli import _mesclar_referenciais
from ppcgen.modelos import Autoridade, NucleoCurricular, ReferenciaisCurso


def test_autoridades_do_perfil_atual_sobrescrevem_por_cargo_e_herdam_o_resto():
    base = ReferenciaisCurso(
        autoridades=[
            Autoridade(cargo="Reitor", nome="Fulano de Tal"),
            Autoridade(cargo="Coordenador(a) do Curso", nome="[a confirmar]"),
        ]
    )
    atual = ReferenciaisCurso(
        autoridades=[Autoridade(cargo="Coordenador(a) do Curso", nome="Beltrana de Souza")]
    )

    mesclado = _mesclar_referenciais(base, atual)

    por_cargo = {a.cargo: a.nome for a in mesclado.autoridades}
    assert por_cargo == {
        "Reitor": "Fulano de Tal",
        "Coordenador(a) do Curso": "Beltrana de Souza",
    }


def test_comissao_membros_do_perfil_atual_substitui_a_do_base_inteira():
    base = ReferenciaisCurso(comissao_membros=["Prof. A -- presidente", "Prof. B"])
    atual = ReferenciaisCurso(comissao_membros=["Prof. C -- presidente"])

    mesclado = _mesclar_referenciais(base, atual)

    assert mesclado.comissao_membros == ["Prof. C -- presidente"]


def test_comissao_membros_do_perfil_atual_vazia_herda_do_base():
    base = ReferenciaisCurso(comissao_membros=["Prof. A -- presidente", "Prof. B"])
    atual = ReferenciaisCurso()

    mesclado = _mesclar_referenciais(base, atual)

    assert mesclado.comissao_membros == ["Prof. A -- presidente", "Prof. B"]


def test_mesclar_referenciais_continua_mesclando_nucleos_por_id():
    """Não regride o comportamento já existente para os demais catálogos."""

    base = ReferenciaisCurso(nucleos=[NucleoCurricular(id="BASICO", nome="Básico")])
    atual = ReferenciaisCurso(nucleos=[NucleoCurricular(id="TECNOLOGICO", nome="Tecnológico")])

    mesclado = _mesclar_referenciais(base, atual)

    assert {n.id for n in mesclado.nucleos} == {"BASICO", "TECNOLOGICO"}
