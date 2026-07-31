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
            "cht", "chp", "chd", "che", "tot", "observacoes",
            "pre_requisitos", "correquisitos",
        ]
    )
    componentes.append(
        ["X1", "Disciplina X1", "disciplina", 1, True, True, 30, 0, 0, 0, 30, "", "", ""]
    )
    componentes.append(
        ["X2", "Disciplina X2", "disciplina", 2, True, True, 30, 0, 0, 0, 30, "", "X1", ""]
    )

    nucleos = wb.create_sheet("Nucleos")
    nucleos.append(["id", "nome", "descricao", "componentes"])
    nucleos.append(["BASICO", "Formação Básica", "", "X1|X2"])

    areas = wb.create_sheet("Areas")
    areas.append(["id", "nome", "descricao", "componentes"])
    areas.append(["MATEMATICA", "Matemática", "", "X1|X2"])

    wb.save(caminho)


def test_carregar_matriz_basica(tmp_path):
    caminho = tmp_path / "matriz.xlsx"
    _matriz_minima(caminho)

    curriculo, referenciais, avisos = carregar_matriz(caminho)

    assert len(curriculo.componentes) == 2
    x2 = curriculo.por_codigo()["X2"]
    assert x2.pre_requisitos[0].codigo == "X1"
    assert x2.nucleo == "BASICO"
    assert x2.areas == ["MATEMATICA"]
    assert avisos == []
    assert referenciais.ids_nucleos() == {"BASICO"}
    assert referenciais.ids_areas() == {"MATEMATICA"}
    # legislação não vem da matriz — fica vazia aqui, quem carrega o perfil
    # completo (ppcgen.cli._carregar_contexto) que preenche.
    assert referenciais.legislacao == []
    # competências vêm da aba Competencias, igual às demais — não existe
    # nesta fixture mínima, então o catálogo fica vazio.
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
        ["codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio", "cht", "chp", "chd", "che", "tot", "observacoes"]
    )
    componentes.append(["Y1", "Disciplina Y1", "disciplina", 1, None, True, 30, 0, 0, 0, 30, ""])
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
            "cht", "chp", "chd", "che", "tot", "observacoes",
            "pre_requisitos", "correquisitos",
        ]
    )
    componentes.append(
        ["Z1", "Estágio", "estagio", None, True, True, 0, 0, 0, 0, 300, "",
         "X1, X2 (opcional), >=1200h", "X3 (opcional)"]
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


def test_componentes_de_catalogo_vazio_nao_vincula_nada(tmp_path):
    """Célula ``componentes`` em branco numa aba de catálogo vira lista
    vazia (``_lista_ids_pipe``), nunca ``[""]`` — nenhum componente é
    vinculado."""

    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    componentes = wb.create_sheet("Componentes")
    componentes.append(["codigo", "nome", "tipo"])
    componentes.append(["W1", "Disciplina W1", "disciplina"])

    nucleos = wb.create_sheet("Nucleos")
    nucleos.append(["id", "nome", "descricao", "componentes"])
    nucleos.append(["BASICO", "Básico", "", None])

    areas = wb.create_sheet("Areas")
    areas.append(["id", "nome", "descricao", "componentes"])
    areas.append(["MATEMATICA", "Matemática", "", "  "])

    wb.save(caminho)

    curriculo, referenciais, _avisos = carregar_matriz(caminho)
    w1 = curriculo.por_codigo()["W1"]
    assert w1.nucleo is None
    assert w1.areas == []
    assert w1.temas_transversais == []
    assert w1.conteudos == []
    assert referenciais.nucleos[0].componentes == []
    assert referenciais.areas[0].componentes == []


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

    competencias = wb.create_sheet("Competencias")
    competencias.append(["id", "descricao", "obrigatoria", "fonte"])
    competencias.append(["COMP_01", "Competência de teste", True, "Fonte X"])

    wb.save(caminho)

    _curriculo, referenciais, _avisos = carregar_matriz(caminho)
    assert referenciais.nucleos[0].id == "BASICO"
    assert referenciais.temas_transversais[0].status == "obrigatorio"
    assert referenciais.conteudos[0].obrigatorio is True
    assert referenciais.competencias[0].id == "COMP_01"
    assert referenciais.competencias[0].obrigatoria is True


def test_codigo_provisorio_e_unidade_oferta_derivados_do_codigo(tmp_path):
    """Nenhuma das duas colunas existe mais na planilha (Seção 9) — ambas
    são calculadas a partir de ``codigo``: ``unidade_oferta`` é o prefixo
    até o primeiro dígito/``!``; ``codigo_provisorio`` é ``True`` só para
    o prefixo ``FEELT!``."""

    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    componentes = wb.create_sheet("Componentes")
    componentes.append(["codigo", "nome", "tipo"])
    componentes.append(["FAMAT31011", "Cálculo I", "disciplina"])
    componentes.append(["FEELT!TDCA", "Tópicos em Automação", "disciplina"])
    wb.save(caminho)

    curriculo, _referenciais, _avisos = carregar_matriz(caminho)
    por_codigo = curriculo.por_codigo()

    oficial = por_codigo["FAMAT31011"]
    assert oficial.unidade_oferta == "FAMAT"
    assert oficial.codigo_provisorio is False

    provisorio = por_codigo["FEELT!TDCA"]
    assert provisorio.unidade_oferta == "FEELT"
    assert provisorio.codigo_provisorio is True


def test_vinculo_de_catalogo_a_componente_inexistente_nao_e_descartado(tmp_path):
    """Um código listado em ``componentes`` que não existe na aba
    Componentes não derruba dado nem lança exceção aqui (Seção 29) — fica
    preservado em ``NucleoCurricular.componentes`` (bruto) para
    ``ppcgen.validadores.referenciais`` reportar."""

    caminho = tmp_path / "matriz.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    componentes = wb.create_sheet("Componentes")
    componentes.append(["codigo", "nome", "tipo", "ativo"])
    componentes.append(["V1", "Disciplina V1", "disciplina", True])

    nucleos = wb.create_sheet("Nucleos")
    nucleos.append(["id", "nome", "descricao", "componentes"])
    nucleos.append(["BASICO", "Básico", "", "V1|FANTASMA"])

    wb.save(caminho)

    curriculo, referenciais, avisos = carregar_matriz(caminho)
    v1 = curriculo.por_codigo()["V1"]
    assert v1.nucleo == "BASICO"
    assert referenciais.nucleos[0].componentes == ["V1", "FANTASMA"]
    assert avisos == []
