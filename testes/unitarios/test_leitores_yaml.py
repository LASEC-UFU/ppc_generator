from __future__ import annotations

from ppcgen.leitores.yaml import (
    carregar_areas,
    carregar_competencias,
    carregar_nucleos,
    carregar_referenciais_curso,
    carregar_referenciais_legais,
    carregar_temas_transversais,
)


def _escrever(tmp_path, nome, conteudo):
    caminho = tmp_path / nome
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_carregar_nucleos(tmp_path):
    caminho = _escrever(
        tmp_path,
        "nucleos.yaml",
        "nucleos:\n  - id: BASICO\n    nome: Formação Básica\n    descricao: teste\n",
    )
    nucleos = carregar_nucleos(caminho)
    assert len(nucleos) == 1
    assert nucleos[0].id == "BASICO"
    assert nucleos[0].nome == "Formação Básica"


def test_carregar_areas(tmp_path):
    caminho = _escrever(tmp_path, "areas.yaml", "areas:\n  - id: MATEMATICA\n    nome: Matemática\n")
    areas = carregar_areas(caminho)
    assert areas[0].id == "MATEMATICA"


def test_carregar_competencias_com_obrigatoriedade(tmp_path):
    caminho = _escrever(
        tmp_path,
        "competencias.yaml",
        "competencias:\n  - id: C1\n    descricao: teste\n    obrigatoria: true\n    fonte: X\n",
    )
    competencias = carregar_competencias(caminho)
    assert competencias[0].obrigatoria is True


def test_carregar_referenciais_legais(tmp_path):
    caminho = _escrever(
        tmp_path,
        "legislacao.yaml",
        "referenciais:\n  - id: LEI_X\n    nome: Teste\n    tipo: lei\n    documento: Lei nº 1\n    ano: 2020\n",
    )
    referenciais = carregar_referenciais_legais(caminho)
    assert referenciais[0].ano == 2020


def test_carregar_temas_transversais(tmp_path):
    caminho = _escrever(
        tmp_path,
        "temas.yaml",
        "temas:\n  - id: LIBRAS\n    nome: Libras\n    status: obrigatorio\n",
    )
    temas = carregar_temas_transversais(caminho)
    assert temas[0].status == "obrigatorio"


def test_carregar_referenciais_curso_arquivos_ausentes(tmp_path):
    # pasta vazia: nenhum arquivo de referencial existe -> listas vazias, sem erro
    referenciais = carregar_referenciais_curso(tmp_path)
    assert referenciais.nucleos == []
    assert referenciais.areas == []
    assert referenciais.competencias == []
