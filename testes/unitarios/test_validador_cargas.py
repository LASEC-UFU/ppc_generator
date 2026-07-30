from __future__ import annotations

from ppcgen.config import CurriculoConfig, CursoConfig
from ppcgen.modelos import Curriculo, TipoComponente
from ppcgen.validadores.cargas import validar_cargas
from testes.conftest import componente, construir_perfil


def test_carga_negativa_gera_erro(config_basica):
    disc = componente("A1", cht=-10)
    curriculo = Curriculo(versao="t", componentes=[disc])
    resultado = validar_cargas(curriculo, config_basica)
    assert any(m.codigo_regra == "CARGA_NEGATIVA" for m in resultado.erros)


def test_carga_total_inconsistente(config_basica):
    disc = componente("A1", cht=30, chp=30, tot=100)
    curriculo = Curriculo(versao="t", componentes=[disc])
    resultado = validar_cargas(curriculo, config_basica)
    assert any(m.codigo_regra == "CARGA_TOTAL_INCONSISTENTE" for m in resultado.erros)


def test_carga_sem_modalidade_nao_gera_falso_positivo(config_basica):
    # AAC-like: todas as parcelas None -> soma_parcelas() é None -> não compara com total
    disc = componente(
        "AAC1", cht=None, chp=None, chd=None, che=None, tot=60, tipo=TipoComponente.ATIVIDADE_COMPLEMENTAR
    )
    curriculo = Curriculo(versao="t", componentes=[disc])
    resultado = validar_cargas(curriculo, config_basica)
    assert not resultado.tem_erro


def test_carga_total_curso_divergente():
    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(carga_horaria_total=1000),
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1", cht=30, tot=30)])
    resultado = validar_cargas(curriculo, perfil)
    assert any(m.codigo_regra == "CARGA_TOTAL_CURSO_DIVERGENTE" for m in resultado.erros)


def test_pool_optativas_insuficiente():
    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(carga_optativa_minima=200),
    )
    optativa = componente(
        "OPT1", tipo=TipoComponente.CARGA_OPTATIVA, obrigatorio=False, periodo=None, cht=60, tot=60
    )
    curriculo = Curriculo(versao="t", componentes=[optativa])
    resultado = validar_cargas(curriculo, perfil)
    assert any(m.codigo_regra == "POOL_OPTATIVAS_INSUFICIENTE" for m in resultado.erros)


def test_carga_maxima_por_periodo_excedida():
    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(carga_horaria_maxima_periodo=50),
    )
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("A1", periodo=1, cht=30, tot=30), componente("A2", periodo=1, cht=30, tot=30)],
    )
    resultado = validar_cargas(curriculo, perfil)
    assert any(m.codigo_regra == "CARGA_MAXIMA_PERIODO_EXCEDIDA" for m in resultado.erros)
