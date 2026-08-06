"""Utilitários de normalização de texto usados pelos geradores."""

from __future__ import annotations

import re
from dataclasses import dataclass

from unidecode import unidecode


def slug(texto: str) -> str:
    """Normaliza um texto para uso como nome de arquivo/label LaTeX.

    Equivalente ao padrão usado no script legado
    (``unidecode(nome).replace(" ", "_").lower()``), mas centralizado e
    também removendo pontuação que antes era tratada caso a caso.
    """

    texto = unidecode(texto)
    texto = texto.replace(" e ", " ").replace(" de ", " ").replace(" da ", " ")
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = texto.strip().replace(" ", "_")
    return texto.lower()


def ordinal(numero: int) -> str:
    """Formata um número de período como ordinal em português (ex.: ``3º``)."""

    return f"{numero}\\textordmasculine{{}}"


def texto_ou_travessao(valor: int | None, simbolo: str = "--") -> str:
    """Formata uma carga horária opcional, usando ``simbolo`` quando ausente."""

    return simbolo if valor is None else str(valor)


_PADRAO_PREFIXO_ENFASE = re.compile(r"^([A-ZÀ-ÖØ-Þ]{2,15})\s+(\S+)\s*:\s*(.*)$")


@dataclass
class PrefixoEnfaseFormativa:
    """Resultado do reconhecimento do padrão ``SIGLA NÚMERO: Nome`` no nome
    de um componente curricular — ver :func:`analisar_prefixo_enfase_formativa`."""

    sigla: str
    numero_bruto: str
    nome_disciplina: str

    @property
    def numero_valido(self) -> int | None:
        """``None`` quando ``numero_bruto`` não é um inteiro positivo (ex.:
        ``"0"``, ``"-1"``, ``"I"``, texto arbitrário) — zero, negativos e
        algarismos romanos são deliberadamente rejeitados aqui."""

        if self.numero_bruto.isdigit() and int(self.numero_bruto) > 0:
            return int(self.numero_bruto)
        return None


def analisar_prefixo_enfase_formativa(nome: str) -> PrefixoEnfaseFormativa | None:
    """Reconhece a FORMA ``"SIGLA TOKEN: resto"`` num nome de componente
    curricular (ex.: ``"MIAPI 1: Máquinas Elétricas Inteligentes"``) — usada
    para vincular o componente à sua Ênfase Formativa (áreas de formação
    optativa) sem precisar de nenhum cadastro separado do vínculo.

    Não valida se a sigla existe no catálogo ``EnfasesFormativas`` nem se o
    token numérico é um número de ênfase válido (ver
    :attr:`PrefixoEnfaseFormativa.numero_valido`) — isso é responsabilidade
    de quem chama: o leitor (``ppcgen.leitores.excel``) só vincula no caso
    100% válido; o validador (``ppcgen.validadores.enfases_formativas``)
    reaplica esta mesma função para reportar os problemas finos (sigla
    inexistente, número inválido, nome ausente) sem duplicar o regex.

    Retorna ``None`` quando o nome não tem essa forma — a maioria das
    disciplinas comuns, sem prefixo de ênfase, cai aqui e nunca é tratada
    como erro.
    """

    casamento = _PADRAO_PREFIXO_ENFASE.match(nome.strip())
    if not casamento:
        return None
    sigla, numero_bruto, resto = casamento.groups()
    return PrefixoEnfaseFormativa(sigla=sigla, numero_bruto=numero_bruto, nome_disciplina=resto.strip())
