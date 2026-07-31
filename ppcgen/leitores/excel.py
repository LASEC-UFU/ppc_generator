"""Leitura da matriz curricular oficial (``dados/matriz_curricular.xlsx``).

Esquema de abas adotado (documentado em ``docs/DICIONARIO_DADOS.md``):

1. ``Componentes``   — todos os componentes do curso (obrigatórios,
   optativos pré-aprovados, extensão, estágio, TCC, AAC...), diferenciados
   pelo campo ``tipo`` — não por prefixo/sufixo de código. Pré-requisitos,
   correquisitos, áreas, temas transversais, conteúdos e competências de
   cada componente são colunas desta própria aba (listas separadas por
   vírgula), não abas de junção separadas — ver ``_lista_ids``/
   ``_parse_prerequisitos``/``_parse_correquisitos`` abaixo para a sintaxe
   exata.
2. ``Equivalencias`` — codigo_origem -> codigo_destino.
3. ``Nucleos``       — catálogo de núcleos curriculares (id, nome, descrição).
4. ``Areas``         — catálogo de áreas de formação (id, nome, descrição).
5. ``Temas``         — catálogo de temas transversais (id, nome, descrição,
   fonte normativa, status).
6. ``Conteudos``     — catálogo de conteúdos curriculares exigidos por
   alguma DCN (id, descrição, obrigatório, fonte).
7. ``Certificacoes`` — opcional: certificacao_id -> codigo_componente (0+).

Núcleo é uma coluna direta em ``Componentes`` (cardinalidade 1). Os
catálogos de legislação e competências não vivem na matriz — são
``perfil.legislacao``/``perfil.competencias``, direto em ``perfil.yaml``
(``ppcgen.config``), porque não são dados curriculares por componente. Não
há mais aba ``Curso``: a versão curricular é ``perfil.info.versao`` (Seção
sobre fontes únicas em ``docs/DICIONARIO_DADOS.md``) — outras abas que a
planilha tenha (ex.: um fluxograma visual próprio de cada curso) não fazem
parte deste esquema e não são lidas por este módulo.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

from ppcgen.excecoes import ArquivoNaoEncontrado, FormatoInvalido
from ppcgen.modelos import (
    AreaFormacao,
    CargaHoraria,
    ComponenteCurricular,
    Conteudo,
    Correquisito,
    Curriculo,
    Equivalencia,
    NucleoCurricular,
    PreRequisito,
    ReferenciaisCurso,
    TemaTransversal,
    TipoComponente,
)

ABAS_OBRIGATORIAS = ("Componentes",)
ABAS_OPCIONAIS = (
    "Equivalencias",
    "Nucleos",
    "Areas",
    "Temas",
    "Conteudos",
    "Certificacoes",
)

_SUFIXO_OPCIONAL = "(opcional)"


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


def _lista_ids(valor) -> list[str]:
    """Split de uma célula com IDs separados por vírgula (usada para áreas,
    temas, conteúdos e competências) — células vazias viram lista vazia,
    nunca ``[""]``."""

    texto = _str_ou_vazio(valor)
    if not texto:
        return []
    return [item.strip() for item in texto.split(",") if item.strip()]


def _extrair_opcional(item: str) -> tuple[str, bool]:
    """Separa o sufixo `` (opcional)`` (case-insensitive) de um item de
    pré-requisito/correquisito. Não usa ``?`` como marcador porque códigos
    de componente já podem legitimamente conter ``?`` (Seção sobre
    ``CODIGO_PROVISORIO`` em ``docs/VALIDACOES.md``)."""

    if item.lower().endswith(_SUFIXO_OPCIONAL):
        return item[: -len(_SUFIXO_OPCIONAL)].strip(), True
    return item, False


def _parse_correquisitos(valor) -> list[Correquisito]:
    correquisitos = []
    for item in _lista_ids(valor):
        codigo, opcional = _extrair_opcional(item)
        correquisitos.append(Correquisito(codigo=codigo, opcional=opcional))
    return correquisitos


def _parse_prerequisitos(valor) -> list[PreRequisito]:
    """Cada item é um código de componente (com sufixo opcional `` (opcional)``)
    ou uma exigência de carga horária mínima acumulada, escrita
    ``>=NNNh`` (nunca um código mágico como ``"*"`` — ver
    ``ppcgen.validadores.prerequisitos``). Exemplo de célula:
    ``CTR401, CTR203 (opcional), >=1200h``."""

    pre_requisitos = []
    for item in _lista_ids(valor):
        if item.replace(" ", "").upper().startswith(">="):
            carga_texto = item.split(">=", 1)[1].strip().rstrip("hH").strip()
            pre_requisitos.append(
                PreRequisito(codigo="", carga_horaria_minima=_int_ou_none(carga_texto))
            )
            continue
        codigo, opcional = _extrair_opcional(item)
        pre_requisitos.append(PreRequisito(codigo=codigo, opcional=opcional))
    return pre_requisitos


def carregar_registros_referenciais(wb) -> ReferenciaisCurso:
    """Lê os catálogos de núcleos/áreas/temas/conteúdos das abas de registro
    da própria matriz (``Nucleos``/``Areas``/``Temas``/``Conteudos``) —
    substitui os antigos ``referenciais/*.yaml``. Retorna um
    :class:`ReferenciaisCurso` só com esses quatro campos preenchidos;
    ``legislacao``/``competencias`` vêm de ``perfil.yaml``, não daqui."""

    referenciais = ReferenciaisCurso()

    if "Nucleos" in wb.sheetnames:
        for row in _linhas(wb["Nucleos"]):
            id_ = _str_ou_vazio(row.get("id"))
            if id_:
                referenciais.nucleos.append(
                    NucleoCurricular(
                        id=id_,
                        nome=_str_ou_vazio(row.get("nome")),
                        descricao=_str_ou_vazio(row.get("descricao")),
                    )
                )

    if "Areas" in wb.sheetnames:
        for row in _linhas(wb["Areas"]):
            id_ = _str_ou_vazio(row.get("id"))
            if id_:
                referenciais.areas.append(
                    AreaFormacao(
                        id=id_,
                        nome=_str_ou_vazio(row.get("nome")),
                        descricao=_str_ou_vazio(row.get("descricao")),
                    )
                )

    if "Temas" in wb.sheetnames:
        for row in _linhas(wb["Temas"]):
            id_ = _str_ou_vazio(row.get("id"))
            if id_:
                referenciais.temas_transversais.append(
                    TemaTransversal(
                        id=id_,
                        nome=_str_ou_vazio(row.get("nome")),
                        descricao=_str_ou_vazio(row.get("descricao")),
                        fonte_normativa=_str_ou_vazio(row.get("fonte_normativa")),
                        status=_str_ou_vazio(row.get("status")) or "ativo",
                    )
                )

    if "Conteudos" in wb.sheetnames:
        for row in _linhas(wb["Conteudos"]):
            id_ = _str_ou_vazio(row.get("id"))
            if id_:
                referenciais.conteudos.append(
                    Conteudo(
                        id=id_,
                        descricao=_str_ou_vazio(row.get("descricao")),
                        obrigatorio=_bool(row.get("obrigatorio")),
                        fonte=_str_ou_vazio(row.get("fonte")),
                    )
                )

    return referenciais


def carregar_matriz(caminho: str | Path) -> tuple[Curriculo, ReferenciaisCurso, list[str]]:
    """Lê a matriz curricular e retorna ``(Curriculo, referenciais,
    avisos_leitura)``.

    ``Curriculo.versao`` vem em branco daqui — a versão curricular é
    ``perfil.info.versao`` (já existe em ``perfil.yaml``; não duplicamos o
    dado numa aba ``Curso`` separada). Quem chama com um ``Perfil`` em mãos
    deve fazer ``curriculo.versao = perfil.info.versao`` depois de carregar.

    ``referenciais`` traz só núcleos/áreas/temas/conteúdos (das abas de
    registro da própria matriz) — quem chama ainda precisa preencher
    ``legislacao``/``competencias`` a partir de ``perfil.yaml``.

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

    # ``componentes`` preserva TODAS as linhas, mesmo com código repetido —
    # um dict aqui (codigo -> componente) apagaria silenciosamente a
    # primeira ocorrência de um código duplicado, exatamente o tipo de
    # perda silenciosa que este projeto proíbe (Seção 29). Duplicatas reais
    # são responsabilidade de ``CODIGO_DUPLICADO``
    # (``ppcgen.validadores.codigos``), não do leitor.
    componentes: list[ComponenteCurricular] = []
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
            areas=_lista_ids(row.get("areas")),
            competencias=_lista_ids(row.get("competencias")),
            conteudos=_lista_ids(row.get("conteudos")),
            temas_transversais=_lista_ids(row.get("temas")),
            pre_requisitos=_parse_prerequisitos(row.get("pre_requisitos")),
            correquisitos=_parse_correquisitos(row.get("correquisitos")),
            unidade_oferta=_str_ou_vazio(row.get("unidade_oferta")),
            observacoes=_str_ou_vazio(row.get("observacoes")),
        )
        componentes.append(componente)

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

    referenciais = carregar_registros_referenciais(wb)

    curriculo = Curriculo(
        versao="",
        componentes=componentes,
        equivalencias=equivalencias,
    )
    return curriculo, referenciais, avisos
