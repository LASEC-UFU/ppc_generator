from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, carga_por_tipo
from ppcgen.config import CurriculoConfig, CursoConfig
from ppcgen.modelos import Curriculo, TipoComponente
from testes.conftest import componente, construir_perfil


def test_carga_horaria_oficial_exclui_pool_de_optativas_nao_escolhidas():
    perfil = construir_perfil(
        curso=CursoConfig(numero_periodos=1), curriculo=CurriculoConfig(carga_optativa_minima=60)
    )
    componentes = [
        componente("A1", cht=100, tot=100),  # obrigatória
        componente("OPT1", tipo=TipoComponente.CARGA_OPTATIVA, obrigatorio=False, periodo=None, cht=60, tot=60),
        componente("OPT2", tipo=TipoComponente.CARGA_OPTATIVA, obrigatorio=False, periodo=None, cht=60, tot=60),
        componente("OPT3", tipo=TipoComponente.CARGA_OPTATIVA, obrigatorio=False, periodo=None, cht=60, tot=60),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)

    # soma bruta do currículo (todo o pool) é bem maior que o total oficial
    assert curriculo.carga_horaria_total() == 100 + 60 * 3
    assert carga_horaria_oficial(curriculo, perfil) == 100 + 60  # só o mínimo exigido


def test_carga_por_tipo_soma_apenas_ativos():
    componentes = [
        componente("EXT1", tipo=TipoComponente.EXTENSAO, cht=0, che=30, tot=30),
        componente("EXT2", tipo=TipoComponente.EXTENSAO, cht=0, che=30, tot=30, ativo=False),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)
    assert carga_por_tipo(curriculo, TipoComponente.EXTENSAO) == 30
