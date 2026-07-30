"""Exceções específicas do ppcgen.

Usar exceções nomeadas (em vez de ``Exception`` genérica) permite que a CLI
decida o código de saída correto e que os chamadores tratem cada categoria de
falha de forma diferenciada.
"""

from __future__ import annotations


class PPCGenError(Exception):
    """Erro base de todas as exceções do ppcgen."""


class ConfiguracaoInvalida(PPCGenError):
    """O arquivo de configuração do curso é inválido ou está incompleto."""


class ArquivoNaoEncontrado(PPCGenError):
    """Um arquivo esperado (matriz, ficha, referencial etc.) não foi encontrado."""


class FormatoInvalido(PPCGenError):
    """O conteúdo de um arquivo não está no formato esperado pelo leitor."""


class CompilacaoLatexFalhou(PPCGenError):
    """A compilação do LaTeX (pdflatex/latexmk) retornou erro."""
