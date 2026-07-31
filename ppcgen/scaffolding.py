"""Criação e clonagem de perfis (Seção 11).

Mantido separado da CLI para que a lógica de "quais arquivos um perfil novo
precisa" fique testável isoladamente.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import openpyxl
import yaml

from ppcgen.excecoes import ConfiguracaoInvalida

_PASTAS_FICHAS = ("obrigatorias", "optativas", "extensao", "tcc", "estagio", "complementares")
_PASTAS_ANEXOS = ("resolucoes", "pareceres", "outros")
_TEXTOS = (
    "identificacao.tex",
    "apresentacao.tex",
    "justificativa.tex",
    "principios.tex",
    "perfil_egresso.tex",
    "objetivos.tex",
    "estrutura_curricular.tex",
    "diretrizes_pedagogicas.tex",
    "avaliacao.tex",
    "atendimento_estudante.tex",
    "acompanhamento_egresso.tex",
    "consideracoes_finais.tex",
)


def _criar_matriz_vazia(caminho: Path) -> None:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    componentes = wb.create_sheet("Componentes")
    componentes.append(
        [
            "codigo", "nome", "tipo", "periodo", "ativo", "obrigatorio",
            "cht", "chp", "chd", "che", "tot", "observacoes",
            "pre_requisitos", "correquisitos",
        ]
    )
    for aba, cabecalho in (
        ("Equivalencias", ["codigo_origem", "codigo_destino", "observacao"]),
        ("Nucleos", ["id", "nome", "descricao", "componentes"]),
        ("Areas", ["id", "nome", "descricao", "componentes"]),
        ("Temas", ["id", "nome", "descricao", "fonte_normativa", "status", "componentes"]),
        ("Conteudos", ["id", "descricao", "obrigatorio", "fonte", "componentes"]),
        ("Competencias", ["id", "descricao", "obrigatoria", "fonte", "componentes"]),
    ):
        ws = wb.create_sheet(aba)
        ws.append(cabecalho)

    wb.save(caminho)


def criar_perfil(pasta_perfis: Path, perfil_id: str, nome: str) -> Path:
    """Cria a estrutura inicial de um perfil novo e vazio em
    ``pasta_perfis/<perfil_id>/``."""

    destino = pasta_perfis / perfil_id
    if destino.exists():
        raise ConfiguracaoInvalida(f"Já existe um perfil em {destino}.")

    destino.mkdir(parents=True)
    (destino / "textos").mkdir()
    (destino / "frontmatter").mkdir()
    (destino / "referencias").mkdir()
    (destino / "figuras" / "imagens_capitulos").mkdir(parents=True)
    (destino / "figuras" / "diagramas").mkdir(parents=True)
    (destino / "overrides" / "latex").mkdir(parents=True)
    (destino / "overrides" / "estilos").mkdir(parents=True)
    for sub in _PASTAS_FICHAS:
        (destino / "fichas" / sub).mkdir(parents=True)
    for sub in _PASTAS_ANEXOS:
        (destino / "anexos" / sub).mkdir(parents=True)

    perfil_yaml = {
        "perfil": {
            "id": perfil_id,
            "nome": nome,
            "status": "rascunho",
            "versao": "",
            "descricao": "",
        },
        "curso": {
            "nome": nome,
            "nome_curto": "",
            "sigla": "",
            "grau": "",
            "modalidade": "",
            "turno": "",
            "regime_academico": "Semestral",
            "numero_periodos": 8,
            "campus": "",
            "municipio": "",
            "estado": "",
        },
        "instituicao": {"nome": "", "sigla": "", "unidade_academica": ""},
        "curriculo": {
            "carga_horaria_total": None,
            "carga_obrigatoria": None,
            "carga_optativa_minima": None,
            "carga_extensao": None,
            "carga_aac": None,
            "carga_estagio": None,
            "carga_tcc": None,
            "percentual_minimo_extensao": None,
            "percentual_maximo_ead": None,
            "carga_horaria_maxima_periodo": None,
            "periodo_minimo_tcc": None,
            "periodo_minimo_estagio": None,
        },
        "arquivos": {
            "matriz": "matriz_curricular.xlsx",
            "bibliografia": "referencias/bibliografia.bib",
            "textos": "textos",
            "fichas": "fichas",
            "figuras": "figuras",
            "anexos": "anexos",
            "frontmatter": "frontmatter",
            "overrides": "overrides",
        },
        "geracao": {
            "template": "padrao",
            "anexar_fichas": True,
            "anexar_resolucoes": True,
            "gerar_fluxo_curricular": True,
            "gerar_representacao_grafica": True,
            "gerar_relatorio_validacao": True,
            "compilar_pdf": True,
            "interromper_em_erro": True,
        },
        "saida": {
            "nome_base": f"PPC_{perfil_id}",
            "gerar_corpo": True,
            "gerar_completo": True,
        },
        "legislacao": [],
    }
    (destino / "perfil.yaml").write_text(
        yaml.safe_dump(perfil_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    _criar_matriz_vazia(destino / "matriz_curricular.xlsx")

    for nome_arquivo in _TEXTOS:
        titulo = nome_arquivo.replace(".tex", "").replace("_", " ").title()
        (destino / "textos" / nome_arquivo).write_text(
            f"% TODO: escrever o capítulo '{titulo}'.\n", encoding="utf-8"
        )

    (destino / "referencias" / "bibliografia.bib").write_text(
        "% Adicione aqui as referências bibliográficas deste perfil.\n", encoding="utf-8"
    )
    (destino / "frontmatter" / "capa.yaml").write_text("capa:\n  ano: null\n", encoding="utf-8")
    (destino / "frontmatter" / "autoridades.yaml").write_text("autoridades: []\n", encoding="utf-8")
    (destino / "frontmatter" / "comissao.yaml").write_text(
        "comissao:\n  titulo: \"Equipe de elaboração deste Projeto Pedagógico\"\n  membros: []\n",
        encoding="utf-8",
    )

    (destino / "README.md").write_text(
        f"# Perfil: {perfil_id}\n\n{nome}\n\nStatus: rascunho — gerado por "
        "`python -m ppcgen perfil-criar`. Preencha `perfil.yaml` (incluindo a "
        "seção `legislacao:`), `matriz_curricular.xlsx` (componentes e as "
        "abas Nucleos/Areas/Temas/Conteudos/Competencias, cada uma com sua "
        "coluna `componentes` listando os códigos vinculados, separados por "
        "`|`) e `textos/` antes de validar.\n",
        encoding="utf-8",
    )

    return destino


def clonar_perfil(
    pasta_perfis: Path, origem_id: str, destino_id: str, versao: str | None = None
) -> Path:
    """Clona um perfil existente: copia arquivos editáveis, atualiza id/versão,
    e registra a origem — nunca copia artefatos gerados (não existem dentro
    da pasta do perfil, por isolamento — Seção 12) nem caches."""

    origem = pasta_perfis / origem_id
    destino = pasta_perfis / destino_id
    if not origem.exists():
        raise ConfiguracaoInvalida(f"Perfil de origem '{origem_id}' não existe em {origem}.")
    if destino.exists():
        raise ConfiguracaoInvalida(f"Já existe um perfil em {destino}.")

    shutil.copytree(
        origem,
        destino,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )

    caminho_yaml = destino / "perfil.yaml"
    dados = yaml.safe_load(caminho_yaml.read_text(encoding="utf-8")) or {}
    dados.setdefault("perfil", {})["id"] = destino_id
    dados["perfil"]["origem_clonagem"] = origem_id
    if versao is not None:
        dados["perfil"]["versao"] = versao
    caminho_yaml.write_text(yaml.safe_dump(dados, allow_unicode=True, sort_keys=False), encoding="utf-8")

    return destino
