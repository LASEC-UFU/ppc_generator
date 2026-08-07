"""Validação das Ênfases Formativas (áreas de formação optativa) — Seção 9.

A vinculação entre um componente curricular e sua ênfase vem da coluna
``componentes`` da aba ``EnfasesFormativas`` (mesmo padrão de
``Nucleos``/``Areas``/``Temas``/``Competencias``) — ver
``ppcgen.leitores.excel._aplicar_vinculos_catalogo``. As checagens sobre
essa relação (código inexistente, componente reivindicado por mais de uma
ênfase) vivem em ``ppcgen.validadores.referenciais``, junto das checagens
equivalentes dos demais catálogos; este módulo cuida apenas do que é
específico de ênfases: se a carga horária disponível em cada uma é
suficiente para o mínimo configurado na aba ``Perfil``, e se esse mínimo é
alcançável em número suficiente de ênfases.
"""

from __future__ import annotations

from collections import defaultdict

from ppcgen.config import Perfil
from ppcgen.modelos import AlertaValidacao, Curriculo, ErroValidacao, ReferenciaisCurso, ResultadoValidacao


def validar_enfases_formativas(
    curriculo: Curriculo, perfil: Perfil, referenciais: ReferenciaisCurso
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    if not referenciais.enfases_formativas:
        return resultado  # curso não usa o mecanismo (ex.: Tecnólogo) — nada a checar

    ativos = curriculo.ativos()
    carga_por_enfase: dict[str, int] = defaultdict(int)
    for c in ativos:
        for enfase_id in c.enfases_formativas:
            carga_por_enfase[enfase_id] += c.carga_total

    for enfase in referenciais.enfases_formativas:
        if carga_por_enfase.get(enfase.id, 0) == 0:
            resultado.adicionar(
                AlertaValidacao(
                    "ENFASE_FORMATIVA_SEM_COMPONENTES",
                    f"ênfase formativa '{enfase.id}' ({enfase.nome}) não tem nenhum componente "
                    "ativo vinculado na coluna 'componentes' da aba EnfasesFormativas.",
                )
            )

    minimas = perfil.curriculo.enfases_formativas_minimas
    if minimas is None or minimas < 1 or minimas > len(referenciais.enfases_formativas):
        resultado.adicionar(
            ErroValidacao(
                "ENFASES_FORMATIVAS_MINIMAS_INVALIDAS",
                f"curriculo.enfases_formativas_minimas ({minimas}) precisa ser um inteiro entre 1 "
                f"e {len(referenciais.enfases_formativas)} (número de ênfases cadastradas).",
            )
        )
        return resultado  # sem um mínimo válido, as checagens de suficiência abaixo não fazem sentido

    carga_minima = perfil.curriculo.carga_horaria_minima_por_enfase
    if carga_minima is None or carga_minima <= 0:
        resultado.adicionar(
            ErroValidacao(
                "ENFASE_FORMATIVA_CARGA_MINIMA_INVALIDA",
                f"curriculo.carga_horaria_minima_por_enfase ({carga_minima}) precisa ser um número "
                "positivo de horas.",
            )
        )
        return resultado

    enfases_suficientes = 0
    for enfase in referenciais.enfases_formativas:
        disponivel = carga_por_enfase.get(enfase.id, 0)
        if disponivel < carga_minima:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_CARGA_INSUFICIENTE",
                    f"ênfase formativa '{enfase.id}' ({enfase.nome}) tem apenas {disponivel}h de "
                    f"componentes ativos vinculados, insuficiente para o mínimo de {carga_minima}h.",
                )
            )
        else:
            enfases_suficientes += 1

    if enfases_suficientes < minimas:
        resultado.adicionar(
            ErroValidacao(
                "ENFASES_FORMATIVAS_INTEGRALIZACAO_INVIAVEL",
                f"apenas {enfases_suficientes} ênfase(s) formativa(s) têm carga horária suficiente "
                f"({carga_minima}h) — são necessárias, no mínimo, {minimas}.",
            )
        )

    return resultado
