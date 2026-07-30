from __future__ import annotations

from ppcgen.modelos import Curriculo, FichaCurricular, StatusFicha
from ppcgen.validadores.fichas import avaliar_fichas
from testes.conftest import componente


def test_ficha_ausente():
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    _resultado, situacao = avaliar_fichas(curriculo, [])
    assert situacao.status_por_componente["A1"] == StatusFicha.AUSENTE


def test_ficha_consistente():
    curriculo = Curriculo(versao="t", componentes=[componente("A1", nome="Disciplina A1", tot=30)])
    ficha = FichaCurricular(
        codigo="A1",
        nome="Disciplina A1",
        ementa="x",
        objetivos="x",
        programa="x",
        metodologia="x",
        avaliacao="x",
        bibliografia_basica="x",
        bibliografia_complementar="x",
    )
    from ppcgen.modelos import CargaHoraria

    ficha.carga_horaria = CargaHoraria(total=30)
    _resultado, situacao = avaliar_fichas(curriculo, [ficha])
    assert situacao.status_por_componente["A1"] == StatusFicha.LOCALIZADA_CONSISTENTE


def test_ficha_com_carga_divergente():
    curriculo = Curriculo(versao="t", componentes=[componente("A1", tot=30)])
    from ppcgen.modelos import CargaHoraria

    ficha = FichaCurricular(codigo="A1", nome="A1", carga_horaria=CargaHoraria(total=999))
    resultado, situacao = avaliar_fichas(curriculo, [ficha])
    assert situacao.status_por_componente["A1"] == StatusFicha.LOCALIZADA_DIVERGENTE
    assert any(m.codigo_regra == "FICHA_CARGA_DIVERGENTE" for m in resultado.erros)


def test_ficha_duplicada():
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    fichas = [FichaCurricular(codigo="A1"), FichaCurricular(codigo="A1")]
    _resultado, situacao = avaliar_fichas(curriculo, fichas)
    assert situacao.status_por_componente["A1"] == StatusFicha.DUPLICADA


def test_ficha_nao_reconhecida_por_baixa_confianca():
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    fichas = [FichaCurricular(codigo="A1", confianca_extracao=0.0)]
    _resultado, situacao = avaliar_fichas(curriculo, fichas)
    assert situacao.status_por_componente["A1"] == StatusFicha.NAO_RECONHECIDA


def test_ficha_orfa_reportada():
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    fichas = [FichaCurricular(codigo="A1"), FichaCurricular(codigo="ZZZ")]
    _resultado, situacao = avaliar_fichas(curriculo, fichas)
    assert "ZZZ" in situacao.fichas_orfas
