"""Validações de pré-requisitos e correquisitos, incluindo detecção de ciclos
(Seções 9 e 10).

Pré-requisitos por carga horária mínima (ex.: "só pode cursar Estágio após
integralizar 1875h") são modelados explicitamente por
:attr:`~ppcgen.modelos.PreRequisito.carga_horaria_minima` — nunca por um
código mágico como ``"*"``, que o script legado usava.
"""

from __future__ import annotations

from ppcgen.config import Perfil
from ppcgen.modelos import (
    AlertaValidacao,
    ComponenteCurricular,
    Curriculo,
    ErroValidacao,
    ResultadoValidacao,
)


def construir_grafo_prerequisitos(curriculo: Curriculo) -> dict[str, list[str]]:
    """Grafo dirigido código -> lista de códigos de pré-requisito (reais)."""

    codigos_validos = {c.codigo for c in curriculo.componentes}
    grafo: dict[str, list[str]] = {c.codigo: [] for c in curriculo.componentes}
    for c in curriculo.componentes:
        for preq in c.pre_requisitos:
            if preq.codigo and preq.codigo in codigos_validos:
                grafo[c.codigo].append(preq.codigo)
    return grafo


def detectar_ciclos(grafo: dict[str, list[str]]) -> list[list[str]]:
    """Retorna os ciclos encontrados, cada um como a lista de códigos no caminho."""

    ESTADO_NAO_VISITADO, ESTADO_EM_PROGRESSO, ESTADO_CONCLUIDO = 0, 1, 2
    estado = dict.fromkeys(grafo, ESTADO_NAO_VISITADO)
    ciclos: list[list[str]] = []

    def dfs(no: str, caminho: list[str]) -> None:
        estado[no] = ESTADO_EM_PROGRESSO
        caminho.append(no)
        for vizinho in grafo.get(no, []):
            if estado.get(vizinho) == ESTADO_EM_PROGRESSO:
                inicio = caminho.index(vizinho)
                ciclos.append(caminho[inicio:] + [vizinho])
            elif estado.get(vizinho) == ESTADO_NAO_VISITADO:
                dfs(vizinho, caminho)
        caminho.pop()
        estado[no] = ESTADO_CONCLUIDO

    for no in grafo:
        if estado[no] == ESTADO_NAO_VISITADO:
            dfs(no, [])
    return ciclos


def validar_equivalencias(curriculo: Curriculo) -> ResultadoValidacao:
    """Confere se cada par de ``curriculo.equivalencias`` referencia códigos
    reais — um alerta, não um erro, pois o lado "origem" costuma ser um
    componente de um currículo anterior, que não precisa estar (e
    tipicamente não está) na matriz atual (Seção 23: migração sem perda)."""

    resultado = ResultadoValidacao()
    por_codigo = curriculo.por_codigo()
    for equivalencia in curriculo.equivalencias:
        if equivalencia.codigo_destino not in por_codigo:
            resultado.adicionar(
                AlertaValidacao(
                    "EQUIVALENCIA_DESTINO_INEXISTENTE",
                    f"equivalência '{equivalencia.codigo_origem}' -> "
                    f"'{equivalencia.codigo_destino}' aponta para um código que não "
                    "foi localizado na matriz curricular atual.",
                )
            )
        origem = por_codigo.get(equivalencia.codigo_origem)
        if origem is not None and origem.ativo:
            resultado.adicionar(
                AlertaValidacao(
                    "EQUIVALENCIA_ORIGEM_AINDA_ATIVA",
                    f"'{equivalencia.codigo_origem}' está registrada como equivalente a "
                    f"'{equivalencia.codigo_destino}', mas ainda está ativa na matriz "
                    "curricular atual — confirme se a equivalência é intencional (ex.: "
                    "equivalência entre disciplinas de outras unidades, não uma "
                    "substituição de currículo anterior).",
                )
            )
    return resultado


