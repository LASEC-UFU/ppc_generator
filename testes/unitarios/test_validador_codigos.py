from __future__ import annotations

from ppcgen.modelos import CargaHoraria, ComponenteCurricular, Curriculo, TipoComponente
from ppcgen.validadores.codigos import validar_codigos
from testes.conftest import componente


def test_codigo_duplicado_gera_erro(config_basica):
    curriculo = Curriculo(versao="t", componentes=[componente("A1"), componente("A1")])
    resultado = validar_codigos(curriculo, config_basica)
    assert any(m.codigo_regra == "CODIGO_DUPLICADO" for m in resultado.erros)


def test_nome_obrigatorio(config_basica):
    # Construído diretamente (sem o helper `componente`, que preenche o nome
    # com o código quando omitido) para exercitar de fato o caso de nome vazio.
    sem_nome = ComponenteCurricular(
        codigo="A1", nome="", tipo=TipoComponente.DISCIPLINA, carga_horaria=CargaHoraria(total=30), periodo=1
    )
    curriculo = Curriculo(versao="t", componentes=[sem_nome])
    resultado = validar_codigos(curriculo, config_basica)
    assert any(m.codigo_regra == "NOME_OBRIGATORIO" for m in resultado.erros)


def test_codigo_provisorio_vira_alerta(config_basica):
    curriculo = Curriculo(versao="t", componentes=[componente("FEELT!PS")])
    resultado = validar_codigos(curriculo, config_basica)
    assert any(m.codigo_regra == "CODIGO_PROVISORIO" for m in resultado.alertas)


def test_periodo_fora_do_intervalo(config_basica):
    curriculo = Curriculo(versao="t", componentes=[componente("A1", periodo=99)])
    resultado = validar_codigos(curriculo, config_basica)
    assert any(m.codigo_regra == "PERIODO_FORA_DO_INTERVALO" for m in resultado.erros)


def test_codigo_valido_nao_gera_erro(config_basica):
    curriculo = Curriculo(versao="t", componentes=[componente("A1"), componente("A2", periodo=2)])
    resultado = validar_codigos(curriculo, config_basica)
    assert not resultado.tem_erro
