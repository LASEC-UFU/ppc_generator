from __future__ import annotations

from ppcgen.modelos import Competencia, Curriculo, NucleoCurricular, ReferenciaisCurso
from ppcgen.validadores.referenciais import validar_referenciais
from testes.conftest import componente


def test_componente_sem_nucleo_gera_erro():
    curriculo = Curriculo(versao="t", componentes=[componente("A1", nucleo=None)])
    resultado = validar_referenciais(curriculo, ReferenciaisCurso())
    assert any(m.codigo_regra == "COMPONENTE_SEM_NUCLEO" for m in resultado.erros)


def test_componente_sem_area_gera_erro():
    curriculo = Curriculo(versao="t", componentes=[componente("A1", areas=[])])
    resultado = validar_referenciais(curriculo, ReferenciaisCurso())
    assert any(m.codigo_regra == "COMPONENTE_SEM_AREA" for m in resultado.erros)


def test_nucleo_inexistente_no_catalogo_gera_erro():
    referenciais = ReferenciaisCurso(nucleos=[NucleoCurricular(id="BASICO", nome="Básico")])
    curriculo = Curriculo(versao="t", componentes=[componente("A1", nucleo="INEXISTENTE")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "NUCLEO_INEXISTENTE" for m in resultado.erros)


def test_competencia_obrigatoria_sem_cobertura_gera_alerta():
    referenciais = ReferenciaisCurso(
        competencias=[Competencia(id="C1", descricao="teste", obrigatoria=True)]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1", competencias=[])])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "COMPETENCIA_OBRIGATORIA_SEM_COBERTURA" for m in resultado.alertas)


def test_competencia_coberta_nao_gera_alerta():
    referenciais = ReferenciaisCurso(
        competencias=[Competencia(id="C1", descricao="teste", obrigatoria=True)]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1", competencias=["C1"])])
    resultado = validar_referenciais(curriculo, referenciais)
    assert not any(m.codigo_regra == "COMPETENCIA_OBRIGATORIA_SEM_COBERTURA" for m in resultado.mensagens)
