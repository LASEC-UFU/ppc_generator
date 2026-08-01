from __future__ import annotations

from ppcgen.geradores.latex import gerar_capitulos_tex


def test_gera_um_input_por_capitulo_na_ordem():
    tex = gerar_capitulos_tex(["identificacao", "apresentacao", "justificativa"])
    assert tex == (
        "\\input{textos/identificacao}\n"
        "\\input{textos/apresentacao}\n"
        "\\input{textos/justificativa}\n"
    )


def test_lista_vazia_gera_comentario_sem_quebrar():
    tex = gerar_capitulos_tex([])
    assert tex.strip().startswith("%")
    assert "\\input" not in tex
