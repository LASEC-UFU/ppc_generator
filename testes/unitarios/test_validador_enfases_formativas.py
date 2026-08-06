from __future__ import annotations

from ppcgen.config import CurriculoConfig
from ppcgen.modelos import Curriculo, EnfaseFormativa, ReferenciaisCurso
from ppcgen.validadores.enfases_formativas import validar_enfases_formativas
from testes.conftest import componente, construir_perfil


def _referenciais(*siglas_nomes: tuple[str, str]) -> ReferenciaisCurso:
    return ReferenciaisCurso(
        enfases_formativas=[EnfaseFormativa(id=sigla, nome=nome, sigla=sigla) for sigla, nome in siglas_nomes]
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


def test_nomenclatura_invalida_nome_ausente_apos_dois_pontos():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(versao="t", componentes=[componente("M1", nome="MIAPI 1:")])
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_NOMENCLATURA_INVALIDA" for m in resultado.erros)


def test_sigla_inexistente_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(versao="t", componentes=[componente("M1", nome="RASC 1: Controle Robusto")])
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_SIGLA_INEXISTENTE" for m in resultado.erros)


def test_numero_invalido_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(versao="t", componentes=[componente("M1", nome="MIAPI 0: Nome Qualquer")])
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_NUMERO_INVALIDO" for m in resultado.erros)


def test_numero_duplicado_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("M1", nome="MIAPI 1: Primeira"),
            componente("M2", nome="MIAPI 1: Segunda"),
        ],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_NUMERO_DUPLICADO" for m in resultado.erros)


def test_sequencia_inconsistente_gera_alerta():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("M1", nome="MIAPI 1: Primeira"),
            componente("M2", nome="MIAPI 3: Terceira"),
        ],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_SEQUENCIA_INCONSISTENTE" for m in resultado.alertas)


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
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"))
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("M1", nome="MIAPI 1: Primeira", tot=60, enfase_formativa_id="MIAPI")],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=1, carga_minima=400), referenciais)
    assert any(m.codigo_regra == "ENFASE_FORMATIVA_CARGA_INSUFICIENTE" for m in resultado.erros)


def test_integralizacao_inviavel_gera_erro():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"), ("RASC", "Robótica"))
    curriculo = Curriculo(
        versao="t",
        componentes=[componente("M1", nome="MIAPI 1: Primeira", tot=60, enfase_formativa_id="MIAPI")],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=2, carga_minima=400), referenciais)
    assert any(m.codigo_regra == "ENFASES_FORMATIVAS_INTEGRALIZACAO_INVIAVEL" for m in resultado.erros)


def test_caminho_feliz_sem_mensagens():
    referenciais = _referenciais(("MIAPI", "Máquinas Inteligentes"), ("RASC", "Robótica"))
    curriculo = Curriculo(
        versao="t",
        componentes=[
            componente("M1", nome="MIAPI 1: Primeira", tot=60, enfase_formativa_id="MIAPI"),
            componente("M2", nome="MIAPI 2: Segunda", tot=60, enfase_formativa_id="MIAPI"),
            componente("R1", nome="RASC 1: Primeira", tot=60, enfase_formativa_id="RASC"),
            componente("R2", nome="RASC 2: Segunda", tot=60, enfase_formativa_id="RASC"),
        ],
    )
    resultado = validar_enfases_formativas(curriculo, _perfil(minimas=2, carga_minima=120), referenciais)
    assert resultado.mensagens == []
