from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, carga_optativa_minima, carga_por_tipo
from ppcgen.modelos import Curriculo, TipoComponente
from testes.conftest import componente


def test_carga_horaria_oficial_exclui_pool_de_optativas_nao_escolhidas():
    componentes = [
        componente("A1", cht=100, tot=100),  # obrigatória
        # "MÓDULO OPTATIVO" é o componente agregador que carrega a carga
        # horária optativa mínima do curso — nunca uma disciplina cursável,
        # mas isso é reconhecido pelo NOME (ver
        # ppcgen.calculo.eh_agregador_optativo), não pelo campo `ativo`: ele
        # pode estar ativo=True ou False livremente, sem afetar o cálculo.
        componente("OPT", nome="MÓDULO OPTATIVO", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60, ativo=False),
        componente("OPT1", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60),
        componente("OPT2", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60),
        componente("OPT3", tipo=TipoComponente.CARGA_OPTATIVA, periodo=None, cht=60, tot=60),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)

    assert carga_optativa_minima(curriculo) == 60
    # soma bruta do currículo (todo o pool, incluindo o agregador inativo)
    # é bem maior que o total oficial
    assert curriculo.carga_horaria_total() == 100 + 60 * 3
    assert carga_horaria_oficial(curriculo) == 100 + 60  # só o mínimo exigido


def test_carga_horaria_oficial_nao_duplica_agregador_ativo_ou_com_outro_tipo():
    """Regressão: o componente agregador pode estar ``ativo=True`` e com
    qualquer ``tipo`` — nenhum dos dois campos o torna uma disciplina real,
    só o nome (ver ``ppcgen.calculo.eh_agregador_optativo``). Mesmo assim,
    ele não pode ser contado tanto em ``componentes_oficiais`` (por ter
    ``tipo != carga_optativa``) quanto de novo via
    ``carga_optativa_minima`` — ``componentes_oficiais`` precisa excluí-lo
    por nome, não só por tipo/ativo."""

    componentes = [
        componente("A1", cht=100, tot=100),
        componente(
            "OPT",
            nome="MÓDULO OPTATIVO",
            tipo=TipoComponente.DISCIPLINA,
            periodo=None,
            cht=45,
            tot=45,
            ativo=True,
        ),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)

    assert carga_optativa_minima(curriculo) == 45
    # 100 (A1) + 45 (mínimo optativo, contado uma única vez) — nunca 190
    assert carga_horaria_oficial(curriculo) == 145


def test_carga_por_tipo_soma_apenas_ativos():
    componentes = [
        componente("EXT1", tipo=TipoComponente.EXTENSAO, cht=0, che=30, tot=30),
        componente("EXT2", tipo=TipoComponente.EXTENSAO, cht=0, che=30, tot=30, ativo=False),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)
    assert carga_por_tipo(curriculo, TipoComponente.EXTENSAO) == 30
