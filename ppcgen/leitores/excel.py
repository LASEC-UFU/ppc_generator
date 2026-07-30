"""Leitura da matriz curricular oficial (``dados/matriz_curricular.xlsx``).

Esquema de abas adotado (documentado em ``docs/DICIONARIO_DADOS.md``):

1. ``Curso``            — metadados da versão curricular (chave/valor).
2. ``Componentes``      — todos os componentes do curso (obrigatórios,
   optativos pré-aprovados, extensão, estágio, TCC, AAC...), diferenciados
   pelo campo ``tipo`` — não por prefixo/sufixo de código.
3. ``Pre-requisitos``   — tabela de junção codigo_componente -> pré-requisito.
4. ``Correquisitos``    — tabela de junção codigo_componente -> correquisito.
5. ``Equivalencias``    — codigo_origem -> codigo_destino.
6. ``Areas``            — tabela de junção codigo_componente -> area_id (0+).
7. ``Temas``            — tabela de junção codigo_componente -> tema_id (0+).
8. ``Competencias``     — tabela de junção codigo_componente -> competencia_id (0+).
9. ``Certificacoes``    — opcional: certificacao_id -> codigo_componente (0+).

Núcleo é uma coluna direta em ``Componentes`` (cardinalidade 1) e optativas
pré-aprovadas são apenas componentes com ``tipo=carga_optativa`` — evitando
abas redundantes com a mesma informação em formatos diferentes.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

from ppcgen.excecoes import ArquivoNaoEncontrado, FormatoInvalido
from ppcgen.modelos import (
    CargaHoraria,
    ComponenteCurricular,
    Correquisito,
    Curriculo,
    Equivalencia,
    PreRequisito,
    TipoComponente,
)

ABAS_OBRIGATORIAS = ("Curso", "Componentes")
ABAS_OPCIONAIS = (
    "Pre-requisitos",
    "Correquisitos",
    "Equivalencias",
    "Areas",
    "Temas",
    "Competencias",
    "Conteudos",
    "Certificacoes",
)


def _linhas(planilha) -> list[dict]:
    """Converte uma planilha (com cabeçalho na 1ª linha) em lista de dicts."""

    linhas = list(planilha.iter_rows(values_only=True))
    if not linhas:
        return []
    cabecalho = [str(c).strip() if c is not None else "" for c in linhas[0]]
    resultado = []
    for linha in linhas[1:]:
        if all(v is None for v in linha):
            continue
        resultado.append(dict(zip(cabecalho, linha)))
    return resultado


def _bool(valor, padrao: bool = False) -> bool:
    if valor is None or valor == "":
        return padrao
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().upper() in {"TRUE", "VERDADEIRO", "1", "SIM"}


def _int_ou_none(valor) -> int | None:
    if valor is None or valor == "":
        return None
    return int(valor)


def _str_ou_vazio(valor) -> str:
    return "" if valor is None else str(valor).strip()


def _tipo_componente(valor) -> TipoComponente:
    valor = _str_ou_vazio(valor).lower() or "disciplina"
    try:
        return TipoComponente(valor)
    except ValueError as exc:
        validos = ", ".join(t.value for t in TipoComponente)
        raise FormatoInvalido(
            f"Tipo de componente inválido: '{valor}'. Valores aceitos: {validos}"
        ) from exc


def carregar_matriz(caminho: str | Path) -> tuple[Curriculo, dict, list[str]]:
    """Lê a matriz curricular e retorna ``(Curriculo, metadados_curso, avisos_leitura)``.

    ``avisos_leitura`` registra situações que o leitor não deve "corrigir"
    silenciosamente (ex.: célula de status ativo/inativo em branco) — cabe ao
    validador (Seção 9) decidir a severidade de cada uma.
    """

    caminho = Path(caminho)
    if not caminho.exists():
        raise ArquivoNaoEncontrado(f"Matriz curricular não encontrada: {caminho}")

    wb = openpyxl.load_workbook(caminho, data_only=True)
    for aba in ABAS_OBRIGATORIAS:
        if aba not in wb.sheetnames:
            raise FormatoInvalido(f"Aba obrigatória ausente na matriz: '{aba}'")

    avisos: list[str] = []
    metadados = {
        row.get("campo"): row.get("valor") for row in _linhas(wb["Curso"]) if row.get("campo")
    }

    # ``componentes`` preserva TODAS as linhas, mesmo com código repetido —
    # um dict aqui (codigo -> componente) apagaria silenciosamente a
    # primeira ocorrência de um código duplicado, exatamente o tipo de
    # perda silenciosa que este projeto proíbe (Seção 29). Duplicatas reais
    # são responsabilidade de ``CODIGO_DUPLICADO``
    # (``ppcgen.validadores.codigos``), não do leitor. ``por_codigo`` é só
    # um índice auxiliar para anexar as abas de junção abaixo — em caso de
    # código duplicado, a última ocorrência na planilha "vence" para fins
    # de anexação (pré-requisito/área/tema/...), mas ambos os componentes
    # continuam presentes em ``componentes``.
    componentes: list[ComponenteCurricular] = []
    por_codigo: dict[str, ComponenteCurricular] = {}
    for row in _linhas(wb["Componentes"]):
        codigo = _str_ou_vazio(row.get("codigo"))
        if not codigo:
            continue
        if row.get("ativo") is None or row.get("ativo") == "":
            avisos.append(
                f"{codigo}: coluna 'ativo' em branco na aba Componentes — assumido "
                "ativo=True; defina explicitamente TRUE/FALSE."
            )
        componente = ComponenteCurricular(
            codigo=codigo,
            nome=_str_ou_vazio(row.get("nome")),
            tipo=_tipo_componente(row.get("tipo")),
            carga_horaria=CargaHoraria(
                teorica=_int_ou_none(row.get("cht")),
                pratica=_int_ou_none(row.get("chp")),
                ead=_int_ou_none(row.get("chd")),
                extensao=_int_ou_none(row.get("che")),
                total=_int_ou_none(row.get("tot")),
            ),
            periodo=_int_ou_none(row.get("periodo")),
            ativo=_bool(row.get("ativo"), padrao=True),
            obrigatorio=_bool(row.get("obrigatorio")),
            codigo_provisorio=_bool(row.get("codigo_provisorio")),
            nucleo=_str_ou_vazio(row.get("nucleo_id")) or None,
            unidade_oferta=_str_ou_vazio(row.get("unidade_oferta")),
            ementa=_str_ou_vazio(row.get("ementa")),
            observacoes=_str_ou_vazio(row.get("observacoes")),
        )
        componentes.append(componente)
        por_codigo[codigo] = componente

    if "Pre-requisitos" in wb.sheetnames:
        for row in _linhas(wb["Pre-requisitos"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            comp.pre_requisitos.append(
                PreRequisito(
                    codigo=_str_ou_vazio(row.get("codigo_prerequisito")),
                    opcional=_bool(row.get("opcional")),
                    carga_horaria_minima=_int_ou_none(row.get("carga_horaria_minima")),
                )
            )

    if "Correquisitos" in wb.sheetnames:
        for row in _linhas(wb["Correquisitos"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            comp.correquisitos.append(
                Correquisito(
                    codigo=_str_ou_vazio(row.get("codigo_correquisito")),
                    opcional=_bool(row.get("opcional")),
                )
            )

    if "Areas" in wb.sheetnames:
        for row in _linhas(wb["Areas"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            area_id = _str_ou_vazio(row.get("area_id"))
            if area_id:
                comp.areas.append(area_id)

    if "Temas" in wb.sheetnames:
        for row in _linhas(wb["Temas"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            tema_id = _str_ou_vazio(row.get("tema_id"))
            if tema_id:
                comp.temas_transversais.append(tema_id)

    if "Competencias" in wb.sheetnames:
        for row in _linhas(wb["Competencias"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            competencia_id = _str_ou_vazio(row.get("competencia_id"))
            if competencia_id:
                comp.competencias.append(competencia_id)

    if "Conteudos" in wb.sheetnames:
        for row in _linhas(wb["Conteudos"]):
            comp = por_codigo.get(_str_ou_vazio(row.get("codigo_componente")))
            if comp is None:
                continue
            conteudo_id = _str_ou_vazio(row.get("conteudo_id"))
            if conteudo_id:
                comp.conteudos.append(conteudo_id)

    equivalencias = []
    if "Equivalencias" in wb.sheetnames:
        for row in _linhas(wb["Equivalencias"]):
            origem = _str_ou_vazio(row.get("codigo_origem"))
            destino = _str_ou_vazio(row.get("codigo_destino"))
            if origem and destino:
                equivalencias.append(
                    Equivalencia(
                        codigo_origem=origem,
                        codigo_destino=destino,
                        observacao=_str_ou_vazio(row.get("observacao")),
                    )
                )

    versao = _str_ou_vazio(metadados.get("versao_curricular")) or "sem-versao"
    curriculo = Curriculo(
        versao=versao,
        componentes=componentes,
        equivalencias=equivalencias,
    )
    return curriculo, metadados, avisos


def carregar_equivalencias(caminho: str | Path) -> list[Equivalencia]:
    """Lê o arquivo dedicado ``equivalencias.xlsx`` de um perfil (mesmo
    esquema da aba ``Equivalencias`` da matriz — ``codigo_origem``,
    ``codigo_destino``, ``observacao``). Complementa, não substitui, uma
    eventual aba ``Equivalencias`` na própria matriz.
    """

    caminho = Path(caminho)
    if not caminho.exists():
        raise ArquivoNaoEncontrado(f"Arquivo de equivalências não encontrado: {caminho}")

    wb = openpyxl.load_workbook(caminho, data_only=True)
    planilha = wb[wb.sheetnames[0]]
    equivalencias = []
    for row in _linhas(planilha):
        origem = _str_ou_vazio(row.get("codigo_origem"))
        destino = _str_ou_vazio(row.get("codigo_destino"))
        if origem and destino:
            equivalencias.append(
                Equivalencia(
                    codigo_origem=origem,
                    codigo_destino=destino,
                    observacao=_str_ou_vazio(row.get("observacao")),
                )
            )
    return equivalencias
