"""Compilação do PDF via ``latexmk``/``pdflatex`` (Seção 13/16).

Isola o processo externo em uma única função para que a CLI trate erro de
compilação de forma uniforme (Seção 12: código de saída != 0 em caso de
erro crítico).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ppcgen.config import Perfil
from ppcgen.excecoes import CompilacaoLatexFalhou
from ppcgen.utilitarios.caminhos import raiz_projeto
from ppcgen.utilitarios.logging import obter_logger

logger = obter_logger(__name__)


_EXTENSOES_IMAGEM = {".png", ".jpg", ".jpeg", ".pdf", ".eps"}


def _copiar_arvore(origem: Path, destino: Path) -> None:
    if origem.exists():
        shutil.copytree(origem, destino, dirs_exist_ok=True)


def _copiar_imagens(origem: Path, destino: Path) -> None:
    """Copia só os arquivos de imagem de ``origem`` para ``destino`` — usado
    para trazer a pasta de identidade visual compartilhada (que também
    contém ``cores.yaml``, não um arquivo LaTeX) para dentro de ``figuras/``.
    """

    if not origem.exists():
        return
    destino.mkdir(parents=True, exist_ok=True)
    for arquivo in origem.iterdir():
        if arquivo.is_file() and arquivo.suffix.lower() in _EXTENSOES_IMAGEM:
            shutil.copyfile(arquivo, destino / arquivo.name)


def montar_arvore_latex(perfil: Perfil, pasta_destino: Path) -> Path:
    """Monta, em ``pasta_destino``, uma árvore LaTeX autocontida e pronta
    para compilar: templates genéricos (``templates/latex/``) + conteúdo do
    perfil (``textos/``, ``frontmatter/``, ``figuras/``, bibliografia),
    resolvido através da cadeia de herança (``extends``), com os
    ``overrides/`` do perfil aplicados por cima (Seção 6/9).

    Não grava nada dentro da pasta do perfil (Seção 12) — tudo é escrito em
    ``pasta_destino`` (``saida/<perfil_id>/latex/``).
    """

    pasta_destino.mkdir(parents=True, exist_ok=True)
    pasta_templates = raiz_projeto() / "templates" / "latex"

    # 1) Templates genéricos (base).
    shutil.copyfile(pasta_templates / "Main.tex", pasta_destino / "Main.tex")
    _copiar_arvore(pasta_templates / "configuracoes", pasta_destino / "configuracoes")

    # 2) Conteúdo do perfil, da cadeia de herança para o mais específico
    #    (perfil base primeiro, perfil atual por cima — Seção 9, prioridade 1 > 2).
    cadeia = []
    atual: Perfil | None = perfil
    while atual is not None:
        cadeia.append(atual)
        atual = atual.perfil_base
    for p in reversed(cadeia):
        _copiar_arvore(p.diretorio / p.arquivos.textos, pasta_destino / "textos")
        _copiar_arvore(p.diretorio / p.arquivos.figuras, pasta_destino / "figuras")
        folha_rosto = p.diretorio / p.arquivos.frontmatter / "folha_rosto.tex"
        if folha_rosto.exists():
            (pasta_destino / "frontmatter").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(folha_rosto, pasta_destino / "frontmatter" / "folha_rosto.tex")

    # 2b) Identidade visual compartilhada (logos institucionais etc.), só se
    #     declarada explicitamente em heranca.identidade_visual (Seção 6: sem
    #     acesso implícito a dados/compartilhados/) — disponível em
    #     ``figuras/compartilhadas/`` para os textos do perfil referenciarem.
    if perfil.heranca.identidade_visual:
        pasta_identidade = perfil.caminho_compartilhado(perfil.heranca.identidade_visual).parent
        _copiar_imagens(pasta_identidade, pasta_destino / "figuras" / "compartilhadas")

    # 3) Bibliografia: concatena as fontes compartilhadas (heranca.referencias)
    #    com a bibliografia própria do perfil, sempre deixando o arquivo de
    #    destino existir (mesmo vazio) para que \addbibresource nunca aponte
    #    para um caminho inexistente.
    (pasta_destino / "referencias").mkdir(parents=True, exist_ok=True)
    destino_biblio = pasta_destino / "referencias" / "bibliografia.bib"
    partes_bib = []
    for caminho_rel in perfil.heranca.referencias:
        caminho_bib_compartilhado = perfil.caminho_compartilhado(caminho_rel)
        if caminho_bib_compartilhado.exists():
            partes_bib.append(caminho_bib_compartilhado.read_text(encoding="utf-8"))
    caminho_biblio = perfil.resolver_arquivo(perfil.arquivos.bibliografia)
    if caminho_biblio is not None:
        partes_bib.append(caminho_biblio.read_text(encoding="utf-8"))
    if partes_bib:
        destino_biblio.write_text("\n\n".join(partes_bib), encoding="utf-8")
    else:
        destino_biblio.write_text("% Nenhuma bibliografia declarada neste perfil.\n", encoding="utf-8")

    # 4) Overrides do perfil (prioridade máxima — Seção 9).
    _copiar_arvore(perfil.diretorio / perfil.arquivos.overrides / "latex", pasta_destino)
    _copiar_arvore(perfil.diretorio / perfil.arquivos.overrides / "estilos", pasta_destino / "configuracoes")

    return pasta_destino / "Main.tex"


def compilar_pdf(caminho_tex: Path, arquivo_saida: Path) -> Path:
    """Compila ``caminho_tex`` (executando a partir do diretório do arquivo)
    e copia o PDF resultante para ``arquivo_saida``.

    Artefatos de build (``.aux``/``.log``/... e o próprio PDF intermediário)
    ficam isolados em ``<pasta_tex>/build/`` (Seção 13) — nunca na raiz do
    projeto nem misturados com os fontes do perfil.
    """

    pasta_tex = caminho_tex.parent
    nome_base = caminho_tex.stem
    pasta_build = pasta_tex / "build"
    pasta_build.mkdir(parents=True, exist_ok=True)

    comando = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={pasta_build}",
        caminho_tex.name,
    ]
    logger.info("Compilando %s (isso pode levar alguns minutos)...", caminho_tex)
    resultado = subprocess.run(
        comando,
        cwd=pasta_tex,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    pdf_gerado = pasta_build / f"{nome_base}.pdf"
    if resultado.returncode != 0 or not pdf_gerado.exists():
        log_saida = (resultado.stdout or "") + "\n" + (resultado.stderr or "")
        raise CompilacaoLatexFalhou(
            f"Falha ao compilar {caminho_tex.name} (código {resultado.returncode}).\n"
            f"Últimas linhas do log:\n" + "\n".join(log_saida.splitlines()[-40:])
        )

    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf_gerado, arquivo_saida)
    logger.info("PDF gerado em %s", arquivo_saida)
    return arquivo_saida


def montar_pdf_completo(
    pdf_corpo: Path, fichas_pdf_em_ordem: list[Path], destino: Path
) -> tuple[Path, list[Path]]:
    """Concatena o corpo do PPC com as fichas curriculares (em PDF) na ordem
    curricular informada. Fichas que não estejam em PDF (ex.: DOCX ainda não
    exportado) não podem ser anexadas diretamente — são reportadas para
    conversão manual, nunca ignoradas silenciosamente (Seção 16).
    """

    from pypdf import PdfWriter

    nao_anexadas = [f for f in fichas_pdf_em_ordem if f.suffix.lower() != ".pdf"]
    anexaveis = [f for f in fichas_pdf_em_ordem if f.suffix.lower() == ".pdf"]

    writer = PdfWriter()
    writer.append(str(pdf_corpo))
    for ficha_pdf in anexaveis:
        writer.append(str(ficha_pdf))

    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        writer.write(f)

    if nao_anexadas:
        logger.warning(
            "%d ficha(s) não estão em PDF e não foram anexadas ao PPC completo: %s",
            len(nao_anexadas),
            ", ".join(p.name for p in nao_anexadas),
        )
    return destino, nao_anexadas
