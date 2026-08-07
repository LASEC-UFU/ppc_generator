"""Validações de carga horária (Seção 9 — CARGA HORÁRIA).

Cobre não-negatividade, consistência interna (parcelas x total) e as cargas
mínimas configuráveis (total do curso, optativas, AAC, estágio, TCC). Os
percentuais de EaD e de extensão têm módulos dedicados
(:mod:`ppcgen.validadores.ead` e :mod:`ppcgen.validadores.extensao`) porque
combinam carga horária com regras percentuais próprias.
"""

from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, carga_optativa_minima, carga_por_tipo, eh_agregador_optativo
from ppcgen.config import Perfil
from ppcgen.modelos import (
    AlertaValidacao,
    Curriculo,
    ErroValidacao,
    ResultadoValidacao,
    TipoComponente,
)


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
    total_calculado = carga_horaria_oficial(curriculo)
    if cfg.carga_horaria_total is not None and total_calculado != cfg.carga_horaria_total:
        resultado.adicionar(
            ErroValidacao(
                "CARGA_TOTAL_CURSO_DIVERGENTE",
                f"carga horária total calculada a partir da matriz ({total_calculado}h) "
                f"difere da configurada na aba Perfil ({cfg.carga_horaria_total}h).",
            )
        )

    # O componente agregador ("MÓDULO OPTATIVO") pode estar ativo=True ou
    # False — o campo `ativo` não é o que o distingue de uma disciplina
    # cursável, é o **nome** (ppcgen.calculo.eh_agregador_optativo). Por
    # isso ele é excluído por nome tanto de `componentes_oficiais`
    # (ppcgen.calculo) quanto da soma do pool real abaixo,
    # independentemente do seu `ativo`/`tipo` — nenhum dos dois evita que
    # ele seja contado (uma única vez) como a carga horária optativa
    # mínima do curso, via ppcgen.calculo.carga_optativa_minima.
    agregadores = [c for c in curriculo.ativos() if eh_agregador_optativo(c.nome)]
    optativas_ativas = [
        c for c in curriculo.ativos() if c.tipo == TipoComponente.CARGA_OPTATIVA
    ]
    soma_optativas = sum(
        c.carga_total for c in optativas_ativas if c not in agregadores
    )
    minima_configurada = carga_optativa_minima(curriculo)
    if minima_configurada is not None and soma_optativas < minima_configurada:
        resultado.adicionar(
            ErroValidacao(
                "POOL_OPTATIVAS_INSUFICIENTE",
                f"pool de componentes optativos oferece apenas {soma_optativas}h, "
                f"insuficiente para o mínimo exigido de {minima_configurada}h.",
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
