"""Fixtures compartilhadas entre os testes unitários e de integração."""

from __future__ import annotations

from pathlib import Path

import pytest

from ppcgen.config import (
    ArquivosConfig,
    CapaConfig,
    ComissaoConfig,
    CurriculoConfig,
    CursoConfig,
    GeracaoConfig,
    InfoPerfil,
    InstituicaoConfig,
    OfertaConfig,
    Perfil,
    SaidaConfig,
)
from ppcgen.modelos import (
    CargaHoraria,
    ComponenteCurricular,
    Correquisito,
    PreRequisito,
    TipoComponente,
)


def componente(
    codigo: str,
    nome: str = "",
    tipo: TipoComponente = TipoComponente.DISCIPLINA,
    periodo: int | None = 1,
    cht: int | None = 30,
    chp: int | None = 0,
    chd: int | None = 0,
    che: int | None = 0,
    tot: int | None = None,
    obrigatorio: bool = True,
    ativo: bool = True,
    nucleo: str | None = "BASICO",
    areas: list[str] | None = None,
    pre_requisitos: list[PreRequisito] | None = None,
    correquisitos: list[Correquisito] | None = None,
    **outros,
) -> ComponenteCurricular:
    if tot is None:
        partes = [p for p in (cht, chp, chd, che) if p is not None]
        tot = sum(partes) if partes else 0
    return ComponenteCurricular(
        codigo=codigo,
        nome=nome or codigo,
        tipo=tipo,
        carga_horaria=CargaHoraria(teorica=cht, pratica=chp, ead=chd, extensao=che, total=tot),
        periodo=periodo,
        obrigatorio=obrigatorio,
        ativo=ativo,
        nucleo=nucleo,
        areas=areas if areas is not None else ["MATEMATICA"],
        pre_requisitos=pre_requisitos or [],
        correquisitos=correquisitos or [],
        **outros,
    )


def construir_perfil(tmp_path: Path | None = None, **overrides) -> Perfil:
    """Constrói um Perfil mínimo em memória para testes unitários — não lê
    nenhuma planilha do disco (a menos que o teste explicitamente queira
    exercitar o carregamento, caso em que deve usar
    ``ppcgen.config.carregar_perfil`` diretamente sobre um fixture real)."""

    diretorio = tmp_path or Path(".")
    base = {
        "info": InfoPerfil(id="perfil_teste", nome="Perfil de Teste"),
        "curso": CursoConfig(numero_periodos=4),
        "instituicao": InstituicaoConfig(),
        "curriculo": CurriculoConfig(),
        "oferta": OfertaConfig(),
        "capa": CapaConfig(),
        "comissao": ComissaoConfig(),
        "arquivos": ArquivosConfig(),
        "geracao": GeracaoConfig(),
        "saida": SaidaConfig(),
        "diretorio": diretorio,
        "raiz_dados": diretorio.parent if diretorio != Path(".") else Path("."),
    }
    base.update(overrides)
    return Perfil(**base)


@pytest.fixture
def config_basica() -> Perfil:
    return construir_perfil(curso=CursoConfig(numero_periodos=4))


@pytest.fixture
def raiz_projeto() -> Path:
    return Path(__file__).resolve().parent.parent
