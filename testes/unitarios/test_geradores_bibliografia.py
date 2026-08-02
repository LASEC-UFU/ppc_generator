from __future__ import annotations

from ppcgen.geradores.bibliografia import gerar_bibliografia_bib
from ppcgen.modelos import EntradaBibliografica, ReferencialCurricular


def test_entrada_minima_gera_bloco_bibtex_valido():
    entrada = EntradaBibliografica(chave="teste_2024", tipo="misc", autor="Autor Teste", titulo="Título")
    bib = gerar_bibliografia_bib([entrada])
    assert "@misc{teste_2024," in bib
    assert bib.count("{") == bib.count("}")
    assert "author = {{Autor Teste}}," in bib
    assert "title = {Título}," in bib


def test_url_vira_campo_url_nativo_sem_escapar_o_link():
    entrada = EntradaBibliografica(
        chave="teste_url", tipo="misc", autor="A", titulo="T",
        url="https://exemplo.org/a%20b?x=1&y=2",
    )
    bib = gerar_bibliografia_bib([entrada])
    # campo url nativo (verbatim no datamodel do biblatex) — link não escapado
    assert "url = {https://exemplo.org/a%20b?x=1&y=2}" in bib


def test_nota_com_caracteres_especiais_e_escapada():
    entrada = EntradaBibliografica(
        chave="teste_nota", tipo="misc", autor="A", titulo="T",
        nota="Alterada em 50% dos casos & revisada",
    )
    bib = gerar_bibliografia_bib([entrada])
    assert r"50\% dos casos \& revisada" in bib


def test_campos_vazios_nao_aparecem_no_bib():
    entrada = EntradaBibliografica(chave="minimo", tipo="misc", autor="A", titulo="T")
    bib = gerar_bibliografia_bib([entrada])
    for campo in ("address", "publisher", "organization", "institution", "edition",
                  "series", "doi", "pages", "url", "note"):
        assert f"{campo} =" not in bib


def test_lista_vazia_gera_comentario_sem_quebrar():
    bib = gerar_bibliografia_bib([])
    assert bib.strip().startswith("%")


def test_multiplas_entradas_ficam_em_blocos_separados():
    entradas = [
        EntradaBibliografica(chave="a", tipo="misc", autor="A", titulo="T1"),
        EntradaBibliografica(chave="b", tipo="book", autor="B", titulo="T2"),
    ]
    bib = gerar_bibliografia_bib(entradas)
    assert "@misc{a," in bib
    assert "@book{b," in bib
    assert bib.index("@misc{a,") < bib.index("@book{b,")


def test_legislacao_tambem_entra_no_bib_sem_linha_duplicada():
    norma = ReferencialCurricular(
        id="LDB", nome="Lei de Diretrizes e Bases", documento="Lei nº 9.394/1996",
        ano=1996, url="https://exemplo.org/ldb",
    )
    bib = gerar_bibliografia_bib([], [norma])
    assert bib.count("@misc{LDB,") == 1
    assert "title = {Lei nº 9.394/1996}" in bib
    assert "url = {https://exemplo.org/ldb}" in bib


def test_mesma_chave_nas_duas_abas_e_emitida_uma_vez_e_recebe_url_da_norma():
    entrada = EntradaBibliografica(chave="LDB", tipo="misc", titulo="Título detalhado")
    norma = ReferencialCurricular(id="LDB", nome="Lei", url="https://exemplo.org/ldb")
    bib = gerar_bibliografia_bib([entrada], [norma])
    assert bib.count("@misc{LDB,") == 1
    assert "title = {Título detalhado}" in bib
    assert "url = {https://exemplo.org/ldb}" in bib
