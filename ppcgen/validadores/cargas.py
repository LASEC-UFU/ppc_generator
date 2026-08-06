"""Validações de carga horária (Seção 9 — CARGA HORÁRIA).

Cobre não-negatividade, consistência interna (parcelas x total) e as cargas
mínimas configuráveis (total do curso, optativas, AAC, estágio, TCC). Os
percentuais de EaD e de extensão têm módulos dedicados
(:mod:`ppcgen.validadores.ead` e :mod:`ppcgen.validadores.extensao`) porque
combinam carga horária com regras percentuais próprias.
"""

from __future__ import annotations

import unicodedata

from ppcgen.calculo import carga_horaria_oficial, carga_por_tipo
from ppcgen.config import Perfil
from ppcgen.modelos import (
    AlertaValidacao,
    Curriculo,
    ErroValidacao,
    ResultadoValidacao,
    TipoComponente,
)


def _eh_agregador_optativo(nome: str) -> bool:
    """Identifica linhas-resumo que não representam componentes cursáveis."""

    normalizado = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", nome.casefold())
        if not unicodedata.combining(caractere)
    )
    normalizado = " ".join(normalizado.split())
    return normalizado in {"modulo optativo", "carga optativa", "pool optativo", "bloco optativo"}


def validar_cargas(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()

    for c in curriculo.componentes:
        ch = c.carga_horaria
        for campo, valor in (
            ("cht", ch.teorica),
            ("chp", ch.pratica),
            ("chd", ch.ead),
            ("che", ch.extensao),
            ("tot", ch.total),
        ):
            if valor is not None and valor < 0:
                resultado.adicionar(
                    ErroValidacao(
                        "CARGA_NEGATIVA",
                        f"carga '{campo}' de '{c.codigo}' é negativa ({valor}).",
                        componente=c.codigo,
                        campo=campo,
                    )
                )

        soma = ch.soma_parcelas()
        if soma is not None and ch.total is not None and soma != ch.total:
            resultado.adicionar(
                ErroValidacao(
                    "CARGA_TOTAL_INCONSISTENTE",
                    f"carga total informada de {ch.total}h é diferente da soma das "
                    f"parcelas (CHT+CHP+CHD+CHE = {soma}h) para '{c.codigo}'.",
                    componente=c.codigo,
                    campo="tot",
                )
            )

    cfg = perfil.curriculo
    total_calculado = carga_horaria_oficial(curriculo, perfil)
    if cfg.carga_horaria_total is not None and total_calculado != cfg.carga_horaria_total:
        resultado.adicionar(
            ErroValidacao(
                "CARGA_TOTAL_CURSO_DIVERGENTE",
                f"carga horária total calculada a partir da matriz ({total_calculado}h) "
                f"difere da configurada na aba Perfil ({cfg.carga_horaria_total}h).",
            )
        )

    optativas_ativas = [
        c for c in curriculo.ativos() if c.tipo == TipoComponente.CARGA_OPTATIVA
    ]
    agregadores_optativos = [c for c in optativas_ativas if _eh_agregador_optativo(c.nome)]
    for componente in agregadores_optativos:
        resultado.adicionar(
            ErroValidacao(
                "COMPONENTE_AGREGADOR_OPTATIVO",
                f"'{componente.codigo}' ('{componente.nome}') é uma linha agregadora, "
                "não uma disciplina cursável; cadastre o elenco real de optativas.",
                componente=componente.codigo,
                campo="nome",
            )
        )

    soma_optativas = sum(
        c.carga_total for c in optativas_ativas if c not in agregadores_optativos
    )
    if cfg.carga_optativa_minima is not None and soma_optativas < cfg.carga_optativa_minima:
        resultado.adicionar(
            ErroValidacao(
                "POOL_OPTATIVAS_INSUFICIENTE",
                f"pool de componentes optativos oferece apenas {soma_optativas}h, "
                f"insuficiente para o mínimo exigido de {cfg.carga_optativa_minima}h.",
            )
        )

    for tipo, minimo, rotulo in (
        (TipoComponente.ATIVIDADE_COMPLEMENTAR, cfg.carga_aac, "AAC"),
        (TipoComponente.ESTAGIO, cfg.carga_estagio, "estágio"),
        (TipoComponente.TCC, cfg.carga_tcc, "TCC"),
    ):
        if minimo is None:
            continue
        soma = carga_por_tipo(curriculo, tipo)
        if soma != minimo:
            resultado.adicionar(
                AlertaValidacao(
                    "CARGA_TIPO_DIVERGENTE",
                    f"carga de {rotulo} na matriz ({soma}h) difere da configurada "
                    f"na aba Perfil ({minimo}h).",
                )
            )

    if cfg.carga_horaria_presencial_maxima_periodo is not None:
        cargas_presenciais_por_periodo: dict[int, int] = {}
        for c in curriculo.ativos():
            if c.periodo is None:
                continue
            carga_presencial = (c.carga_horaria.teorica or 0) + (c.carga_horaria.pratica or 0)
            cargas_presenciais_por_periodo[c.periodo] = (
                cargas_presenciais_por_periodo.get(c.periodo, 0) + carga_presencial
            )
        for periodo, carga in sorted(cargas_presenciais_por_periodo.items()):
            if carga > cfg.carga_horaria_presencial_maxima_periodo:
                resultado.adicionar(
                    ErroValidacao(
                        "CARGA_MAXIMA_PERIODO_EXCEDIDA",
                        f"{periodo}º período soma {carga}h de carga presencial (CHT+CHP), "
                        f"acima do máximo configurado de "
                        f"{cfg.carga_horaria_presencial_maxima_periodo}h.",
                    )
                )

    return resultado
