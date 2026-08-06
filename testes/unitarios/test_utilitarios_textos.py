from __future__ import annotations

from ppcgen.utilitarios.textos import analisar_prefixo_enfase_formativa


def test_prefixo_valido_simples():
    resultado = analisar_prefixo_enfase_formativa("MIAPI 1: Máquinas Elétricas Inteligentes")
    assert resultado is not None
    assert resultado.sigla == "MIAPI"
    assert resultado.numero_bruto == "1"
    assert resultado.numero_valido == 1
    assert resultado.nome_disciplina == "Máquinas Elétricas Inteligentes"


def test_prefixo_valido_outras_siglas():
    assert analisar_prefixo_enfase_formativa("RASC 2: Controle Robusto").sigla == "RASC"
    assert analisar_prefixo_enfase_formativa("SEICI 3: IA Embarcada").numero_valido == 3


def test_disciplina_sem_prefixo_retorna_none():
    assert analisar_prefixo_enfase_formativa("Cálculo Diferencial e Integral I") is None
    assert analisar_prefixo_enfase_formativa("TCC: Trabalho de Conclusão de Curso") is None


def test_numero_invalido_ainda_reconhece_sigla():
    for nome, numero_bruto in (
        ("MIAPI 0: X", "0"),
        ("MIAPI -1: X", "-1"),
        ("MIAPI I: X", "I"),
    ):
        resultado = analisar_prefixo_enfase_formativa(nome)
        assert resultado is not None, nome
        assert resultado.sigla == "MIAPI"
        assert resultado.numero_bruto == numero_bruto
        assert resultado.numero_valido is None


def test_nome_disciplina_ausente():
    resultado = analisar_prefixo_enfase_formativa("MIAPI 1:")
    assert resultado is not None
    assert resultado.nome_disciplina == ""
