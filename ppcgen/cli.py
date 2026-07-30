"""Interface de linha de comando do ppcgen (Seção 10/12).

    python -m ppcgen perfis
    python -m ppcgen perfil-info --perfil <id>
    python -m ppcgen perfil-validar --perfil <id>
    python -m ppcgen perfil-criar --id <id> --nome "<nome>"
    python -m ppcgen perfil-clonar --origem <id> --destino <id> [--versao <v>]

    python -m ppcgen validar --perfil <id> | --perfil-dir <caminho>
    python -m ppcgen validar-fichas --perfil <id>
    python -m ppcgen gerar --perfil <id>
    python -m ppcgen compilar --perfil <id>
    python -m ppcgen completo --perfil <id>
    python -m ppcgen comparar --anterior <matriz.xlsx> --atual <matriz.xlsx>
    python -m ppcgen limpar --perfil <id> | --todos

    python -m ppcgen validar-todos [--status <status>]
    python -m ppcgen gerar-todos [--status <status>]
    python -m ppcgen completo-todos [--status <status>]

A geração NUNCA presume um curso (Seção 10): todo comando que opera sobre um
único perfil exige ``--perfil`` ou ``--perfil-dir`` explícitos, exceto pela
conveniência local opcional e não-oficial de ``.ppcgen.local.yaml``
(Seção 18 — nunca usada em `*-todos`, testes ou CI).

Retorna código de saída diferente de zero sempre que houver erro crítico.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

import ppcgen.perfis as perfis_mod
from ppcgen.compiladores.latex import compilar_pdf, montar_arvore_latex, montar_pdf_completo
from ppcgen.config import Perfil
from ppcgen.excecoes import ConfiguracaoInvalida, PPCGenError
from ppcgen.geradores.comparacao import (
    comparar_curriculos,
    gerar_relatorio_comparacao_html,
    gerar_relatorio_comparacao_json,
)
from ppcgen.geradores.latex import gerar_arquivos_latex
from ppcgen.geradores.relatorios import (
    gerar_relatorio_html,
    gerar_relatorio_json,
    imprimir_resumo_terminal,
)
from ppcgen.leitores.excel import carregar_equivalencias, carregar_matriz
from ppcgen.leitores.fichas import carregar_fichas
from ppcgen.leitores.yaml import ReferenciaisCurso, carregar_referenciais_curso
from ppcgen.modelos import Curriculo, TipoComponente
from ppcgen.scaffolding import clonar_perfil, criar_perfil
from ppcgen.utilitarios.caminhos import raiz_projeto
from ppcgen.utilitarios.logging import configurar, obter_logger
from ppcgen.validadores.curriculo import validar_curriculo
from ppcgen.validadores.perfil import validar_perfil

logger = obter_logger(__name__)


# ---------------------------------------------------------------------------
# Resolução do perfil selecionado
# ---------------------------------------------------------------------------


def _perfil_padrao_local() -> str | None:
    caminho = raiz_projeto() / ".ppcgen.local.yaml"
    if not caminho.exists():
        return None
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    return dados.get("perfil_padrao")


def _resolver_perfil(args: argparse.Namespace) -> Perfil:
    perfil_dir = getattr(args, "perfil_dir", None)
    perfil_id = getattr(args, "perfil", None)
    if perfil_dir:
        return perfis_mod.carregar(perfil_dir=perfil_dir)
    if perfil_id:
        return perfis_mod.carregar(perfil_id=perfil_id)

    padrao = _perfil_padrao_local()
    if padrao:
        logger.warning(
            "Nenhum --perfil informado; usando perfil padrão local '%s' "
            "(.ppcgen.local.yaml). Em operações oficiais, informe --perfil "
            "explicitamente (Seção 18).",
            padrao,
        )
        return perfis_mod.carregar(perfil_id=padrao)

    raise ConfiguracaoInvalida(
        "Informe --perfil <id> ou --perfil-dir <caminho>. Nenhum perfil padrão "
        "está configurado em .ppcgen.local.yaml."
    )


def _pasta_saida_perfil(perfil: Perfil) -> Path:
    return raiz_projeto() / "saida" / perfil.info.id


# ---------------------------------------------------------------------------
# Contexto de dados (matriz + referenciais + fichas)
# ---------------------------------------------------------------------------


def _carregar_contexto(perfil: Perfil) -> tuple[Curriculo, ReferenciaisCurso, list[str]]:
    caminho_matriz = perfil.resolver_arquivo(perfil.arquivos.matriz)
    if caminho_matriz is None:
        raise ConfiguracaoInvalida(
            f"Matriz curricular '{perfil.arquivos.matriz}' não encontrada no perfil "
            f"'{perfil.info.id}' (nem no perfil base, se houver)."
        )
    curriculo, _metadados, avisos = carregar_matriz(caminho_matriz)
    caminho_equivalencias = perfil.resolver_arquivo(perfil.arquivos.equivalencias)
    if caminho_equivalencias is not None:
        curriculo.equivalencias.extend(carregar_equivalencias(caminho_equivalencias))
    pasta_referenciais = perfil.diretorio / perfil.arquivos.referenciais
    referenciais = carregar_referenciais_curso(pasta_referenciais)
    if perfil.perfil_base is not None:
        referenciais = _mesclar_referenciais(
            carregar_referenciais_curso(perfil.perfil_base.diretorio / perfil.perfil_base.arquivos.referenciais),
            referenciais,
        )
    referenciais = _acrescentar_legislacao_compartilhada(perfil, referenciais)
    return curriculo, referenciais, avisos


def _acrescentar_legislacao_compartilhada(perfil: Perfil, referenciais: ReferenciaisCurso) -> ReferenciaisCurso:
    """Acrescenta ao catálogo os referenciais legais compartilhados
    declarados em ``heranca.legislacao`` (Seção 8) — não sobrescreve os do
    perfil, apenas complementa (por id)."""

    from ppcgen.leitores.yaml import carregar_referenciais_legais

    if not perfil.heranca.legislacao:
        return referenciais
    ids_existentes = {r.id for r in referenciais.legislacao}
    adicionais = []
    for caminho_rel in perfil.heranca.legislacao:
        caminho = perfil.caminho_compartilhado(caminho_rel)
        for referencial in carregar_referenciais_legais(caminho):
            if referencial.id not in ids_existentes:
                adicionais.append(referencial)
                ids_existentes.add(referencial.id)
    referenciais.legislacao.extend(adicionais)
    return referenciais


def _mesclar_referenciais(base: ReferenciaisCurso, atual: ReferenciaisCurso) -> ReferenciaisCurso:
    """Perfil derivado herda o catálogo do perfil base; entradas com o mesmo
    id no perfil atual sobrescrevem as do base (Seção 9)."""

    def _merge(lista_base, lista_atual):
        por_id = {item.id: item for item in lista_base}
        for item in lista_atual:
            por_id[item.id] = item
        return list(por_id.values())

    return ReferenciaisCurso(
        nucleos=_merge(base.nucleos, atual.nucleos),
        areas=_merge(base.areas, atual.areas),
        competencias=_merge(base.competencias, atual.competencias),
        conteudos=_merge(base.conteudos, atual.conteudos),
        legislacao=_merge(base.legislacao, atual.legislacao),
        temas_transversais=_merge(base.temas_transversais, atual.temas_transversais),
    )


def _carregar_fichas_do_perfil(perfil: Perfil) -> list:
    """Carrega fichas priorizando obrigatórias/optativas/... do perfil atual
    e, para o que faltar, do perfil base (Seção 9 — herança de fichas)."""

    por_codigo: dict = {}
    cadeia = []
    atual: Perfil | None = perfil
    while atual is not None:
        cadeia.append(atual)
        atual = atual.perfil_base
    for p in reversed(cadeia):
        pasta_fichas = p.diretorio / p.arquivos.fichas
        for sub in ("obrigatorias", "optativas", "extensao", "tcc", "estagio", "complementares"):
            for ficha in carregar_fichas(pasta_fichas / sub):
                por_codigo[ficha.codigo] = ficha
    return list(por_codigo.values())


def _gravar_relatorios_validacao(perfil: Perfil, resultado, situacao_fichas) -> None:
    pasta_relatorios = _pasta_saida_perfil(perfil) / "relatorios"
    if perfil.geracao.gerar_relatorio_validacao:
        gerar_relatorio_html(resultado, pasta_relatorios / "validacao.html", situacao_fichas)
        gerar_relatorio_json(resultado, pasta_relatorios / "validacao.json", situacao_fichas)


# ---------------------------------------------------------------------------
# Comandos de perfil único
# ---------------------------------------------------------------------------


def cmd_validar(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)

    resultado_perfil = validar_perfil(perfil)
    imprimir_resumo_terminal(resultado_perfil)
    if resultado_perfil.tem_erro and perfil.geracao.interromper_em_erro:
        logger.error("Validação interrompida: estrutura do perfil tem erro(s) crítico(s).")
        return 1

    curriculo, referenciais, avisos = _carregar_contexto(perfil)
    fichas = _carregar_fichas_do_perfil(perfil) if getattr(args, "incluir_fichas", False) else None

    resultado, situacao_fichas = validar_curriculo(
        curriculo, perfil, referenciais, fichas=fichas, avisos_leitura=avisos
    )
    imprimir_resumo_terminal(resultado)
    _gravar_relatorios_validacao(perfil, resultado, situacao_fichas)

    if resultado.tem_erro and perfil.geracao.interromper_em_erro:
        return 1
    return 0


def cmd_validar_fichas(args: argparse.Namespace) -> int:
    args.incluir_fichas = True
    return cmd_validar(args)


def cmd_gerar(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)
    curriculo, referenciais, avisos = _carregar_contexto(perfil)

    resultado, _ = validar_curriculo(curriculo, perfil, referenciais, avisos_leitura=avisos)
    imprimir_resumo_terminal(resultado)
    _gravar_relatorios_validacao(perfil, resultado, None)

    if resultado.tem_erro and perfil.geracao.interromper_em_erro:
        logger.error("Geração interrompida: há erro(s) crítico(s) de validação.")
        return 1

    pasta_latex = _pasta_saida_perfil(perfil) / "latex"
    gerados = gerar_arquivos_latex(curriculo, perfil, referenciais, pasta_latex / "gerado")
    print(f"\n{len(gerados)} arquivo(s) LaTeX gerado(s) em {pasta_latex / 'gerado'}:")
    for caminho in gerados:
        print(f"  - {caminho.name}")
    return 0


def cmd_compilar(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)
    pasta_latex = _pasta_saida_perfil(perfil) / "latex"
    caminho_tex = montar_arvore_latex(perfil, pasta_latex)
    nome_base = perfil.saida.nome_base
    destino = _pasta_saida_perfil(perfil) / f"{nome_base}_corpo.pdf"
    try:
        compilar_pdf(caminho_tex, destino)
    except PPCGenError as exc:
        logger.error(str(exc))
        return 1
    print(f"PDF do corpo do PPC gerado em: {destino}")
    return 0


def cmd_completo(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)

    resultado_perfil = validar_perfil(perfil)
    imprimir_resumo_terminal(resultado_perfil)
    if resultado_perfil.tem_erro and perfil.geracao.interromper_em_erro:
        logger.error("PPC completo interrompido: estrutura do perfil tem erro(s) crítico(s).")
        return 1

    curriculo, referenciais, avisos = _carregar_contexto(perfil)
    fichas = _carregar_fichas_do_perfil(perfil)

    resultado, situacao_fichas = validar_curriculo(
        curriculo, perfil, referenciais, fichas=fichas, avisos_leitura=avisos
    )
    imprimir_resumo_terminal(resultado)
    _gravar_relatorios_validacao(perfil, resultado, situacao_fichas)

    if resultado.tem_erro and perfil.geracao.interromper_em_erro:
        logger.error("Geração do PPC completo interrompida: há erro(s) crítico(s).")
        return 1

    pasta_saida = _pasta_saida_perfil(perfil)
    pasta_latex = pasta_saida / "latex"
    gerar_arquivos_latex(curriculo, perfil, referenciais, pasta_latex / "gerado")
    caminho_tex = montar_arvore_latex(perfil, pasta_latex)

    nome_base = perfil.saida.nome_base
    pdf_corpo = pasta_saida / f"{nome_base}_corpo.pdf"
    try:
        compilar_pdf(caminho_tex, pdf_corpo)
    except PPCGenError as exc:
        logger.error(str(exc))
        return 1

    fichas_por_codigo = {f.codigo: f for f in fichas}
    ordem = sorted(
        (c for c in curriculo.ativos() if c.tipo != TipoComponente.ATIVIDADE_COMPLEMENTAR),
        key=lambda c: (c.periodo if c.periodo is not None else 99, c.nome),
    )
    anexos_em_ordem = [
        fichas_por_codigo[c.codigo].arquivo_origem
        for c in ordem
        if c.codigo in fichas_por_codigo and fichas_por_codigo[c.codigo].arquivo_origem
    ]

    if perfil.geracao.anexar_resolucoes:
        pasta_resolucoes = perfil.diretorio / perfil.arquivos.anexos / "resolucoes"
        if pasta_resolucoes.exists():
            anexos_em_ordem += sorted(pasta_resolucoes.glob("*.pdf"))

    pdf_completo = pasta_saida / f"{nome_base}_completo.pdf"
    destino, nao_anexadas = montar_pdf_completo(pdf_corpo, anexos_em_ordem, pdf_completo)

    print(f"\nPPC completo do perfil '{perfil.info.id}' gerado com sucesso. Arquivos produzidos:")
    print(f"  - {pdf_corpo}")
    print(f"  - {destino}")
    print(f"  - {pasta_saida / 'relatorios' / 'validacao.html'}")
    print(f"  - {pasta_saida / 'relatorios' / 'validacao.json'}")
    if nao_anexadas:
        print(
            f"\nATENÇÃO: {len(nao_anexadas)} ficha(s)/anexo(s) não puderam ser anexados "
            "(formato não é PDF) — converta manualmente e reexecute:"
        )
        for caminho in nao_anexadas:
            print(f"  - {caminho}")
    return 0


def cmd_comparar(args: argparse.Namespace) -> int:
    anterior, _meta_a, _avisos_a = carregar_matriz(args.anterior)
    atual, _meta_b, _avisos_b = carregar_matriz(args.atual)
    relatorio = comparar_curriculos(anterior, atual)

    pasta_saida = Path(args.saida) if args.saida else raiz_projeto() / "saida"
    gerar_relatorio_comparacao_html(relatorio, pasta_saida / "relatorio_comparacao.html")
    gerar_relatorio_comparacao_json(relatorio, pasta_saida / "relatorio_comparacao.json")

    print(
        f"Comparação {relatorio.versao_anterior} -> {relatorio.versao_atual}: "
        f"{len(relatorio.incluidos)} incluído(s), {len(relatorio.removidos)} removido(s), "
        f"{len(relatorio.alterados)} alterado(s)."
    )
    print(f"Relatórios em: {pasta_saida / 'relatorio_comparacao.html'} / .json")
    return 0


def _limpar_perfil(perfil_id: str) -> int:
    pasta_saida = raiz_projeto() / "saida" / perfil_id
    removidos = 0
    if pasta_saida.exists():
        shutil.rmtree(pasta_saida)
        removidos += 1
    print(f"Saída do perfil '{perfil_id}' removida ({pasta_saida}).")
    return removidos


def cmd_limpar(args: argparse.Namespace) -> int:
    raiz = raiz_projeto()

    if getattr(args, "todos", False):
        pasta_saida_raiz = raiz / "saida"
        if pasta_saida_raiz.exists():
            for pasta_perfil in pasta_saida_raiz.iterdir():
                if pasta_perfil.is_dir():
                    shutil.rmtree(pasta_perfil)
        print("Saída de todos os perfis removida.")
    else:
        perfil = _resolver_perfil(args)
        _limpar_perfil(perfil.info.id)

    for pasta_cache in raiz.rglob("__pycache__"):
        shutil.rmtree(pasta_cache, ignore_errors=True)

    print("Dados de entrada (dados/perfis, dados/compartilhados) foram preservados.")
    return 0


# ---------------------------------------------------------------------------
# Comandos de gestão de perfis
# ---------------------------------------------------------------------------


def cmd_perfis(_args: argparse.Namespace) -> int:
    referencias = perfis_mod.listar_referencias()
    linhas = []
    for ref in referencias.values():
        try:
            perfil = perfis_mod.carregar_perfil(ref.caminho)
            valido = not validar_perfil(perfil).tem_erro
            linhas.append(
                (perfil.info.id, perfil.curso.nome, perfil.info.versao, perfil.info.status, str(ref.caminho), valido)
            )
        except PPCGenError as exc:
            linhas.append((ref.id, f"<erro: {exc}>", "-", "-", str(ref.caminho), False))

    largura_id = max((len(linha[0]) for linha in linhas), default=6)
    largura_curso = max((len(linha[1]) for linha in linhas), default=5)
    largura_versao = max((len(linha[2]) for linha in linhas), default=6)
    print(
        f"{'PERFIL':<{largura_id}}  {'CURSO':<{largura_curso}}  {'VERSÃO':<{largura_versao}}  "
        "STATUS       VÁLIDO"
    )
    for perfil_id, curso, versao, status, _caminho, valido in linhas:
        print(
            f"{perfil_id:<{largura_id}}  {curso:<{largura_curso}}  {versao:<{largura_versao}}  "
            f"{status:<12} {'sim' if valido else 'não'}"
        )
    return 0


def cmd_perfil_info(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)
    print(f"id: {perfil.info.id}")
    print(f"nome: {perfil.info.nome}")
    print(f"status: {perfil.info.status}")
    print(f"versão: {perfil.info.versao}")
    print(f"extends: {perfil.info.extends or '(nenhum)'}")
    print(f"curso: {perfil.curso.nome} ({perfil.curso.grau}, {perfil.curso.modalidade})")
    print(f"instituição: {perfil.instituicao.nome} / {perfil.instituicao.unidade_academica}")
    print(f"diretório: {perfil.diretorio}")
    print(f"carga horária total configurada: {perfil.curriculo.carga_horaria_total}")
    return 0


def cmd_perfil_validar(args: argparse.Namespace) -> int:
    perfil = _resolver_perfil(args)
    resultado = validar_perfil(perfil)
    imprimir_resumo_terminal(resultado)
    return 1 if resultado.tem_erro else 0


def cmd_perfil_criar(args: argparse.Namespace) -> int:
    pasta_perfis = raiz_projeto() / "dados" / "perfis"
    destino = criar_perfil(pasta_perfis, args.id, args.nome)
    print(f"Perfil '{args.id}' criado em {destino}")
    return 0


def cmd_perfil_clonar(args: argparse.Namespace) -> int:
    pasta_perfis = raiz_projeto() / "dados" / "perfis"
    destino = clonar_perfil(pasta_perfis, args.origem, args.destino, versao=args.versao)
    print(f"Perfil '{args.origem}' clonado para '{args.destino}' em {destino}")
    return 0


# ---------------------------------------------------------------------------
# Comandos em lote
# ---------------------------------------------------------------------------


def _perfis_para_lote(status: str | None) -> list[Perfil]:
    referencias = perfis_mod.listar_referencias()
    perfis = []
    for ref in referencias.values():
        if not ref.ativo:
            continue
        perfil = perfis_mod.carregar_perfil(ref.caminho)
        if status is not None and perfil.info.status != status:
            continue
        perfis.append(perfil)
    return perfis


def _rodar_em_lote(args: argparse.Namespace, comando_unico) -> int:
    perfis = _perfis_para_lote(getattr(args, "status", None))
    if not perfis:
        print("Nenhum perfil ativo encontrado (verifique --status ou dados/perfis.yaml).")
        return 0

    resultados: list[tuple[str, int]] = []
    for perfil in perfis:
        print(f"\n=== Perfil: {perfil.info.id} ===")
        args_perfil = argparse.Namespace(**vars(args))
        args_perfil.perfil = perfil.info.id
        args_perfil.perfil_dir = None
        try:
            codigo = comando_unico(args_perfil)
        except PPCGenError as exc:
            logger.error("Perfil '%s' falhou: %s", perfil.info.id, exc)
            codigo = 1
        resultados.append((perfil.info.id, codigo))

    print("\n=== Resumo do lote ===")
    for perfil_id, codigo in resultados:
        print(f"  {perfil_id}: {'OK' if codigo == 0 else 'FALHOU'}")

    return 1 if any(codigo != 0 for _id, codigo in resultados) else 0


def cmd_validar_todos(args: argparse.Namespace) -> int:
    args.incluir_fichas = False
    return _rodar_em_lote(args, cmd_validar)


def cmd_gerar_todos(args: argparse.Namespace) -> int:
    return _rodar_em_lote(args, cmd_gerar)


def cmd_completo_todos(args: argparse.Namespace) -> int:
    return _rodar_em_lote(args, cmd_completo)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _add_selecao_perfil(sub: argparse.ArgumentParser) -> None:
    grupo = sub.add_mutually_exclusive_group()
    grupo.add_argument("--perfil", help="identificador do perfil (dados/perfis/<id>/)")
    grupo.add_argument("--perfil-dir", help="caminho direto para a pasta do perfil")


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ppcgen", description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="ativa logs em nível DEBUG")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_validar = subparsers.add_parser("validar", help="valida o perfil e a matriz curricular")
    _add_selecao_perfil(p_validar)
    p_validar.add_argument("--incluir-fichas", action="store_true", help="também valida as fichas")
    p_validar.set_defaults(func=cmd_validar, incluir_fichas=False)

    p_validar_fichas = subparsers.add_parser("validar-fichas", help="valida somente as fichas")
    _add_selecao_perfil(p_validar_fichas)
    p_validar_fichas.set_defaults(func=cmd_validar_fichas)

    p_gerar = subparsers.add_parser("gerar", help="gera os arquivos LaTeX do corpo do PPC")
    _add_selecao_perfil(p_gerar)
    p_gerar.set_defaults(func=cmd_gerar)

    p_compilar = subparsers.add_parser("compilar", help="compila o corpo do PPC em PDF")
    _add_selecao_perfil(p_compilar)
    p_compilar.set_defaults(func=cmd_compilar)

    p_completo = subparsers.add_parser("completo", help="valida, gera, compila e consolida o PPC completo")
    _add_selecao_perfil(p_completo)
    p_completo.set_defaults(func=cmd_completo)

    p_comparar = subparsers.add_parser("comparar", help="compara duas versões da matriz curricular")
    p_comparar.add_argument("--anterior", required=True, help="matriz curricular anterior (.xlsx)")
    p_comparar.add_argument("--atual", required=True, help="matriz curricular atual (.xlsx)")
    p_comparar.add_argument("--saida", help="pasta de saída dos relatórios (padrão: ./saida)")
    p_comparar.set_defaults(func=cmd_comparar)

    p_limpar = subparsers.add_parser("limpar", help="remove artefatos temporários/recriáveis")
    _add_selecao_perfil(p_limpar)
    p_limpar.add_argument("--todos", action="store_true", help="limpa a saída de todos os perfis")
    p_limpar.set_defaults(func=cmd_limpar)

    p_perfis = subparsers.add_parser("perfis", help="lista os perfis disponíveis")
    p_perfis.set_defaults(func=cmd_perfis)

    p_perfil_info = subparsers.add_parser("perfil-info", help="mostra os dados de um perfil")
    _add_selecao_perfil(p_perfil_info)
    p_perfil_info.set_defaults(func=cmd_perfil_info)

    p_perfil_validar = subparsers.add_parser("perfil-validar", help="valida somente a estrutura do perfil")
    _add_selecao_perfil(p_perfil_validar)
    p_perfil_validar.set_defaults(func=cmd_perfil_validar)

    p_perfil_criar = subparsers.add_parser("perfil-criar", help="cria a estrutura inicial de um novo perfil")
    p_perfil_criar.add_argument("--id", required=True, help="identificador único do novo perfil")
    p_perfil_criar.add_argument("--nome", required=True, help="nome de exibição do novo perfil")
    p_perfil_criar.set_defaults(func=cmd_perfil_criar)

    p_perfil_clonar = subparsers.add_parser("perfil-clonar", help="clona um perfil existente")
    p_perfil_clonar.add_argument("--origem", required=True, help="id do perfil de origem")
    p_perfil_clonar.add_argument("--destino", required=True, help="id do novo perfil")
    p_perfil_clonar.add_argument("--versao", help="nova versão curricular (opcional)")
    p_perfil_clonar.set_defaults(func=cmd_perfil_clonar, versao=None)

    p_validar_todos = subparsers.add_parser("validar-todos", help="valida todos os perfis ativos")
    p_validar_todos.add_argument("--status", help="filtra por status (ex.: vigente, proposta)")
    p_validar_todos.set_defaults(func=cmd_validar_todos, status=None)

    p_gerar_todos = subparsers.add_parser("gerar-todos", help="gera todos os perfis ativos")
    p_gerar_todos.add_argument("--status", help="filtra por status")
    p_gerar_todos.set_defaults(func=cmd_gerar_todos, status=None)

    p_completo_todos = subparsers.add_parser("completo-todos", help="gera o PPC completo de todos os perfis ativos")
    p_completo_todos.add_argument("--status", help="filtra por status")
    p_completo_todos.set_defaults(func=cmd_completo_todos, status=None)

    return parser


def _forcar_utf8_console() -> None:
    """Evita o crash de encoding do script legado (UnicodeDecodeError em
    consoles Windows com codepage cp1252): reconfigura stdout/stderr para
    UTF-8 quando o interpretador suportar, em vez de depender de
    ``PYTHONUTF8=1`` estar setado no ambiente."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _forcar_utf8_console()
    parser = _construir_parser()
    args = parser.parse_args(argv)
    configurar(verbose=args.verbose)

    try:
        return args.func(args)
    except PPCGenError as exc:
        logger.error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
