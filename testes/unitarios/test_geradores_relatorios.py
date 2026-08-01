from __future__ import annotations

from ppcgen.geradores.comparacao import (
    comparar_curriculos,
    gerar_relatorio_comparacao_html,
)
from ppcgen.geradores.relatorios import gerar_relatorio_html
from ppcgen.modelos import Curriculo, ErroValidacao, ResultadoValidacao
from testes.conftest import componente


def test_relatorio_validacao_escapa_dados_da_planilha(tmp_path):
    resultado = ResultadoValidacao()
    resultado.adicionar(ErroValidacao("REGRA<1", "mensagem <script>", componente="A&1"))
    destino = tmp_path / "validacao.html"

    gerar_relatorio_html(resultado, destino)

    html = destino.read_text(encoding="utf-8")
    assert "mensagem &lt;script&gt;" in html
    assert "A&amp;1" in html
    assert "REGRA&lt;1" in html


def test_relatorio_comparacao_escapa_dados_da_matriz(tmp_path):
    anterior = componente("A<1", nome="Anterior")
    atual = componente("A<1", nome="Atual & melhor")
    relatorio = comparar_curriculos(
        Curriculo("<anterior>", [anterior]),
        Curriculo("<atual>", [atual]),
    )
    destino = tmp_path / "comparacao.html"

    gerar_relatorio_comparacao_html(relatorio, destino)

    html = destino.read_text(encoding="utf-8")
    assert "&lt;anterior&gt;" in html
    assert "Atual &amp; melhor" in html
