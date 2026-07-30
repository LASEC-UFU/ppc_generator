from __future__ import annotations

from ppcgen.geradores.comparacao import comparar_curriculos
from ppcgen.modelos import Curriculo
from testes.conftest import componente


def test_componentes_incluidos_e_removidos():
    anterior = Curriculo(versao="2025-1", componentes=[componente("A1"), componente("A2")])
    atual = Curriculo(versao="2026-1", componentes=[componente("A1"), componente("A3")])

    relatorio = comparar_curriculos(anterior, atual)
    assert relatorio.incluidos == ["A3"]
    assert relatorio.removidos == ["A2"]


def test_componente_alterado_detecta_mudanca_de_carga():
    anterior = Curriculo(versao="2025-1", componentes=[componente("A1", cht=30, tot=30)])
    atual = Curriculo(versao="2026-1", componentes=[componente("A1", cht=60, tot=60)])

    relatorio = comparar_curriculos(anterior, atual)
    campos_alterados = {d.campo for d in relatorio.alterados}
    assert "carga_total" in campos_alterados


def test_mudanca_de_obrigatorio_para_optativo_e_detectada():
    anterior = Curriculo(versao="2025-1", componentes=[componente("A1", obrigatorio=True)])
    atual = Curriculo(versao="2026-1", componentes=[componente("A1", obrigatorio=False)])

    relatorio = comparar_curriculos(anterior, atual)
    assert any(d.campo == "obrigatorio" for d in relatorio.alterados)


def test_impacto_sobre_competencias():
    anterior = Curriculo(versao="2025-1", componentes=[componente("A1", competencias=["C1", "C2"])])
    atual = Curriculo(versao="2026-1", componentes=[componente("A1", competencias=["C2", "C3"])])

    relatorio = comparar_curriculos(anterior, atual)
    assert relatorio.competencias_perdidas == ["C1"]
    assert relatorio.competencias_ganhas == ["C3"]


def test_carga_total_sem_alteracao_nao_gera_diferenca_espuria():
    anterior = Curriculo(versao="2025-1", componentes=[componente("A1", cht=30, tot=30)])
    atual = Curriculo(versao="2026-1", componentes=[componente("A1", cht=30, tot=30)])

    relatorio = comparar_curriculos(anterior, atual)
    assert relatorio.alterados == []
    assert relatorio.incluidos == []
    assert relatorio.removidos == []
