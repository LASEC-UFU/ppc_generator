"""Validação do percentual máximo de EaD (Seção 9). O limite não é assumido
pelo código — vem de ``perfil.yaml`` (``curriculo.percentual_maximo_ead``,
em pontos percentuais 0-100), que por sua vez deve refletir a legislação
vigente configurada em ``referenciais/legislacao.yaml``.
"""

from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, componentes_oficiais
from ppcgen.config import Perfil
from ppcgen.modelos import Curriculo, ErroValidacao, ResultadoValidacao


def validar_ead(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    percentual_maximo = perfil.curriculo.percentual_maximo_ead
    if percentual_maximo is None:
        return resultado

    total = carga_horaria_oficial(curriculo, perfil)
    if total == 0:
        return resultado

    # Soma apenas os componentes que contam no total oficial: a repartição
    # de EaD dentro do pool de optativas depende de quais o estudante
    # escolher (ver ppcgen.calculo.carga_horaria_oficial), então não entra aqui.
    carga_ead = sum((c.carga_horaria.ead or 0) for c in componentes_oficiais(curriculo))
    percentual_atual = 100 * carga_ead / total

    if percentual_atual > percentual_maximo:
        resultado.adicionar(
            ErroValidacao(
                "EAD_ACIMA_DO_MAXIMO",
                f"carga em EaD é {percentual_atual:.1f}% da carga total "
                f"({carga_ead}h de {total}h), acima do máximo configurado de "
                f"{percentual_maximo:.1f}%.",
            )
        )
    return resultado
