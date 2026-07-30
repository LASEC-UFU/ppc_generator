"""Testes de isolamento entre perfis (Seção 21): um perfil não pode ler nem
escrever fora da própria pasta a não ser via ``heranca`` explícita; a
seleção de perfil nunca é implícita.
"""

from __future__ import annotations

import pytest

from ppcgen.config import carregar_perfil
from ppcgen.excecoes import ConfiguracaoInvalida
from ppcgen.scaffolding import criar_perfil


def test_caminho_rejeita_escape_para_outro_perfil(tmp_path):
    pasta_perfis = tmp_path / "perfis"
    pasta_perfis.mkdir()
    criar_perfil(pasta_perfis, "perfil_a", "Perfil A")
    criar_perfil(pasta_perfis, "perfil_b", "Perfil B")
    (pasta_perfis / "perfil_b" / "segredo.txt").write_text("dado de outro perfil", encoding="utf-8")

    perfil_a = carregar_perfil(pasta_perfis / "perfil_a", raiz_dados=tmp_path)

    with pytest.raises(ConfiguracaoInvalida):
        perfil_a.caminho("../perfil_b/segredo.txt")


def test_resolver_arquivo_nao_escapa_via_dotdot(tmp_path):
    pasta_perfis = tmp_path / "perfis"
    pasta_perfis.mkdir()
    criar_perfil(pasta_perfis, "perfil_a", "Perfil A")
    criar_perfil(pasta_perfis, "perfil_b", "Perfil B")
    (pasta_perfis / "perfil_b" / "segredo.txt").write_text("dado de outro perfil", encoding="utf-8")

    perfil_a = carregar_perfil(pasta_perfis / "perfil_a", raiz_dados=tmp_path)

    with pytest.raises(ConfiguracaoInvalida):
        perfil_a.resolver_arquivo("../perfil_b/segredo.txt")


def test_geracao_de_um_perfil_nao_grava_em_outro(tmp_path):
    """As saídas de dois perfis, geradas na mesma rodada, nunca se misturam."""

    from ppcgen.geradores.latex import gerar_arquivos_latex
    from ppcgen.leitores.yaml import ReferenciaisCurso
    from ppcgen.modelos import Curriculo
    from testes.conftest import componente, construir_perfil

    perfil_a = construir_perfil(tmp_path / "perfil_a")
    perfil_b = construir_perfil(tmp_path / "perfil_b")

    curriculo = Curriculo(versao="t", componentes=[componente("X1", nome="Disciplina X1")])
    referenciais = ReferenciaisCurso()

    pasta_saida_a = tmp_path / "saida" / "perfil_a" / "gerado"
    pasta_saida_b = tmp_path / "saida" / "perfil_b" / "gerado"

    gerar_arquivos_latex(curriculo, perfil_a, referenciais, pasta_saida_a)
    gerar_arquivos_latex(curriculo, perfil_b, referenciais, pasta_saida_b)

    assert pasta_saida_a.exists()
    assert pasta_saida_b.exists()
    # Nenhum arquivo de um vazou para a pasta do outro além do esperado.
    assert set(p.name for p in pasta_saida_a.iterdir()) == set(p.name for p in pasta_saida_b.iterdir())
    assert pasta_saida_a != pasta_saida_b


def test_cli_exige_selecao_explicita_de_perfil(monkeypatch, tmp_path):
    from ppcgen import cli

    monkeypatch.setattr(cli, "_perfil_padrao_local", lambda: None)
    args = type("Args", (), {"perfil": None, "perfil_dir": None})()

    with pytest.raises(ConfiguracaoInvalida):
        cli._resolver_perfil(args)
