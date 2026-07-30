from __future__ import annotations

import pytest

from ppcgen.utilitarios.latex import cabecalho_gerado, escapar


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("100%", r"100\%"),
        ("A & B", r"A \& B"),
        ("R$ 10", r"R\$ 10"),
        ("C#", r"C\#"),
        ("nome_completo", r"nome\_completo"),
        ("{chave}", r"\{chave\}"),
        ("a~b", r"a\textasciitilde{}b"),
        ("x^2", r"x\textasciicircum{}2"),
        ("\\comando", r"\textbackslash{}comando"),
    ],
)
def test_escapar_caracteres_especiais(entrada, esperado):
    assert escapar(entrada) == esperado


def test_escapar_acentos_nao_sao_alterados():
    assert escapar("Programação e Comunicação Técnica") == "Programação e Comunicação Técnica"


def test_escapar_none_ou_vazio():
    assert escapar(None) == ""
    assert escapar("") == ""


def test_escapar_nao_faz_escape_duplo_do_backslash_gerado():
    # Garante que o '\' introduzido por um escape anterior não é escapado de novo
    resultado = escapar("50%")
    assert resultado.count("\\") == 1


def test_cabecalho_gerado_contem_aviso_e_fonte():
    texto = cabecalho_gerado("dados/matriz_curricular.xlsx", "2026-1")
    assert "NAO EDITE MANUALMENTE" in texto
    assert "dados/matriz_curricular.xlsx" in texto
    assert "2026-1" in texto
