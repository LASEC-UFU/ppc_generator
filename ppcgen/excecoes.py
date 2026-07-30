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


class ReferenciaInexistente(PPCGenError):
    """Um identificador referenciado (código, núcleo, competência...) não existe."""


class ValidacaoFalhou(PPCGenError):
    """A validação curricular encontrou ao menos um erro crítico.

    Carrega o :class:`~ppcgen.modelos.ResultadoValidacao` para que o chamador
    (CLI ou outro módulo) possa inspecionar e reportar os erros específicos.
    """

    def __init__(self, resultado):
        self.resultado = resultado
        super().__init__(
            f"Validação falhou com {len(resultado.erros)} erro(s) crítico(s)."
        )


class CicloDePrerequisitos(PPCGenError):
    """Foi detectado um ciclo no grafo de pré-requisitos."""

    def __init__(self, caminho: list[str]):
        self.caminho = caminho
        super().__init__("Ciclo de pré-requisitos: " + " → ".join(caminho))


class CompilacaoLatexFalhou(PPCGenError):
    """A compilação do LaTeX (pdflatex/latexmk) retornou erro."""
