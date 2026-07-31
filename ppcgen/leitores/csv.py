"""Importador de compatibilidade para o CSV legado do curso de Engenharia de
Computação (``py/PPC_disciplinas_final.csv``).

Não é a fonte oficial do novo sistema (essa é ``dados/matriz_curricular.xlsx``
— ver :mod:`ppcgen.leitores.excel`); serve para:

- migrar/comparar os dados antigos sem risco de perda silenciosa (Seção 23);
- alimentar os testes de integração com um conjunto de dados real.

Qualquer informação que não possa ser mapeada com segurança para o novo
modelo é preservada em ``observacoes`` e reportada em ``alertas_migracao``,
nunca descartada ou "corrigida" silenciosamente (Seção 23/29).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from ppcgen.excecoes import ArquivoNaoEncontrado
from ppcgen.modelos import (
    CargaHoraria,
    ComponenteCurricular,
    Correquisito,
    Curriculo,
    PreRequisito,
    TipoComponente,
)

# Mapa histórico usado pelo script legado para "QEXTR" (Seção 7: identificadores
# em vez de números). Documentado aqui apenas para permitir a migração; o
# curso novo não deve reutilizar estes identificadores como se fossem
# universais — cada curso define os seus na aba Temas da própria matriz.
LEGADO_QEXTR_TEMAS: dict[int, str] = {
    2: "RELACOES_ETNICO_RACIAIS",
    3: "LIBRAS",
    4: "DIREITOS_HUMANOS",
    5: "EDUCACAO_AMBIENTAL",
    6: "PREVENCAO_DESASTRES",
}

_MAPA_NUCLEO_LEGADO = {
    "FORM_BAS": "BASICO",
    "FORM_HUM": "HUMANISTICO",
    "FORM_TEC": "TECNOLOGICO",
    "FORM_CMP": "COMPLEMENTAR",
}

_MAPA_AREA_CC2020 = {
    "CC_UO1": "CC2020_USUARIOS_ORGANIZACOES",
    "CC_SM2": "CC2020_MODELAGEM_SISTEMAS",
    "CC_SAI3": "CC2020_ARQUITETURA_INFRAESTRUTURA",
    "CC_SD4": "CC2020_DESENVOLVIMENTO_SOFTWARE",
    "CC_SF5": "CC2020_FUNDAMENTOS_SOFTWARE",
    "CC_HW6": "CC2020_HARDWARE",
}


@dataclass
class ResultadoImportacaoCSV:
    curriculo: Curriculo
    alertas_migracao: list[str] = field(default_factory=list)


def _bool(valor: str) -> bool:
    return (valor or "").strip().upper() == "TRUE"


def _carga(valor: str) -> int | None:
    valor = (valor or "").strip()
    if valor == "" or not valor.lstrip("-").isdigit():
        return None
    numero = int(valor)
    return None if numero < 0 else numero


def carregar_csv_legado(caminho: str | Path) -> ResultadoImportacaoCSV:
    caminho = Path(caminho)
    if not caminho.exists():
        raise ArquivoNaoEncontrado(f"CSV legado não encontrado: {caminho}")

    alertas: list[str] = []
    componentes: list[ComponenteCurricular] = []

    with open(caminho, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f, delimiter=";")
        for linha in leitor:
            codigo = (linha.get("Código") or "").strip()
            nome = (linha.get("Nome") or "").strip()
            if not codigo or not nome:
                continue

            per_bruto = (linha.get("PER") or "").strip()
            periodo: int | None = None
            tipo = TipoComponente.DISCIPLINA
            if per_bruto == "acc":
                tipo = TipoComponente.OUTRO
                alertas.append(
                    f"{codigo}: período 'acc' mapeado para tipo OUTRO — o CSV legado não "
                    "distingue Estágio Supervisionado de TCC nesta linha (ambos eram "
                    "aceitos como alternativas); decisão acadêmica necessária."
                )
            elif per_bruto == "aac":
                tipo = TipoComponente.ATIVIDADE_COMPLEMENTAR
            elif per_bruto == "opt":
                tipo = TipoComponente.CARGA_OPTATIVA
            elif per_bruto.lstrip("-").isdigit() and int(per_bruto) >= 0:
                periodo = int(per_bruto)
            elif per_bruto.lstrip("-").isdigit() and int(per_bruto) < 0:
                # PER negativo (ex.: "-1") era usado no legado para o pool de
                # disciplinas "equivalentes"/optativas pré-aprovadas (FLX=False
                # em py/gen_docs.py) — sem período fixo, não um período -1 real.
                periodo = None
            elif per_bruto:
                alertas.append(
                    f"{codigo}: período '{per_bruto}' não reconhecido — mantido como "
                    "indefinido (None), decisão acadêmica necessária."
                )

            if _bool(linha.get("EXT", "")):
                tipo = TipoComponente.EXTENSAO

            nucleo = None
            nucleos_marcados = [
                destino for origem, destino in _MAPA_NUCLEO_LEGADO.items() if _bool(linha.get(origem, ""))
            ]
            if len(nucleos_marcados) > 1:
                alertas.append(
                    f"{codigo}: múltiplos núcleos marcados ({', '.join(nucleos_marcados)}) — "
                    f"mantido apenas '{nucleos_marcados[0]}', decisão acadêmica necessária."
                )
            if nucleos_marcados:
                nucleo = nucleos_marcados[0]

            areas = [
                destino for origem, destino in _MAPA_AREA_CC2020.items() if _bool(linha.get(origem, ""))
            ]

            preq_bruto = (linha.get("PREQ") or "").strip()
            pre_requisitos = [
                (PreRequisito(codigo="", carga_horaria_minima=-1) if p == "*" else PreRequisito(codigo=p))
                for p in preq_bruto.split("/")
                if p
            ]
            # ``carga_horaria_minima=-1`` acima é um marcador temporário
            # resolvido logo abaixo (fora do loop) para o valor real de
            # "carga mínima integralizada" que o legado computava
            # dinamicamente (ch_req_acc) — nunca chega ao modelo final.
            creq_bruto = (linha.get("CREQ") or "").strip()
            correquisitos = [Correquisito(codigo=c) for c in creq_bruto.split("/") if c]

            temas_transversais = []
            qextr_bruto = (linha.get("QEXTR") or "").strip()
            for valor in qextr_bruto.split("/"):
                if valor.strip().lstrip("-").isdigit() and int(valor) in LEGADO_QEXTR_TEMAS:
                    temas_transversais.append(LEGADO_QEXTR_TEMAS[int(valor)])

            # FLX=False no legado marcava linhas do "pool de
            # equivalências/optativas pré-aprovadas" (Seção 23), somadas à
            # parte pelo script antigo e nunca incluídas na carga horária do
            # curso — o equivalente mais próximo no novo modelo é
            # ativo=False (fora de curriculo.ativos()).
            ativo = (linha.get("FLX") or "True").strip().upper() != "FALSE"

            if (linha.get("DCN_base") or "").strip() or (linha.get("DCN_ecp") or "").strip():
                alertas.append(
                    f"{codigo}: colunas DCN_base/DCN_ecp não migradas — referenciam listas de "
                    "conteúdo específicas da DCN de Computação/CC2020, não aplicáveis a outros "
                    "cursos (Seção 24). Consulte o CSV original se precisar recuperá-las."
                )

            componentes.append(
                ComponenteCurricular(
                    codigo=codigo,
                    nome=nome,
                    tipo=tipo,
                    carga_horaria=CargaHoraria(
                        teorica=_carga(linha.get("CHT", "")),
                        pratica=_carga(linha.get("CHP", "")),
                        ead=_carga(linha.get("CHD", "")),
                        extensao=_carga(linha.get("CHE", "")),
                        total=_carga(linha.get("TOT", "")),
                    ),
                    periodo=periodo,
                    ativo=ativo,
                    obrigatorio=_bool(linha.get("OBR", "")),
                    nucleo=nucleo,
                    areas=areas,
                    temas_transversais=temas_transversais,
                    pre_requisitos=pre_requisitos,
                    correquisitos=correquisitos,
                )
            )

    # Resolve o marcador temporário do pré-requisito "*": o legado calculava
    # dinamicamente a carga mínima para iniciar a Atividade de Conclusão de
    # Curso como a soma da carga obrigatória do 1º ao 5º período
    # (`PER_ACC = 5` em py/gen_docs.py) — reproduzido aqui só para a
    # migração, não como uma regra do sistema novo (cada curso configura seu
    # próprio `periodo_minimo_estagio`/`periodo_minimo_tcc`).
    limite_periodo_acc = 5
    ch_req_acc = sum(
        c.carga_total
        for c in componentes
        if c.obrigatorio and c.periodo is not None and c.periodo <= limite_periodo_acc
    )
    for c in componentes:
        for preq in c.pre_requisitos:
            if preq.codigo == "" and preq.carga_horaria_minima == -1:
                preq.carga_horaria_minima = ch_req_acc

    curriculo = Curriculo(versao="legado-csv", componentes=componentes)
    return ResultadoImportacaoCSV(curriculo=curriculo, alertas_migracao=alertas)
