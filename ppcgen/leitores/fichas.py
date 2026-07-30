"""Leitura de fichas de componentes curriculares (DOCX, PDF com texto, PDFs
exportados do SEI).

Cada formato tem seu próprio adaptador (Seção 15) em vez de uma bateria de
expressões regulares genéricas tentando cobrir todos os casos. OCR **não** é
usado como estratégia principal: um PDF sem camada de texto extraível é
marcado como não reconhecido, com confiança zero, para revisão manual — esta
versão não embute um motor de OCR.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from ppcgen.modelos import FichaCurricular
from ppcgen.utilitarios.logging import obter_logger

logger = obter_logger(__name__)

_SECOES = {
    "ementa": r"EMENTA\s*\n([\s\S]*?)\n(?=PROGRAMA|OBJETIVOS|METODOLOGIA|$)",
    "objetivos": r"OBJETIVOS?\s*\n([\s\S]*?)\n(?=EMENTA|PROGRAMA|METODOLOGIA|$)",
    "programa": r"PROGRAMA\s*\n([\s\S]*?)\n(?=METODOLOGIA|AVALIA|BIBLIOGRAFIA|$)",
    "metodologia": r"METODOLOGIA\s*\n([\s\S]*?)\n(?=AVALIA|BIBLIOGRAFIA|$)",
    "avaliacao": r"AVALIA[ÇC][ÃA]O\s*\n([\s\S]*?)\n(?=BIBLIOGRAFIA|$)",
    "bibliografia_basica": r"BIBLIOGRAFIA B[ÁA]SICA\s*\n([\s\S]*?)\n(?=BIBLIOGRAFIA COMPLEMENTAR|$)",
    "bibliografia_complementar": r"BIBLIOGRAFIA COMPLEMENTAR\s*\n([\s\S]*?)$",
}


def _extrair_secoes(texto: str) -> dict[str, str]:
    dados = {}
    for campo, padrao in _SECOES.items():
        m = re.search(padrao, texto, re.IGNORECASE)
        dados[campo] = m.group(1).strip() if m else ""
    return dados


def _extrair_codigo(texto: str, nome_arquivo: str) -> str:
    m = re.search(r"C[ÓO]DIGO:\s*(\S+)", texto, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # PDFs do SEI costumam ter o código no próprio nome do arquivo.
    m = re.search(r"([A-Z]{3,}[!_]?\w+)\.pdf$", nome_arquivo, re.IGNORECASE)
    return m.group(1) if m else Path(nome_arquivo).stem


class LeitorFicha(ABC):
    @abstractmethod
    def suporta(self, caminho: Path) -> bool: ...

    @abstractmethod
    def extrair(self, caminho: Path) -> FichaCurricular: ...


class LeitorFichaPDF(LeitorFicha):
    """Lê PDFs com camada de texto (inclusive exportações do SEI)."""

    LIMIAR_TEXTO_MINIMO = 200  # caracteres; abaixo disso, tratamos como "sem texto"

    def suporta(self, caminho: Path) -> bool:
        return caminho.suffix.lower() == ".pdf"

    def extrair(self, caminho: Path) -> FichaCurricular:
        from pypdf import PdfReader

        reader = PdfReader(str(caminho))
        texto = "\n".join(pagina.extract_text() or "" for pagina in reader.pages)

        if len(texto.strip()) < self.LIMIAR_TEXTO_MINIMO:
            logger.warning(
                "Ficha '%s' sem camada de texto suficiente (%d caracteres); "
                "OCR não é usado como estratégia principal — marcando confiança baixa.",
                caminho.name,
                len(texto.strip()),
            )
            return FichaCurricular(
                codigo=_extrair_codigo("", caminho.name),
                arquivo_origem=caminho,
                formato_origem="pdf_sem_texto",
                confianca_extracao=0.0,
            )

        secoes = _extrair_secoes(texto)
        nome_m = re.search(r"COMPONENTE CURRICULAR:\s*(.*)", texto, re.IGNORECASE)
        cht_m = re.search(r"TE[ÓO]RICA:\s*(\d+)", texto, re.IGNORECASE)
        chp_m = re.search(r"PR[ÁA]TICA:\s*(\d+)", texto, re.IGNORECASE)
        chd_m = re.search(r"DIST[ÂA]NCIA:\s*(\d+)", texto, re.IGNORECASE)
        tot_m = re.search(r"CH\s*TOTAL:\s*(\d+)", texto, re.IGNORECASE)

        from ppcgen.modelos import CargaHoraria

        carga = None
        if any([cht_m, chp_m, chd_m, tot_m]):
            carga = CargaHoraria(
                teorica=int(cht_m.group(1)) if cht_m else None,
                pratica=int(chp_m.group(1)) if chp_m else None,
                ead=int(chd_m.group(1)) if chd_m else None,
                total=int(tot_m.group(1)) if tot_m else None,
            )

        return FichaCurricular(
            codigo=_extrair_codigo(texto, caminho.name),
            nome=nome_m.group(1).strip() if nome_m else "",
            carga_horaria=carga,
            arquivo_origem=caminho,
            formato_origem="pdf",
            confianca_extracao=1.0,
            **secoes,
        )


class LeitorFichaDOCX(LeitorFicha):
    """Lê fichas em formato DOCX (modelo editável)."""

    def suporta(self, caminho: Path) -> bool:
        return caminho.suffix.lower() == ".docx"

    def extrair(self, caminho: Path) -> FichaCurricular:
        import docx

        documento = docx.Document(str(caminho))
        texto = "\n".join(p.text for p in documento.paragraphs)
        secoes = _extrair_secoes(texto)
        nome_m = re.search(r"COMPONENTE CURRICULAR:\s*(.*)", texto, re.IGNORECASE)

        return FichaCurricular(
            codigo=_extrair_codigo(texto, caminho.name),
            nome=nome_m.group(1).strip() if nome_m else "",
            arquivo_origem=caminho,
            formato_origem="docx",
            confianca_extracao=1.0,
            **secoes,
        )


_ADAPTADORES: list[LeitorFicha] = [LeitorFichaPDF(), LeitorFichaDOCX()]


def detectar_leitor(caminho: Path) -> LeitorFicha | None:
    for adaptador in _ADAPTADORES:
        if adaptador.suporta(caminho):
            return adaptador
    return None


def carregar_fichas(pasta: Path) -> list[FichaCurricular]:
    """Carrega todas as fichas reconhecíveis de ``pasta`` (não recursivo)."""

    if not pasta.exists():
        return []

    fichas = []
    for caminho in sorted(pasta.iterdir()):
        if not caminho.is_file():
            continue
        adaptador = detectar_leitor(caminho)
        if adaptador is None:
            logger.info("Arquivo '%s' com formato não reconhecido, ignorado.", caminho.name)
            continue
        try:
            fichas.append(adaptador.extrair(caminho))
        except Exception as exc:  # noqa: BLE001 - relatamos e seguimos para as demais fichas
            logger.error("Falha ao ler ficha '%s': %s", caminho.name, exc)
            fichas.append(
                FichaCurricular(
                    codigo=Path(caminho.name).stem,
                    arquivo_origem=caminho,
                    formato_origem="erro",
                    confianca_extracao=0.0,
                )
            )
    return fichas
