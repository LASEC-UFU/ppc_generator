"""Teste de integração ponta a ponta (Seção 20): carrega o perfil mínimo de
testes (``testes/perfis_exemplo/perfil_minimo``, isolado dos dados reais de
produção — Seção 21), valida, gera os arquivos LaTeX, monta a árvore de
compilação e tenta compilar de verdade (se o TeX estiver disponível no
ambiente), conferindo os artefatos esperados.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from ppcgen.compiladores.latex import compilar_pdf, montar_arvore_latex
from ppcgen.config import carregar_perfil
from ppcgen.geradores.latex import gerar_arquivos_latex
from ppcgen.leitores.excel import carregar_matriz
from ppcgen.leitores.yaml import carregar_referenciais_curso
from ppcgen.validadores.curriculo import validar_curriculo
from ppcgen.validadores.perfil import validar_perfil

RAIZ_FIXTURES = Path(__file__).resolve().parent.parent / "perfis_exemplo"


@pytest.fixture
def perfil_minimo():
    return carregar_perfil(RAIZ_FIXTURES / "perfil_minimo")


def test_perfil_minimo_passa_na_validacao_estrutural(perfil_minimo):
    resultado = validar_perfil(perfil_minimo)
    assert not resultado.tem_erro, [m.mensagem for m in resultado.erros]


def test_perfil_minimo_valida_sem_erros(perfil_minimo):
    curriculo, _metadados, avisos = carregar_matriz(
        perfil_minimo.resolver_arquivo(perfil_minimo.arquivos.matriz)
    )
    referenciais = carregar_referenciais_curso(perfil_minimo.diretorio / perfil_minimo.arquivos.referenciais)

    resultado, _situacao = validar_curriculo(curriculo, perfil_minimo, referenciais, avisos_leitura=avisos)
    assert not resultado.tem_erro, [m.mensagem for m in resultado.erros]


def test_pipeline_gera_arquivos_latex_esperados(tmp_path, perfil_minimo):
    curriculo, _metadados, _avisos = carregar_matriz(
        perfil_minimo.resolver_arquivo(perfil_minimo.arquivos.matriz)
    )
    referenciais = carregar_referenciais_curso(perfil_minimo.diretorio / perfil_minimo.arquivos.referenciais)
    pasta_gerado = tmp_path / "gerado"

    gerados = gerar_arquivos_latex(curriculo, perfil_minimo, referenciais, pasta_gerado)

    nomes = {p.name for p in gerados}
    assert "tab_fluxo_curricular.tex" in nomes
    assert "curso_macros.tex" in nomes
    assert "frontmatter.tex" in nomes

    conteudo_fluxo = (pasta_gerado / "tab_fluxo_curricular.tex").read_text(encoding="utf-8")
    assert "NAO EDITE MANUALMENTE" in conteudo_fluxo
    assert "Fundamentos de Teste" in conteudo_fluxo
    assert conteudo_fluxo.count(r"\begin{longtblr}") == conteudo_fluxo.count(r"\end{longtblr}")


@pytest.mark.skipif(shutil.which("latexmk") is None, reason="TeX não disponível neste ambiente")
def test_pipeline_compila_pdf_do_perfil_minimo(tmp_path, perfil_minimo):
    curriculo, _metadados, _avisos = carregar_matriz(
        perfil_minimo.resolver_arquivo(perfil_minimo.arquivos.matriz)
    )
    referenciais = carregar_referenciais_curso(perfil_minimo.diretorio / perfil_minimo.arquivos.referenciais)

    pasta_latex = tmp_path / "latex"
    gerar_arquivos_latex(curriculo, perfil_minimo, referenciais, pasta_latex / "gerado")
    caminho_tex = montar_arvore_latex(perfil_minimo, pasta_latex)

    destino_pdf = tmp_path / "corpo.pdf"
    compilar_pdf(caminho_tex, destino_pdf)

    assert destino_pdf.exists()
    assert destino_pdf.stat().st_size > 0
