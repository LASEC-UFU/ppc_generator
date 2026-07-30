from __future__ import annotations

from ppcgen.config import CurriculoConfig, CursoConfig, OfertaConfig
from ppcgen.modelos import Curriculo, TipoComponente
from ppcgen.validadores.ead import validar_ead, validar_formato_oferta
from ppcgen.validadores.extensao import validar_extensao
from testes.conftest import componente, construir_perfil


def _perfil(oferta=None, **kwargs):
    return construir_perfil(
        curso=CursoConfig(numero_periodos=1),
        curriculo=CurriculoConfig(**kwargs),
        oferta=oferta or OfertaConfig(),
    )


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


def test_formato_oferta_desconhecido_gera_erro():
    perfil = _perfil(oferta=OfertaConfig(formato="hibrido"))
    resultado = validar_formato_oferta(perfil)
    assert any(m.codigo_regra == "OFERTA_FORMATO_DESCONHECIDO" for m in resultado.erros)


def test_percentual_maximo_ead_acima_do_teto_presencial_gera_erro():
    # Decreto nº 12.456/2025: presencial admite no máximo 30% de EaD.
    perfil = _perfil(percentual_maximo_ead=40, oferta=OfertaConfig(formato="presencial"))
    resultado = validar_formato_oferta(perfil)
    assert any(m.codigo_regra == "EAD_ACIMA_DO_TETO_LEGAL_FORMATO" for m in resultado.erros)


def test_percentual_maximo_ead_no_teto_presencial_nao_gera_erro():
    perfil = _perfil(percentual_maximo_ead=30, oferta=OfertaConfig(formato="presencial"))
    resultado = validar_formato_oferta(perfil)
    assert not resultado.tem_erro


def test_percentual_maximo_ead_valido_para_semipresencial_mas_nao_presencial():
    # 50% excede o teto do presencial (30%) mas está dentro do teto do
    # semipresencial (70%) — o formato declarado é que decide, não um
    # percentual "genérico".
    perfil_presencial = _perfil(percentual_maximo_ead=50, oferta=OfertaConfig(formato="presencial"))
    assert validar_formato_oferta(perfil_presencial).tem_erro

    perfil_semipresencial = _perfil(
        percentual_maximo_ead=50, oferta=OfertaConfig(formato="semipresencial")
    )
    assert not validar_formato_oferta(perfil_semipresencial).tem_erro


def test_oferta_com_ead_e_norma_institucional_pendente_gera_alerta():
    perfil = _perfil(
        oferta=OfertaConfig(formato="presencial", possui_carga_ead=True, status_validacao_institucional="pendente")
    )
    resultado = validar_formato_oferta(perfil)
    assert any(
        m.codigo_regra == "OFERTA_SEM_NORMA_INSTITUCIONAL_CONFIRMADA" for m in resultado.alertas
    )


def test_oferta_com_norma_institucional_confirmada_nao_gera_alerta():
    perfil = _perfil(
        oferta=OfertaConfig(
            formato="presencial",
            possui_carga_ead=True,
            norma_institucional="Resolução CONGRAD nº XXX/2026",
            status_validacao_institucional="confirmado",
        )
    )
    resultado = validar_formato_oferta(perfil)
    assert not any(
        m.codigo_regra == "OFERTA_SEM_NORMA_INSTITUCIONAL_CONFIRMADA" for m in resultado.alertas
    )
