"""Validação do percentual mínimo de extensão (Seção 9 / Resolução CNE/CES
nº 7/2018, quando configurada como referencial do perfil — ver
``perfil.legislacao`` em ``perfil.yaml``; este módulo não assume nenhum
percentual por si, apenas aplica o que estiver em ``perfil.yaml``).
"""

from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, carga_por_tipo
from ppcgen.config import Perfil
from ppcgen.modelos import Curriculo, ErroValidacao, ResultadoValidacao, TipoComponente


def validar_extensao(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    percentual_minimo = perfil.curriculo.percentual_minimo_extensao
    if percentual_minimo is None:
        return resultado

    total = carga_horaria_oficial(curriculo, perfil)
    if total == 0:
        return resultado

    carga_extensao = carga_por_tipo(curriculo, TipoComponente.EXTENSAO)
    percentual_atual = 100 * carga_extensao / total

    if percentual_atual < percentual_minimo:
        resultado.adicionar(
            ErroValidacao(
                "EXTENSAO_ABAIXO_DO_MINIMO",
                f"carga de extensão é {percentual_atual:.1f}% da carga total "
                f"({carga_extensao}h de {total}h), abaixo do mínimo configurado de "
                f"{percentual_minimo:.1f}%.",
            )
        )
    return resultado
