"""Validações de identificação dos componentes curriculares (Seção 9).

Cada função recebe o :class:`~ppcgen.modelos.Curriculo` já carregado e
devolve um :class:`~ppcgen.modelos.ResultadoValidacao` — nunca lança exceção
por um problema de dado (isso é papel do leitor, para formatos realmente
inválidos); aqui tudo vira ERRO/ALERTA/INFORMACAO reportável.
"""

from __future__ import annotations

import re
from collections import Counter

from ppcgen.config import Perfil
from ppcgen.modelos import (
    AlertaValidacao,
    Curriculo,
    ErroValidacao,
    InformacaoValidacao,
    ResultadoValidacao,
)
from ppcgen.utilitarios.textos import slug

_CODIGO_VALIDO = re.compile(r"^[A-Za-z0-9_!?\-]+$")


def validar_codigos(curriculo: Curriculo, perfil: Perfil) -> ResultadoValidacao:
    resultado = ResultadoValidacao()

    contagem_codigos = Counter(c.codigo for c in curriculo.componentes)
    for codigo, qtd in contagem_codigos.items():
        if qtd > 1:
            resultado.adicionar(
                ErroValidacao(
                    "CODIGO_DUPLICADO",
                    f"código '{codigo}' aparece {qtd} vezes na matriz curricular.",
                    componente=codigo,
                )
            )

    contagem_nomes = Counter(slug(c.nome) for c in curriculo.componentes if c.nome)
    nomes_duplicados = {n for n, qtd in contagem_nomes.items() if qtd > 1}

    for c in curriculo.componentes:
        if not c.nome.strip():
            resultado.adicionar(
                ErroValidacao("NOME_OBRIGATORIO", "componente sem nome.", componente=c.codigo)
            )
        elif slug(c.nome) in nomes_duplicados:
            resultado.adicionar(
                AlertaValidacao(
                    "NOME_DUPLICADO",
                    f"nome '{c.nome}' repetido em mais de um componente — confirme se é "
                    "intencional (ex.: pool de optativas genéricas).",
                    componente=c.codigo,
                )
            )

        if not _CODIGO_VALIDO.match(c.codigo):
            resultado.adicionar(
                ErroValidacao(
                    "CODIGO_CARACTERES_INVALIDOS",
                    f"código '{c.codigo}' contém caracteres fora do padrão esperado "
                    "(letras, números, '_', '-', '!', '?').",
                    componente=c.codigo,
                )
            )

        if c.codigo_provisorio or "?" in c.codigo or "!" in c.codigo:
            resultado.adicionar(
                AlertaValidacao(
                    "CODIGO_PROVISORIO",
                    f"código '{c.codigo}' parece provisório (contém '?'/'!' ou está "
                    "marcado como tal) — deve ser substituído pelo código oficial antes "
                    "da aprovação do PPC.",
                    componente=c.codigo,
                )
            )

        if '"' in c.nome:
            resultado.adicionar(
                InformacaoValidacao(
                    "NOME_COM_ASPAS",
                    f"nome de '{c.codigo}' contém aspas — verifique se não é artefato de "
                    "exportação.",
                    componente=c.codigo,
                )
            )

        if c.periodo is not None and not (1 <= c.periodo <= perfil.curso.numero_periodos):
            resultado.adicionar(
                ErroValidacao(
                    "PERIODO_FORA_DO_INTERVALO",
                    f"período {c.periodo} fora do intervalo configurado "
                    f"(1..{perfil.curso.numero_periodos}).",
                    componente=c.codigo,
                    campo="periodo",
                )
            )

    return resultado
