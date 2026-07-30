"""Validação das fichas de componentes curriculares contra a matriz (Seções 9
e 15): compara código, nome, carga horária, pré-requisitos e preenchimento
dos campos textuais obrigatórios, além de classificar a situação de cada
ficha (localizada/consistente, divergente, ausente, não reconhecida,
duplicada ou de currículo anterior).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ppcgen.modelos import (
    AlertaValidacao,
    Curriculo,
    ErroValidacao,
    FichaCurricular,
    ResultadoValidacao,
    StatusFicha,
    TipoComponente,
)
from ppcgen.utilitarios.textos import slug

_TIPOS_SEM_FICHA_OBRIGATORIA = {TipoComponente.ATIVIDADE_COMPLEMENTAR}
_CAMPOS_TEXTUAIS_OBRIGATORIOS = (
    "ementa",
    "objetivos",
    "programa",
    "metodologia",
    "avaliacao",
    "bibliografia_basica",
    "bibliografia_complementar",
)


@dataclass
class SituacaoFichas:
    status_por_componente: dict[str, StatusFicha] = field(default_factory=dict)
    fichas_orfas: list[str] = field(default_factory=list)


def avaliar_fichas(
    curriculo: Curriculo, fichas: list[FichaCurricular]
) -> tuple[ResultadoValidacao, SituacaoFichas]:
    resultado = ResultadoValidacao()
    situacao = SituacaoFichas()

    fichas_por_codigo: dict[str, list[FichaCurricular]] = {}
    for ficha in fichas:
        fichas_por_codigo.setdefault(ficha.codigo, []).append(ficha)

    codigos_matriz = {c.codigo for c in curriculo.componentes}

    for c in curriculo.ativos():
        if c.tipo in _TIPOS_SEM_FICHA_OBRIGATORIA:
            continue

        candidatas = fichas_por_codigo.get(c.codigo, [])
        candidatas_reconhecidas = [f for f in candidatas if f.confianca_extracao > 0]

        if not candidatas:
            situacao.status_por_componente[c.codigo] = StatusFicha.AUSENTE
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_AUSENTE",
                    f"componente '{c.codigo}' não possui ficha curricular localizada.",
                    componente=c.codigo,
                )
            )
            continue

        if not candidatas_reconhecidas:
            situacao.status_por_componente[c.codigo] = StatusFicha.NAO_RECONHECIDA
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_NAO_RECONHECIDA",
                    f"ficha de '{c.codigo}' foi localizada mas não pôde ser lida com "
                    "confiança (ex.: PDF sem camada de texto); revisão manual necessária.",
                    componente=c.codigo,
                )
            )
            continue

        if len(candidatas_reconhecidas) > 1:
            situacao.status_por_componente[c.codigo] = StatusFicha.DUPLICADA
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_DUPLICADA",
                    f"mais de uma ficha reconhecida para o código '{c.codigo}' "
                    f"({len(candidatas_reconhecidas)} arquivos).",
                    componente=c.codigo,
                )
            )
            continue

        ficha = candidatas_reconhecidas[0]
        divergente = False

        if ficha.nome and slug(ficha.nome) != slug(c.nome):
            divergente = True
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_NOME_DIVERGENTE",
                    f"nome na ficha ('{ficha.nome}') diverge do nome na matriz "
                    f"('{c.nome}') para '{c.codigo}'.",
                    componente=c.codigo,
                )
            )

        if (
            ficha.carga_horaria
            and ficha.carga_horaria.total is not None
            and c.carga_horaria.total is not None
            and ficha.carga_horaria.total != c.carga_horaria.total
        ):
            divergente = True
            resultado.adicionar(
                ErroValidacao(
                    "FICHA_CARGA_DIVERGENTE",
                    f"carga total na ficha ({ficha.carga_horaria.total}h) diverge da "
                    f"matriz ({c.carga_horaria.total}h) para '{c.codigo}'.",
                    componente=c.codigo,
                )
            )

        preq_ficha = set(ficha.pre_requisitos)
        preq_matriz = {p.codigo for p in c.pre_requisitos if p.codigo}
        if preq_ficha and preq_ficha != preq_matriz:
            divergente = True
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_PREREQUISITOS_DIVERGENTES",
                    f"pré-requisitos na ficha ({sorted(preq_ficha)}) divergem da matriz "
                    f"({sorted(preq_matriz)}) para '{c.codigo}'.",
                    componente=c.codigo,
                )
            )

        for campo in _CAMPOS_TEXTUAIS_OBRIGATORIOS:
            if not getattr(ficha, campo, "").strip():
                resultado.adicionar(
                    AlertaValidacao(
                        "FICHA_CAMPO_VAZIO",
                        f"ficha de '{c.codigo}' não possui '{campo}' preenchido.",
                        componente=c.codigo,
                        campo=campo,
                    )
                )

        situacao.status_por_componente[c.codigo] = (
            StatusFicha.LOCALIZADA_DIVERGENTE if divergente else StatusFicha.LOCALIZADA_CONSISTENTE
        )

    for codigo_ficha in fichas_por_codigo:
        if codigo_ficha not in codigos_matriz:
            situacao.fichas_orfas.append(codigo_ficha)
            resultado.adicionar(
                AlertaValidacao(
                    "FICHA_SEM_COMPONENTE_CORRESPONDENTE",
                    f"ficha '{codigo_ficha}' não corresponde a nenhum componente da "
                    "matriz curricular atual — pode pertencer a um currículo anterior.",
                )
            )

    return resultado, situacao
