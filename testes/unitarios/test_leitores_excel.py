from __future__ import annotations

import openpyxl
import pytest

from ppcgen.excecoes import FormatoInvalido
from ppcgen.leitores.excel import carregar_matriz


def _matriz_minima(caminho):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    componentes = wb.create_sheet("Componentes")
    componentes.append(
        [
            "codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio",
            "codigo_provisorio", "cht", "chp", "chd", "che", "tot",
            "nucleo_id", "unidade_oferta", "observacoes",
            "pre_requisitos", "correquisitos", "areas", "temas", "conteudos", "competencias",
        ]
    )
    componentes.append(
        ["X1", "Disciplina X1", "disciplina", 1, True, True, False, 30, 0, 0, 0, 30,
         "BASICO", "UA1", "", "", "", "MATEMATICA", "", "", ""]
    )
    componentes.append(
        ["X2", "Disciplina X2", "disciplina", 2, True, True, False, 30, 0, 0, 0, 30,
         "BASICO", "UA1", "", "X1", "", "MATEMATICA", "", "", ""]
    )

    nucleos = wb.create_sheet("Nucleos")
    nucleos.append(["id", "nome", "descricao"])
    nucleos.append(["BASICO", "Formação Básica", ""])

    areas = wb.create_sheet("Areas")
    areas.append(["id", "nome", "descricao"])
    areas.append(["MATEMATICA", "Matemática", ""])

    wb.save(caminho)


def test_carregar_matriz_basica(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    _matriz_minima(caminho)

    curriculo, referenciais, avisos = carregar_matriz(caminho)

    assert len(curriculo.componentes) == 2
    x2 = curriculo.por_codigo()["X2"]
    assert x2.pre_requisitos[0].codigo == "X1"
    assert x2.areas == ["MATEMATICA"]
    assert avisos == []
    assert referenciais.ids_nucleos() == {"BASICO"}
    assert referenciais.ids_areas() == {"MATEMATICA"}
    # legislação/competências não vêm da matriz — ficam vazias aqui, quem
    # carrega o perfil completo (ppcgen.cli._carregar_contexto) que preenche.
    assert referenciais.legislacao == []
    assert referenciais.competencias == []


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
    componentes = wb.create_sheet("Componentes")
    componentes.append(
        ["codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio", "codigo_provisorio", "cht", "chp", "chd", "che", "tot", "nucleo_id", "unidade_oferta", "observacoes"]
    )
    componentes.append(["Y1", "Disciplina Y1", "disciplina", 1, None, True, False, 30, 0, 0, 0, 30, "BASICO", "UA1", ""])
    wb.save(caminho)

    _curriculo, _referenciais, avisos = carregar_matriz(caminho)
    assert any("ativo" in aviso for aviso in avisos)


def test_curriculo_versao_vem_em_branco_da_matriz(tmp_path):
    """Não há mais aba ``Curso`` — a versão curricular é responsabilidade de
    quem chama (``perfil.info.versao``), nunca duplicada na planilha."""

    caminho = tmp_path / "matriz.xlsx"
    _matriz_minima(caminho)
    curriculo, _referenciais, _avisos = carregar_matriz(caminho)
    assert curriculo.versao == ""


def test_pre_requisitos_com_opcional_e_carga_horaria_minima(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    componentes = wb.create_sheet("Componentes")
    componentes.append(
        [
            "codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio",
            "codigo_provisorio", "cht", "chp", "chd", "che", "tot",
            "nucleo_id", "unidade_oferta", "observacoes",
            "pre_requisitos", "correquisitos", "areas", "temas", "conteudos", "competencias",
        ]
    )
    componentes.append(
        ["Z1", "Estágio", "estagio", None, True, True, False, 0, 0, 0, 0, 300,
         "TECNOLOGICO", "", "",
         "X1, X2 (opcional), >=1200h", "X3 (opcional)", "", "", "", ""]
    )
    wb.save(caminho)

    curriculo, _referenciais, _avisos = carregar_matriz(caminho)
    z1 = curriculo.por_codigo()["Z1"]

    assert len(z1.pre_requisitos) == 3
    assert z1.pre_requisitos[0].codigo == "X1"
    assert z1.pre_requisitos[0].opcional is False
    assert z1.pre_requisitos[1].codigo == "X2"
    assert z1.pre_requisitos[1].opcional is True
    assert z1.pre_requisitos[2].codigo == ""
    assert z1.pre_requisitos[2].carga_horaria_minima == 1200

    assert len(z1.correquisitos) == 1
    assert z1.correquisitos[0].codigo == "X3"
    assert z1.correquisitos[0].opcional is True


def test_lista_ids_vazia_para_celula_em_branco(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    componentes = wb.create_sheet("Componentes")
    componentes.append(["codigo", "nome", "tipo", "areas", "temas", "conteudos"])
    componentes.append(["W1", "Disciplina W1", "disciplina", None, "", "  "])
    wb.save(caminho)

    curriculo, _referenciais, _avisos = carregar_matriz(caminho)
    w1 = curriculo.por_codigo()["W1"]
    assert w1.areas == []
    assert w1.temas_transversais == []
    assert w1.conteudos == []


def test_carregar_registros_referenciais_completo(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    wb.create_sheet("Componentes").append(["codigo", "nome", "tipo"])

    nucleos = wb.create_sheet("Nucleos")
    nucleos.append(["id", "nome", "descricao"])
    nucleos.append(["BASICO", "Básico", "texto"])

    temas = wb.create_sheet("Temas")
    temas.append(["id", "nome", "descricao", "fonte_normativa", "status"])
    temas.append(["LIBRAS", "Libras", "", "Decreto nº 5.626/2005", "obrigatorio"])

    conteudos = wb.create_sheet("Conteudos")
    conteudos.append(["id", "descricao", "obrigatorio", "fonte"])
    conteudos.append(["DCN_01", "Conteúdo de teste", True, "DCN X"])

    wb.save(caminho)

    _curriculo, referenciais, _avisos = carregar_matriz(caminho)
    assert referenciais.nucleos[0].id == "BASICO"
    assert referenciais.temas_transversais[0].status == "obrigatorio"
    assert referenciais.conteudos[0].obrigatorio is True
