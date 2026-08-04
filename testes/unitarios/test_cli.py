"""Testes unitários dos montadores de lista usados pela CLI — sem tocar
LaTeX/compilação de PDF, que ficam nos testes de integração."""

from __future__ import annotations

from pathlib import Path

from ppcgen.cli import _montar_lista_anexos
from ppcgen.config import GeracaoConfig
from ppcgen.modelos import CargaHoraria, Curriculo, FichaCurricular, TipoComponente
from testes.conftest import componente, construir_perfil


def _ficha(codigo: str, caminho: Path) -> FichaCurricular:
    caminho.write_bytes(b"%PDF-fake")
    return FichaCurricular(codigo=codigo, carga_horaria=CargaHoraria(), arquivo_origem=caminho)


def test_anexar_fichas_true_inclui_fichas_na_ordem_curricular(tmp_path):
    perfil = construir_perfil(tmp_path, geracao=GeracaoConfig(anexar_fichas=True, anexar_resolucoes=False))
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("B1", periodo=2),
            componente("A1", periodo=1),
        ],
    )
    fichas = [
        _ficha("A1", tmp_path / "a1.pdf"),
        _ficha("B1", tmp_path / "b1.pdf"),
    ]

    anexos = _montar_lista_anexos(perfil, curriculo, fichas)

    assert anexos == [tmp_path / "a1.pdf", tmp_path / "b1.pdf"]


def test_anexar_fichas_false_nao_inclui_fichas(tmp_path):
    """Antes desta correção, geracao.anexar_fichas nunca era lido — as
    fichas eram sempre anexadas no PPC completo independente do valor
    configurado na aba Perfil."""

    perfil = construir_perfil(tmp_path, geracao=GeracaoConfig(anexar_fichas=False, anexar_resolucoes=False))
    curriculo = Curriculo(versao="t", componentes=[componente("A1", periodo=1)])
    fichas = [_ficha("A1", tmp_path / "a1.pdf")]

    anexos = _montar_lista_anexos(perfil, curriculo, fichas)

    assert anexos == []


def test_atividade_complementar_nunca_e_anexada(tmp_path):
    perfil = construir_perfil(tmp_path, geracao=GeracaoConfig(anexar_fichas=True, anexar_resolucoes=False))
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("AAC1", periodo=1, tipo=TipoComponente.ATIVIDADE_COMPLEMENTAR)],
    )
    fichas = [_ficha("AAC1", tmp_path / "aac1.pdf")]

    anexos = _montar_lista_anexos(perfil, curriculo, fichas)

    assert anexos == []


def test_anexar_resolucoes_inclui_pdfs_da_pasta_anexos(tmp_path):
    perfil = construir_perfil(tmp_path, geracao=GeracaoConfig(anexar_fichas=False, anexar_resolucoes=True))
    pasta_resolucoes = tmp_path / perfil.arquivos.anexos / "resolucoes"
    pasta_resolucoes.mkdir(parents=True)
    (pasta_resolucoes / "res_02.pdf").write_bytes(b"%PDF-fake")
    (pasta_resolucoes / "res_01.pdf").write_bytes(b"%PDF-fake")
    (pasta_resolucoes / "nao_e_pdf.docx").write_bytes(b"fake")
    curriculo = Curriculo(versao="t", componentes=[])

    anexos = _montar_lista_anexos(perfil, curriculo, [])

    assert anexos == [pasta_resolucoes / "res_01.pdf", pasta_resolucoes / "res_02.pdf"]
