"""Validação estrutural do perfil (Seção 14) — roda ANTES da validação da
matriz curricular. Verifica que o perfil está minimamente bem-formado:
identificador válido, arquivos declarados existem, herança é resolvível.

Usa os mesmos códigos de severidade do restante do sistema, com o prefixo
``PERFIL-`` nas mensagens (Seção 14), ex.: ``[ERRO] PERFIL-001 — ...``.
"""

from __future__ import annotations

import re

from ppcgen.config import Perfil
from ppcgen.modelos import AlertaValidacao, ErroValidacao, ResultadoValidacao

_ID_VALIDO = re.compile(r"^[a-z0-9_]+$")

_PASTAS_FICHAS = ("obrigatorias", "optativas", "extensao", "tcc", "estagio", "complementares")


def validar_perfil(perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()

    if not _ID_VALIDO.match(perfil.info.id):
        resultado.adicionar(
            ErroValidacao(
                "PERFIL-000",
                f"identificador de perfil '{perfil.info.id}' inválido — use apenas "
                "letras minúsculas, números e '_', sem espaços ou acentos.",
            )
        )
    elif perfil.info.id.startswith("00"):
        resultado.adicionar(
            ErroValidacao(
                "PERFIL-000",
                f"identificador de perfil '{perfil.info.id}' inválido — o prefixo "
                "'00' é reservado para material de referência mantido manualmente "
                "em saida/ (ex.: saida/00old/, ignorado por `ppcgen limpar --todos`).",
            )
        )

    caminho_matriz = perfil.resolver_arquivo(perfil.arquivos.matriz)
    if caminho_matriz is None:
        resultado.adicionar(
            ErroValidacao(
                "PERFIL-001",
                f"arquivo {perfil.arquivos.matriz} não localizado (nem no perfil, nem "
                "no perfil base, se houver).",
            )
        )

    if perfil.info.extends:
        if perfil.perfil_base is None:
            resultado.adicionar(
                ErroValidacao(
                    "PERFIL-002",
                    f"perfil base '{perfil.info.extends}' não existe.",
                )
            )

    for nome_capitulo in perfil.arquivos.capitulos:
        nome_arquivo = f"{nome_capitulo}.tex"
        caminho = perfil.resolver_arquivo(f"{perfil.arquivos.textos}/{nome_arquivo}")
        if caminho is None:
            resultado.adicionar(
                AlertaValidacao(
                    "PERFIL-003",
                    f"o capítulo '{nome_arquivo}' não foi localizado em "
                    f"{perfil.arquivos.textos}/.",
                )
            )
        elif caminho.stat().st_size == 0:
            resultado.adicionar(
                AlertaValidacao(
                    "PERFIL-003",
                    f"o capítulo {nome_arquivo} está vazio.",
                )
            )

    pasta_fichas_optativas = perfil.diretorio / perfil.arquivos.fichas / "optativas"
    tem_optativas = pasta_fichas_optativas.exists() and any(pasta_fichas_optativas.iterdir())
    if perfil.perfil_base is not None and not tem_optativas:
        pasta_base = perfil.perfil_base.diretorio / perfil.perfil_base.arquivos.fichas / "optativas"
        tem_optativas = pasta_base.exists() and any(pasta_base.iterdir())
    if not tem_optativas:
        resultado.adicionar(AlertaValidacao("PERFIL-004", "nenhuma ficha optativa foi localizada."))

    for sub in _PASTAS_FICHAS:
        pasta = perfil.diretorio / perfil.arquivos.fichas / sub
        if not pasta.exists() and perfil.perfil_base is None:
            resultado.adicionar(
                AlertaValidacao(
                    "PERFIL-006",
                    f"pasta de fichas '{perfil.arquivos.fichas}/{sub}' não existe.",
                )
            )

    if perfil.geracao.template != "padrao":
        from ppcgen.utilitarios.caminhos import raiz_projeto

        pasta_template = raiz_projeto() / "templates" / "latex" / perfil.geracao.template
        if not pasta_template.exists():
            resultado.adicionar(
                ErroValidacao(
                    "PERFIL-008",
                    f"template '{perfil.geracao.template}' não existe em templates/latex/.",
                )
            )

    return resultado
