from __future__ import annotations

from ppcgen.config import CurriculoConfig
from ppcgen.modelos import Curriculo, EnfaseFormativa, ReferenciaisCurso
from ppcgen.validadores.enfases_formativas import validar_enfases_formativas
from testes.conftest import componente, construir_perfil


def _referenciais(*siglas_nomes: tuple[str, str], componentes: dict[str, list[str]] | None = None) -> ReferenciaisCurso:
    componentes = componentes or {}
    return ReferenciaisCurso(
        enfases_formativas=[
            EnfaseFormativa(id=sigla, nome=nome, sigla=sigla, componentes=componentes.get(sigla, []))
            for sigla, nome in siglas_nomes
        ]
    )


def _perfil(minimas=1, carga_minima=1):
    return construir_perfil(
        curriculo=CurriculoConfig(enfases_formativas_minimas=minimas, carga_horaria_minima_por_enfase=carga_minima)
    )


def test_sem_enfases_cadastradas_nao_valida_nada():
    perfil = construir_perfil()
    curriculo = Curriculo(versao="t", componentes=[componente("A1", nome="Cálculo I")])
    resultado = validar_enfases_formativas(curriculo, perfil, ReferenciaisCurso())
    assert resultado.mensagens == []


def test_enfase_sem_componentes_gera_alerta():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(versao="t", componentes=[componente("A1", nome="Cálculo I")])
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_SEM_COMPONENTES" for m in resultado.alertas)


def test_minimas_ausente_gera_erro():
    perfil = construir_perfil(curriculo=CurriculoConfig(carga_horaria_minima_por_enfase=1))
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    resultado = validar_enfases_formativas(Curriculo(versao="t", componentes=[]), perfil, referenciais)
    assert any(m.codigo_regra == "ENFASES_FORMATIVAS_MINIMAS_INVALIDAS" for m in resultado.erros)


def test_minimas_maior_que_cadastradas_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    resultado = validar_enfases_formativas(Curriculo(versao="t", componentes=[]), _perfil(minimas=5), referenciais)
    assert any(m.codigo_regra == "ENFASES_FORMATIVAS_MINIMAS_INVALIDAS" for m in resultado.erros)


def test_carga_minima_ausente_gera_erro():
    perfil = construir_perfil(curriculo=CurriculoConfig(enfases_formativas_minimas=1))
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    resultado = validar_enfases_formativas(Curriculo(versao="t", componentes=[]), perfil, referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_CARGA_MINIMA_INVALIDA" for m in resultado.erros)


def test_carga_insuficiente_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"), componentes={"MIAPI": ["M1"]})
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("M1", nome="Primeira", tot=60, enfases_formativas=["MIAPI"])],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=1, carga_minima=400), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_CARGA_INSUFICIENTE" for m in resultado.erros)


def test_integralizacao_inviavel_gera_erro():
    referenciais = _referenciais(
        ("MIAPI", "Máquinas Inteligentes"), ("RASC", "Robótica"), componentes={"MIAPI": ["M1"]}
    )
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("M1", nome="Primeira", tot=60, enfases_formativas=["MIAPI"])],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=2, carga_minima=400), referenciais)
    assert any(m.codigo_regra == "ENFASES_FORMATIVAS_INTEGRALIZACAO_INVIAVEL" for m in resultado.erros)


def test_caminho_feliz_sem_mensagens():
    referenciais = _referenciais(
        ("MIAPI", "Máquinas Inteligentes"),
        ("RASC", "Robótica"),
        componentes={"MIAPI": ["M1", "M2"], "RASC": ["R1", "R2"]},
    )
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("M1", nome="Primeira", tot=60, enfases_formativas=["MIAPI"]),
            componente("M2", nome="Segunda", tot=60, enfases_formativas=["MIAPI"]),
            componente("R1", nome="Primeira", tot=60, enfases_formativas=["RASC"]),
            componente("R2", nome="Segunda", tot=60, enfases_formativas=["RASC"]),
        ],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=2, carga_minima=120), referenciais)
    assert resultado.mensagens == []


def test_componente_pertence_a_mais_de_uma_enfase_conta_para_ambas():
    referenciais = _referenciais(
        ("MIAPI", "Máquinas Inteligentes"),
        ("RASC", "Robótica"),
        componentes={"MIAPI": ["M1"], "RASC": ["M1"]},
    )
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("M1", nome="Compartilhada", tot=120, enfases_formativas=["MIAPI", "RASC"])],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=2, carga_minima=120), referenciais)
    assert resultado.mensagens == []
