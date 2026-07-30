from __future__ import annotations

from ppcgen.config import InfoPerfil
from ppcgen.validadores.perfil import validar_perfil
from testes.conftest import construir_perfil


def test_id_com_maiuscula_gera_erro(tmp_path):
    perfil = construir_perfil(tmp_path, info=InfoPerfil(id="Curso_Invalido", nome="X"))
    resultado = validar_perfil(perfil)
    assert any(m.codigo_regra == "PERFIL-000" for m in resultado.erros)


def test_id_com_prefixo_00_gera_erro(tmp_path):
    # "00" é reservado para material de referência guardado manualmente em
    # saida/ (ex.: saida/00old/), ignorado por `ppcgen limpar --todos` —
    # nenhum perfil real pode usar esse prefixo, para nunca colidir.
    perfil = construir_perfil(tmp_path, info=InfoPerfil(id="00old", nome="X"))
    resultado = validar_perfil(perfil)
    assert any(m.codigo_regra == "PERFIL-000" for m in resultado.erros)


def test_id_valido_nao_gera_erro_de_formato(tmp_path):
    perfil = construir_perfil(tmp_path, info=InfoPerfil(id="curso_2026_1", nome="X"))
    resultado = validar_perfil(perfil)
    assert not any(m.codigo_regra == "PERFIL-000" for m in resultado.erros)
