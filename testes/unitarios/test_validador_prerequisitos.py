from __future__ import annotations

from ppcgen.modelos import Correquisito, Curriculo, PreRequisito
from ppcgen.validadores.prerequisitos import (
    construir_grafo_prerequisitos,
    detectar_ciclos,
    validar_prerequisitos,
)
from testes.conftest import componente


def test_prerequisito_inexistente_gera_erro(config_basica):
    curriculo = Curriculo(
        versao="t", componentes=[componente("A1", periodo=2, pre_requisitos=[PreRequisito(codigo="ZZZ")])]
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "PREREQUISITO_INEXISTENTE" for m in resultado.erros)


def test_prerequisito_opcional_inexistente_vira_alerta(config_basica):
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("A1", periodo=2, pre_requisitos=[PreRequisito(codigo="ZZZ", opcional=True)])],
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "PREREQUISITO_INEXISTENTE" for m in resultado.alertas)
    assert not resultado.tem_erro


def test_autorreferencia_gera_erro(config_basica):
    curriculo = Curriculo(
        versao="t", componentes=[componente("A1", periodo=1, pre_requisitos=[PreRequisito(codigo="A1")])]
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "PREREQUISITO_AUTORREFERENCIA" for m in resultado.erros)


def test_prerequisito_em_periodo_posterior_gera_erro(config_basica):
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("A1", periodo=1, pre_requisitos=[PreRequisito(codigo="A2")]),
            componente("A2", periodo=2),
        ],
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "PREREQUISITO_PERIODO_INVALIDO" for m in resultado.erros)


def test_prerequisito_codigo_magico_rejeitado(config_basica):
    curriculo = Curriculo(
        versao="t", componentes=[componente("A1", periodo=2, pre_requisitos=[PreRequisito(codigo="*")])]
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "PREREQUISITO_CODIGO_MAGICO" for m in resultado.erros)


def test_carga_horaria_minima_nao_gera_erro(config_basica):
    preq = PreRequisito(codigo="", carga_horaria_minima=1000)
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("TCC", periodo=None, pre_requisitos=[preq])],
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert not resultado.tem_erro


def test_correquisito_periodo_divergente_gera_alerta(config_basica):
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("A1", periodo=1, correquisitos=[Correquisito(codigo="A2")]),
            componente("A2", periodo=2),
        ],
    )
    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "CORREQUISITO_PERIODO_DIVERGENTE" for m in resultado.alertas)


def test_deteccao_de_ciclo_simples():
    grafo = {"A": ["B"], "B": ["C"], "C": ["A"]}
    ciclos = detectar_ciclos(grafo)
    assert len(ciclos) == 1
    assert set(ciclos[0]) == {"A", "B", "C"}


def test_sem_ciclo_nao_detecta_nada():
    grafo = {"A": ["B"], "B": ["C"], "C": []}
    assert detectar_ciclos(grafo) == []


def test_validar_prerequisitos_reporta_ciclo(config_basica):
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("A1", periodo=1, pre_requisitos=[PreRequisito(codigo="A3")]),
            componente("A2", periodo=1, pre_requisitos=[PreRequisito(codigo="A1")]),
            componente("A3", periodo=1, pre_requisitos=[PreRequisito(codigo="A2")]),
        ],
    )
    # forçamos período igual em todos para isolar o teste de ciclo (senão o
    # PREREQUISITO_PERIODO_INVALIDO já dispararia primeiro)
    grafo = construir_grafo_prerequisitos(curriculo)
    ciclos = detectar_ciclos(grafo)
    assert len(ciclos) >= 1

    resultado = validar_prerequisitos(curriculo, config_basica)
    assert any(m.codigo_regra == "CICLO_PREREQUISITOS" for m in resultado.erros)
