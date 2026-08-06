from __future__ import annotations

from ppcgen.geradores.fluxo import gerar_tabela_fluxo, montar_grupos_fluxo
from ppcgen.geradores.representacao_grafica import gerar_representacao_grafica
from ppcgen.geradores.tabelas import formatar_lista_requisitos, formatar_requisito, tabela_componentes
from ppcgen.modelos import Correquisito, Curriculo, PreRequisito, TipoComponente
from testes.conftest import componente


def test_tabela_componentes_escapa_nome_com_caracteres_especiais():
    disc = componente("A1", nome="Circuitos R&C / 50% de Aproveitamento", cht=30, tot=30)
    tex = tabela_componentes([disc], "Título", "label_teste")
    assert r"R\&C" in tex
    assert r"50\% de Aproveitamento" in tex
    assert "\\begin{longtblr}" in tex and "\\end{longtblr}" in tex


def test_tabela_componentes_total_soma_cargas():
    d1 = componente("A1", cht=30, chp=0, tot=30)
    d2 = componente("A2", cht=45, chp=0, tot=45)
    tex = tabela_componentes([d1, d2], "T", "l")
    assert r"\textbf{75}" in tex


def test_formatar_requisito_com_codigo():
    nomes = {"A1": "Cálculo I"}
    texto = formatar_requisito(PreRequisito(codigo="A1"), nomes)
    assert texto == "Cálculo I"


def test_formatar_requisito_com_carga_horaria_minima():
    texto = formatar_requisito(PreRequisito(codigo="", carga_horaria_minima=1200), {})
    assert "1200 horas" in texto


def test_formatar_lista_requisitos_vazia_retorna_livre():
    assert formatar_lista_requisitos([], {}) == "Livre"


def test_montar_grupos_fluxo_agrupa_por_periodo_e_tipo():
    componentes = [
        componente("A1", periodo=1),
        componente("A2", periodo=2),
        componente("OPT1", periodo=None, tipo=TipoComponente.CARGA_OPTATIVA),
        componente("TCC1", periodo=None, tipo=TipoComponente.TCC),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)
    grupos = montar_grupos_fluxo(curriculo, numero_periodos=3)
    assert grupos["1"][0].codigo == "A1"
    assert grupos["2"][0].codigo == "A2"
    assert grupos["Optativas"][0].codigo == "OPT1"
    assert grupos["Conclusão de Curso"][0].codigo == "TCC1"
    assert "3" not in grupos  # período sem componentes não aparece


def test_gerar_tabela_fluxo_nao_quebra_com_correquisito(config_basica):
    componentes = [
        componente("A1", periodo=1, correquisitos=[Correquisito(codigo="A2")]),
        componente("A2", periodo=1),
    ]
    curriculo = Curriculo(versao="t", componentes=componentes)
    nomes = {c.codigo: c.nome for c in componentes}
    tex = gerar_tabela_fluxo(curriculo, config_basica, nomes)
    assert "tab:fluxo_curricular" in tex


def test_representacao_grafica_alta_limita_altura_sem_float(config_basica):
    componentes = [
        componente(
            f"OPT{i}",
            periodo=None,
            tipo=TipoComponente.CARGA_OPTATIVA,
        )
        for i in range(11)
    ]
    tex = gerar_representacao_grafica(
        Curriculo(versao="t", componentes=componentes),
        config_basica,
    )
    assert r"\resizebox{\linewidth}{0.78\textheight}" in tex
    assert r"\begin{center}" in tex
    assert r"\begin{table}" not in tex
