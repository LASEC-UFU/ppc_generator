from __future__ import annotations

from ppcgen.leitores.csv import carregar_csv_legado
from ppcgen.modelos import TipoComponente

CABECALHO = (
    "Nome;Código;PER;CHT;CHP;CHD;CHE;TOT;FLX;OBR;OPT;A|B;EXT;FORM_BAS;FORM_HUM;FORM_TEC;FORM_CMP;"
    "CC_UO1;CC_SM2;CC_SAI3;CC_SD4;CC_SF5;CC_HW6;PREQ;CREQ;Elementos41;Níveis41;Elementos42;Níveis42;"
    "Disposições;Ementa;QEXTR;DCN_base;DCN_ecp\n"
)


def _linha(nome, codigo, per, tot=60, obr="True", ext="False", form_bas="True", preq="", qextr=""):
    campos = [nome, codigo, per, "60", "0", "0", "0", str(tot), "True", obr, "False", "A", ext,
              form_bas, "False", "False", "False", "False", "False", "False", "False", "False", "False",
              preq, "", "", "", "", "", "", "", qextr, "", ""]
    return ";".join(campos) + "\n"


def test_importa_disciplina_basica(tmp_path):
    caminho = tmp_path / "legado.csv"
    caminho.write_text(
        CABECALHO + _linha("Cálculo I", "MAT101", "1"), encoding="utf-8"
    )

    resultado = carregar_csv_legado(caminho)
    assert len(resultado.curriculo.componentes) == 1
    disc = resultado.curriculo.componentes[0]
    assert disc.codigo == "MAT101"
    assert disc.periodo == 1
    assert disc.nucleo == "BASICO"
    assert disc.tipo == TipoComponente.DISCIPLINA


def test_importa_acc_gera_alerta_de_migracao(tmp_path):
    caminho = tmp_path / "legado.csv"
    caminho.write_text(
        CABECALHO + _linha("Atividade de Conclusão", "ACC", "acc", tot=300), encoding="utf-8"
    )
    resultado = carregar_csv_legado(caminho)
    assert resultado.curriculo.componentes[0].tipo == TipoComponente.OUTRO
    assert any("acc" in aviso for aviso in resultado.alertas_migracao)


def test_importa_qextr_mapeado_para_tema_estavel(tmp_path):
    caminho = tmp_path / "legado.csv"
    caminho.write_text(
        CABECALHO + _linha("Libras", "LIB01", "3", qextr="3"), encoding="utf-8"
    )
    resultado = carregar_csv_legado(caminho)
    assert "LIBRAS" in resultado.curriculo.componentes[0].temas_transversais


def test_codigo_provisorio_detectado(tmp_path):
    caminho = tmp_path / "legado.csv"
    caminho.write_text(
        CABECALHO + _linha("Optativa X", "FEELT!PS", "1"), encoding="utf-8"
    )
    resultado = carregar_csv_legado(caminho)
    assert resultado.curriculo.componentes[0].codigo_provisorio is True
