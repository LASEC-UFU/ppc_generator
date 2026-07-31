"""Validação do percentual máximo de EaD (Seção 9). O limite não é assumido
pelo código — vem de ``perfil.yaml`` (``curriculo.percentual_maximo_ead``,
em pontos percentuais 0-100), que por sua vez deve refletir a legislação
vigente configurada em ``perfil.legislacao`` (``perfil.yaml``).

Cobre dois tipos de verificação, independentes entre si:

1. o percentual de EaD *realizado* na matriz não pode ultrapassar o
   configurado (comparação matriz x ``perfil.yaml``, como antes);
2. o percentual *configurado* não pode ultrapassar o teto legal do
   formato de oferta declarado em ``oferta.formato`` (Decreto nº
   12.456/2025 — comparação ``perfil.yaml`` x lei, independente da
   matriz). ``oferta.formato`` nunca é inferido do percentual — é sempre
   uma decisão explícita do perfil (Seção 6).
"""

from __future__ import annotations

from ppcgen.calculo import carga_horaria_oficial, componentes_oficiais
from ppcgen.config import Perfil
from ppcgen.modelos import AlertaValidacao, Curriculo, ErroValidacao, ResultadoValidacao

# Percentual máximo de EaD permitido por formato de oferta, Decreto nº
# 12.456/2025: presencial exige mínimo 70% presencial (≤30% EaD);
# semipresencial exige mínimo 30% presencial (≤70% EaD); a distância exige
# mínimo 10% presencial (≤90% EaD). O decreto também define pisos de
# atividade síncrona mediada que este projeto ainda não modela por
# componente (ver docs/RELATORIO_AUDITORIA_NORMATIVA.md) — só o teto
# presencial/EaD agregado é verificado aqui.
TETO_EAD_POR_FORMATO = {
    "presencial": 30.0,
    "semipresencial": 70.0,
    "distancia": 90.0,
}


def validar_formato_oferta(perfil: Perfil) -> ResultadoValidacao:
    """Verifica ``oferta.formato``/``oferta.percentual_maximo_ead`` contra o
    teto legal do Decreto nº 12.456/2025 — não depende da matriz."""

    resultado = ResultadoValidacao()
    formato = perfil.oferta.formato

    if formato not in TETO_EAD_POR_FORMATO:
        resultado.adicionar(
            ErroValidacao(
                "OFERTA_FORMATO_DESCONHECIDO",
                f"oferta.formato '{formato}' não é reconhecido — use um de: "
                f"{', '.join(sorted(TETO_EAD_POR_FORMATO))}.",
            )
        )
        return resultado

    teto = TETO_EAD_POR_FORMATO[formato]
    percentual_maximo = perfil.curriculo.percentual_maximo_ead
    if percentual_maximo is not None and percentual_maximo > teto:
        resultado.adicionar(
            ErroValidacao(
                "EAD_ACIMA_DO_TETO_LEGAL_FORMATO",
                f"curriculo.percentual_maximo_ead configurado ({percentual_maximo:.1f}%) "
                f"excede o teto legal de {teto:.1f}% para oferta.formato='{formato}' "
                "(Decreto nº 12.456/2025).",
            )
        )

    if perfil.oferta.possui_carga_ead and perfil.oferta.status_validacao_institucional == "pendente":
        resultado.adicionar(
            AlertaValidacao(
                "OFERTA_SEM_NORMA_INSTITUCIONAL_CONFIRMADA",
                "oferta.possui_carga_ead=true mas oferta.status_validacao_institucional "
                "ainda é 'pendente' — confirme com a UFU (CONGRAD) antes de considerar "
                "este PPC pronto para submissão.",
            )
        )

    return resultado


def validar_ead(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    resultado.mesclar(validar_formato_oferta(perfil))

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
