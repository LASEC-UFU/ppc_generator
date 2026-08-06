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
    # A carga horária optativa mínima não é mais um parâmetro da aba Perfil
    # — vem do próprio componente agregador "MÓDULO OPTATIVO" (inativo),
    # única fonte desse valor (ppcgen.calculo.carga_optativa_minima).
    perfil = construir_perfil(curso=CursoConfig(numero_periodos=1))
    agregador = componente(
        "OPT", nome="MÓDULO OPTATIVO", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=200, tot=200, ativo=False
    )
    optativa = componente("OPT1", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60)
    curriculo = Curriculo(versao="t", componentes=[agregador, optativa])
    resultado = validar_cargas(curriculo, perfil)
    assert any(m.codigo_regra == "POOL_OPTATIVAS_INSUFICIENTE" for m in resultado.erros)


def test_agregador_ativo_gera_erro_e_nao_mascara_pool_optativas_insuficiente():
    """Cenário de dado malformado: o agregador foi deixado ``ativo=True``
    (deveria estar sempre inativo). Mesmo assim, ele não deve ser contado
    como um componente real do pool (o que mascararia o déficit real de
    horas optativas) — e sua própria presença ativa já é reportada como
    erro à parte."""

    perfil = construir_perfil(curso=CursoConfig(numero_periodos=1))
    agregador = componente(
        "OPT",
        nome="MÓDULO OPTATIVO",
        tipo=TipoComponente.CARGA_OPTATIVA,
        periodo=None,
        cht=120,
        tot=120,
    )
    optativa_real = componente(
        "OPT1", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60
    )
    resultado = validar_cargas(Curriculo(versao="t", componentes=[agregador, optativa_real]), perfil)

    codigos = {m.codigo_regra for m in resultado.erros}
    assert "COMPONENTE_AGREGADOR_OPTATIVO" in codigos
    assert "POOL_OPTATIVAS_INSUFICIENTE" in codigos


def test_carga_maxima_por_periodo_excedida():
    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(carga_horaria_presencial_maxima_periodo=50),
    )
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("A1", periodo=1, cht=30, tot=30), componente("A2", periodo=1, cht=30, tot=30)],
    )
    resultado = validar_cargas(curriculo, perfil)
    assert any(m.codigo_regra == "CARGA_MAXIMA_PERIODO_EXCEDIDA" for m in resultado.erros)


def test_carga_maxima_por_periodo_considera_so_presencial():
    """CHD (a distância) e CHE (extensão) não contam pro limite — só
    CHT+CHP (presencial). Um período com CHT+CHP dentro do limite não deve
    disparar o erro mesmo que CHD/CHE empurrem o total muito acima dele."""

    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(carga_horaria_presencial_maxima_periodo=50),
    )
    disc = componente("A1", periodo=1, cht=30, chp=10, chd=100, che=100, tot=240)
    curriculo = Curriculo(versao="t", componentes=[disc])
    resultado = validar_cargas(curriculo, perfil)
    assert not any(m.codigo_regra == "CARGA_MAXIMA_PERIODO_EXCEDIDA" for m in resultado.erros)
