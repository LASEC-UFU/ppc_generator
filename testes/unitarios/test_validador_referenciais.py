from __future__ import annotations

from ppcgen.modelos import (
    AreaFormacao,
    Competencia,
    Conteudo,
    Curriculo,
    NucleoCurricular,
    ReferenciaisCurso,
    TemaTransversal,
)
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


def test_nucleo_componente_inexistente_gera_erro():
    """Código listado em ``componentes`` da aba Nucleos que não existe na
    aba Componentes — direção catálogo -> componente (Seção 8)."""

    referenciais = ReferenciaisCurso(
        nucleos=[NucleoCurricular(id="BASICO", nome="Básico", componentes=["INEXISTENTE"])]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "NUCLEO_COMPONENTE_INEXISTENTE" for m in resultado.erros)


def test_area_componente_inexistente_gera_erro():
    referenciais = ReferenciaisCurso(
        areas=[AreaFormacao(id="MATEMATICA", nome="Matemática", componentes=["INEXISTENTE"])]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "AREA_COMPONENTE_INEXISTENTE" for m in resultado.erros)


def test_tema_transversal_componente_inexistente_gera_erro():
    referenciais = ReferenciaisCurso(
        temas_transversais=[TemaTransversal(id="LIBRAS", nome="Libras", componentes=["INEXISTENTE"])]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "TEMA_TRANSVERSAL_COMPONENTE_INEXISTENTE" for m in resultado.erros)


def test_conteudo_componente_inexistente_gera_erro():
    referenciais = ReferenciaisCurso(
        conteudos=[Conteudo(id="DCN_01", descricao="teste", componentes=["INEXISTENTE"])]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "CONTEUDO_COMPONENTE_INEXISTENTE" for m in resultado.erros)


def test_competencia_componente_inexistente_gera_erro():
    referenciais = ReferenciaisCurso(
        competencias=[Competencia(id="C1", descricao="teste", componentes=["INEXISTENTE"])]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "COMPETENCIA_COMPONENTE_INEXISTENTE" for m in resultado.erros)


def test_componente_em_mais_de_um_nucleo_gera_erro():
    referenciais = ReferenciaisCurso(
        nucleos=[
            NucleoCurricular(id="BASICO", nome="Básico", componentes=["A1"]),
            NucleoCurricular(id="TECNOLOGICO", nome="Tecnológico", componentes=["A1"]),
        ]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert any(m.codigo_regra == "NUCLEO_MULTIPLO_PARA_COMPONENTE" for m in resultado.erros)


def test_componente_em_um_so_nucleo_nao_gera_erro_de_conflito():
    referenciais = ReferenciaisCurso(
        nucleos=[
            NucleoCurricular(id="BASICO", nome="Básico", componentes=["A1"]),
            NucleoCurricular(id="TECNOLOGICO", nome="Tecnológico", componentes=["A2"]),
        ]
    )
    curriculo = Curriculo(versao="t", componentes=[componente("A1"), componente("A2")])
    resultado = validar_referenciais(curriculo, referenciais)
    assert not any(m.codigo_regra == "NUCLEO_MULTIPLO_PARA_COMPONENTE" for m in resultado.mensagens)


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