def validar_prerequisitos(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    por_codigo: dict[str, ComponenteCurricular] = curriculo.por_codigo()

    for c in curriculo.componentes:
        for preq in c.pre_requisitos:
            if preq.codigo == "" and preq.carga_horaria_minima is None:
                resultado.adicionar(
                    ErroValidacao(
                        "PREREQUISITO_MALFORMADO",
                        f"pré-requisito de '{c.codigo}' não informa nem um código nem "
                        "uma carga horária mínima.",
                        componente=c.codigo,
                    )
                )
                continue
            if preq.codigo.startswith("*"):
                resultado.adicionar(
                    ErroValidacao(
                        "PREREQUISITO_CODIGO_MAGICO",
                        f"pré-requisito de '{c.codigo}' usa o código mágico "
                        f"'{preq.codigo}' — modele carga horária mínima explicitamente "
                        "em 'carga_horaria_minima', não como pseudo-código.",
                        componente=c.codigo,
                    )
                )
                continue
            if not preq.codigo:
                continue
            if preq.codigo == c.codigo:
                resultado.adicionar(
                    ErroValidacao(
                        "PREREQUISITO_AUTORREFERENCIA",
                        f"'{c.codigo}' aparece como pré-requisito de si mesmo.",
                        componente=c.codigo,
                    )
                )
                continue
            alvo = por_codigo.get(preq.codigo)
            if alvo is None:
                severidade = AlertaValidacao if preq.opcional else ErroValidacao
                resultado.adicionar(
                    severidade(
                        "PREREQUISITO_INEXISTENTE",
                        f"pré-requisito '{preq.codigo}' de '{c.codigo}' não foi localizado "
                        "na matriz curricular.",
                        componente=c.codigo,
                    )
                )
                continue
            if not alvo.ativo:
                resultado.adicionar(
                    ErroValidacao(
                        "PREREQUISITO_INATIVO",
                        f"pré-requisito '{preq.codigo}' de '{c.codigo}' está marcado "
                        "como inativo.",
                        componente=c.codigo,
                    )
                )
            if (
                c.periodo is not None
                and alvo.periodo is not None
                and alvo.periodo >= c.periodo
            ):
                resultado.adicionar(
                    ErroValidacao(
                        "PREREQUISITO_PERIODO_INVALIDO",
                        f"pré-requisito '{preq.codigo}' ({alvo.periodo}º período) de "
                        f"'{c.codigo}' ({c.periodo}º período) não é ofertado antes.",
                        componente=c.codigo,
                    )
                )

        for creq in c.correquisitos:
            if creq.codigo == c.codigo:
                resultado.adicionar(
                    ErroValidacao(
                        "CORREQUISITO_AUTORREFERENCIA",
                        f"'{c.codigo}' aparece como correquisito de si mesmo.",
                        componente=c.codigo,
                    )
                )
                continue
            alvo = por_codigo.get(creq.codigo)
            if alvo is None:
                severidade = AlertaValidacao if creq.opcional else ErroValidacao
                resultado.adicionar(
                    severidade(
                        "CORREQUISITO_INEXISTENTE",
                        f"correquisito '{creq.codigo}' de '{c.codigo}' não foi localizado "
                        "na matriz curricular.",
                        componente=c.codigo,
                    )
                )
                continue
            if c.periodo is not None and alvo.periodo is not None and alvo.periodo != c.periodo:
                resultado.adicionar(
                    AlertaValidacao(
                        "CORREQUISITO_PERIODO_DIVERGENTE",
                        f"correquisito '{creq.codigo}' ({alvo.periodo}º período) de "
                        f"'{c.codigo}' ({c.periodo}º período) não está no mesmo período.",
                        componente=c.codigo,
                    )
                )

    grafo = construir_grafo_prerequisitos(curriculo)
    ciclos_ja_reportados: set[frozenset] = set()
    for ciclo in detectar_ciclos(grafo):
        assinatura = frozenset(ciclo)
        if assinatura in ciclos_ja_reportados:
            continue
        ciclos_ja_reportados.add(assinatura)
        resultado.adicionar(
            ErroValidacao(
                "CICLO_PREREQUISITOS",
                "ciclo de pré-requisitos detectado: " + " → ".join(ciclo),
            )
        )

    return resultado
