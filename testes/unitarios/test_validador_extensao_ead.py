from __future__ import annotations

from ppcgen.config import CurriculoConfig, CursoConfig
from ppcgen.modelos import Curriculo, TipoComponente
from ppcgen.validadores.ead import validar_ead
from ppcgen.validadores.extensao import validar_extensao
from testes.conftest import componente, construir_perfil


def _perfil(**kwargs):
    return construir_perfil(curso=CursoConfig(numero_periodos=1), curriculo=CurriculoConfig(**kwargs))


def test_percentual_extensao_abaixo_do_minimo_gera_erro():
    perfil = _perfil(percentual_minimo_extensao=50)
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("A1", cht=100, tot=100),
            componente("EXT1", tipo=TipoComponente.EXTENSAO, cht=0, che=10, tot=10),
        ],
    )
    resultado = validar_extensao(curriculo, perfil)
    assert any(m.codigo_regra == "EXTENSAO_ABAIXO_DO_MINIMO" for m in resultado.erros)


def test_percentual_extensao_suficiente_nao_gera_erro():
    perfil = _perfil(percentual_minimo_extensao=10)
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("A1", cht=90, tot=90),
            componente("EXT1", tipo=TipoComponente.EXTENSAO, cht=0, che=10, tot=10),
        ],
    )
    resultado = validar_extensao(curriculo, perfil)
    assert not resultado.tem_erro


def test_percentual_maximo_ead_excedido_gera_erro():
    perfil = _perfil(percentual_maximo_ead=10)
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("A1", cht=0, chd=50, tot=50), componente("A2", cht=50, tot=50)],
    )
    resultado = validar_ead(curriculo, perfil)
    assert any(m.codigo_regra == "EAD_ACIMA_DO_MAXIMO" for m in resultado.erros)


def test_sem_limite_configurado_nao_valida():
    perfil = _perfil()
    curriculo = Curriculo(versao="t", componentes=[componente("A1", chd=1000, tot=1000)])
    assert not validar_ead(curriculo, perfil).mensagens
    assert not validar_extensao(curriculo, perfil).mensagens
