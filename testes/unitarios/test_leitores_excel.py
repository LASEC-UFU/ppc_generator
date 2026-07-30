from __future__ import annotations

import openpyxl
import pytest

from ppcgen.excecoes import FormatoInvalido
from ppcgen.leitores.excel import carregar_matriz


def _matriz_minima(caminho):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    curso = wb.create_sheet("Curso")
    curso.append(["campo", "valor"])
    curso.append(["versao_curricular", "2026-teste"])

    componentes = wb.create_sheet("Componentes")
    componentes.append(
        [
            "codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio",
            "codigo_provisorio", "cht", "chp", "chd", "che", "tot",
            "nucleo_id", "unidade_oferta", "ementa", "observacoes",
        ]
    )
    componentes.append(["X1", "Disciplina X1", "disciplina", 1, True, True, False, 30, 0, 0, 0, 30, "BASICO", "UA1", "", ""])
    componentes.append(["X2", "Disciplina X2", "disciplina", 2, True, True, False, 30, 0, 0, 0, 30, "BASICO", "UA1", "", ""])

    preq = wb.create_sheet("Pre-requisitos")
    preq.append(["codigo_componente", "codigo_prerequisito", "opcional", "carga_horaria_minima"])
    preq.append(["X2", "X1", False, None])

    areas = wb.create_sheet("Areas")
    areas.append(["codigo_componente", "area_id"])
    areas.append(["X1", "MATEMATICA"])
    areas.append(["X2", "MATEMATICA"])

    wb.save(caminho)


def test_carregar_matriz_basica(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    _matriz_minima(caminho)

    curriculo, metadados, avisos = carregar_matriz(caminho)

    assert curriculo.versao == "2026-teste"
    assert len(curriculo.componentes) == 2
    x2 = curriculo.por_codigo()["X2"]
    assert x2.pre_requisitos[0].codigo == "X1"
    assert x2.areas == ["MATEMATICA"]
    assert avisos == []


def test_carregar_matriz_aba_obrigatoria_ausente(tmp_path):
    caminho = tmp_path / "matriz_invalida.xlsx"
    wb = openpyxl.Workbook()
    wb.save(caminho)

    with pytest.raises(FormatoInvalido):
        carregar_matriz(caminho)


def test_carregar_matriz_avisa_ativo_em_branco(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    curso = wb.create_sheet("Curso")
    curso.append(["campo", "valor"])
    componentes = wb.create_sheet("Componentes")
    componentes.append(
        ["codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio", "codigo_provisorio", "cht", "chp", "chd", "che", "tot", "nucleo_id", "unidade_oferta", "ementa", "observacoes"]
    )
    componentes.append(["Y1", "Disciplina Y1", "disciplina", 1, None, True, False, 30, 0, 0, 0, 30, "BASICO", "UA1", "", ""])
    wb.save(caminho)

    _curriculo, _metadados, avisos = carregar_matriz(caminho)
    assert any("ativo" in aviso for aviso in avisos)
