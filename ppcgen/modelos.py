"""Modelos de domínio do ppcgen.

Nenhum destes modelos conhece regras de um curso específico (Engenharia de
Computação, CST em Controle e Automação etc.) — os valores permitidos para
núcleos, áreas, temas e conteúdos vêm das abas de registro da matriz
curricular (ver :mod:`ppcgen.leitores.excel`), e legislação/competências
vêm de ``perfil.yaml`` (ver :mod:`ppcgen.config`); nada é fixado aqui.

Convenções:

- Cargas horárias ausentes/indefinidas são representadas por ``None``, nunca
  por sentinelas negativas (ex.: ``-1``).
- Listas mutáveis usam ``field(default_factory=list)``, nunca um literal
  mutável como valor padrão.
- ``ErroValidacao`` e ``AlertaValidacao`` (citados na especificação) são
  fábricas de conveniência sobre :class:`MensagemValidacao`, evitando duas
  classes quase idênticas divergirem com o tempo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TipoComponente(str, Enum):
    """Natureza estrutural de um componente curricular.

    O comportamento de geração/validação deve depender deste campo — nunca de
    prefixos ou sufixos de código (ex.: não usar ``codigo.startswith("AAC")``).
    """

    DISCIPLINA = "disciplina"
    PROJETO_INTEGRADOR = "projeto_integrador"
    EXTENSAO = "extensao"
    ESTAGIO = "estagio"
    TCC = "tcc"
    ATIVIDADE_COMPLEMENTAR = "atividade_complementar"
    CARGA_OPTATIVA = "carga_optativa"
    CERTIFICACAO = "certificacao"
    OUTRO = "outro"


class Severidade(str, Enum):
    ERRO = "erro"
    ALERTA = "alerta"
    INFORMACAO = "informacao"


class StatusFicha(str, Enum):
    LOCALIZADA_CONSISTENTE = "localizada_consistente"
    LOCALIZADA_DIVERGENTE = "localizada_divergente"
    AUSENTE = "ausente"
    NAO_RECONHECIDA = "nao_reconhecida"
    DUPLICADA = "duplicada"
    CURRICULO_ANTERIOR = "curriculo_anterior"


# ---------------------------------------------------------------------------
# Carga horária
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CargaHoraria:
    """Carga horária de um componente, particionada por modalidade.

    Qualquer parcela não informada é ``None`` (não ``0`` e não ``-1``): ``0``
    significa "informado como zero horas", ``None`` significa "não
    informado/não aplicável".
    """

    teorica: int | None = None
    pratica: int | None = None
    ead: int | None = None
    extensao: int | None = None
    total: int | None = None

    def soma_parcelas(self) -> int | None:
        partes = [self.teorica, self.pratica, self.ead, self.extensao]
        informadas = [p for p in partes if p is not None]
        if not informadas:
            return None
        return sum(informadas)


# ---------------------------------------------------------------------------
# Referenciais (núcleos, áreas, competências, temas, legislação)
# ---------------------------------------------------------------------------


@dataclass
class NucleoCurricular:
    id: str
    nome: str
    descricao: str = ""


@dataclass
class AreaFormacao:
    id: str
    nome: str
    descricao: str = ""


@dataclass
class Competencia:
    id: str
    descricao: str
    obrigatoria: bool = False
    fonte: str = ""


@dataclass
class Conteudo:
    """Conteúdo curricular específico exigido por um referencial (ex.: um
    item de uma DCN) — Seção 3. Análogo a :class:`Competencia`, mas para
    conteúdos programáticos em vez de competências profissionais; os dois
    são mantidos como modelos separados porque referenciais distintos podem
    exigir um sem exigir o outro.
    """

    id: str
    descricao: str
    obrigatorio: bool = False
    fonte: str = ""


@dataclass
class ReferencialCurricular:
    id: str
    nome: str
    tipo: str = ""
    documento: str = ""
    ano: int | None = None
    observacoes: str = ""


@dataclass
class TemaTransversal:
    id: str
    nome: str
    descricao: str = ""
    fonte_normativa: str = ""
    status: str = "ativo"


@dataclass
class ReferenciaisCurso:
    """Conjunto completo de referenciais configurados para o curso ativo.

    ``nucleos``/``areas``/``temas_transversais``/``conteudos`` vêm das abas
    de registro da matriz curricular (``ppcgen.leitores.excel``);
    ``legislacao``/``competencias`` vêm diretamente de ``perfil.yaml``
    (``Perfil.legislacao``/``Perfil.competencias``) — nenhum dos dois lê
    mais arquivos YAML separados em ``referenciais/``."""

    nucleos: list[NucleoCurricular] = field(default_factory=list)
    areas: list[AreaFormacao] = field(default_factory=list)
    competencias: list[Competencia] = field(default_factory=list)
    conteudos: list[Conteudo] = field(default_factory=list)
    legislacao: list[ReferencialCurricular] = field(default_factory=list)
    temas_transversais: list[TemaTransversal] = field(default_factory=list)

    def ids_nucleos(self) -> set[str]:
        return {n.id for n in self.nucleos}

    def ids_areas(self) -> set[str]:
        return {a.id for a in self.areas}

    def ids_competencias(self) -> set[str]:
        return {c.id for c in self.competencias}

    def ids_conteudos(self) -> set[str]:
        return {c.id for c in self.conteudos}

    def ids_temas(self) -> set[str]:
        return {t.id for t in self.temas_transversais}


# ---------------------------------------------------------------------------
# Requisitos e equivalências
# ---------------------------------------------------------------------------


@dataclass
class PreRequisito:
    codigo: str
    opcional: bool = False
    carga_horaria_minima: int | None = None


@dataclass
class Correquisito:
    codigo: str
    opcional: bool = False


@dataclass
class Equivalencia:
    codigo_origem: str
    codigo_destino: str
    observacao: str = ""


# ---------------------------------------------------------------------------
# Componente curricular e currículo
# ---------------------------------------------------------------------------


@dataclass
class ComponenteCurricular:
    codigo: str
    nome: str
    tipo: TipoComponente
    carga_horaria: CargaHoraria = field(default_factory=CargaHoraria)
    periodo: int | None = None
    ativo: bool = True
    obrigatorio: bool = False
    codigo_provisorio: bool = False
    nucleo: str | None = None
    areas: list[str] = field(default_factory=list)
    competencias: list[str] = field(default_factory=list)
    conteudos: list[str] = field(default_factory=list)
    temas_transversais: list[str] = field(default_factory=list)
    pre_requisitos: list[PreRequisito] = field(default_factory=list)
    correquisitos: list[Correquisito] = field(default_factory=list)
    unidade_oferta: str = ""
    observacoes: str = ""

    @property
    def carga_total(self) -> int:
        return self.carga_horaria.total or 0


@dataclass
class Curriculo:
    versao: str
    componentes: list[ComponenteCurricular] = field(default_factory=list)
    equivalencias: list[Equivalencia] = field(default_factory=list)

    def por_codigo(self) -> dict[str, ComponenteCurricular]:
        return {c.codigo: c for c in self.componentes}

    def ativos(self) -> list[ComponenteCurricular]:
        return [c for c in self.componentes if c.ativo]

    def carga_horaria_total(self) -> int:
        return sum(c.carga_total for c in self.ativos())


# ---------------------------------------------------------------------------
# Fichas curriculares
# ---------------------------------------------------------------------------


@dataclass
class FichaCurricular:
    codigo: str
    nome: str = ""
    carga_horaria: CargaHoraria | None = None
    pre_requisitos: list[str] = field(default_factory=list)
    ementa: str = ""
    objetivos: str = ""
    programa: str = ""
    metodologia: str = ""
    avaliacao: str = ""
    bibliografia_basica: str = ""
    bibliografia_complementar: str = ""
    arquivo_origem: Path | None = None
    formato_origem: str = ""
    confianca_extracao: float = 1.0


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------


@dataclass
class MensagemValidacao:
    severidade: Severidade
    codigo_regra: str
    mensagem: str
    componente: str | None = None
    campo: str | None = None


def ErroValidacao(
    codigo_regra: str, mensagem: str, componente: str | None = None, campo: str | None = None
) -> MensagemValidacao:
    """Fábrica de uma :class:`MensagemValidacao` de severidade ERRO."""

    return MensagemValidacao(Severidade.ERRO, codigo_regra, mensagem, componente, campo)


def AlertaValidacao(
    codigo_regra: str, mensagem: str, componente: str | None = None, campo: str | None = None
) -> MensagemValidacao:
    """Fábrica de uma :class:`MensagemValidacao` de severidade ALERTA."""

    return MensagemValidacao(Severidade.ALERTA, codigo_regra, mensagem, componente, campo)


def InformacaoValidacao(
    codigo_regra: str, mensagem: str, componente: str | None = None, campo: str | None = None
) -> MensagemValidacao:
    """Fábrica de uma :class:`MensagemValidacao` de severidade INFORMACAO."""

    return MensagemValidacao(Severidade.INFORMACAO, codigo_regra, mensagem, componente, campo)


@dataclass
class ResultadoValidacao:
    mensagens: list[MensagemValidacao] = field(default_factory=list)

    def adicionar(self, mensagem: MensagemValidacao) -> None:
        self.mensagens.append(mensagem)

    @property
    def erros(self) -> list[MensagemValidacao]:
        return [m for m in self.mensagens if m.severidade == Severidade.ERRO]

    @property
    def alertas(self) -> list[MensagemValidacao]:
        return [m for m in self.mensagens if m.severidade == Severidade.ALERTA]

    @property
    def informacoes(self) -> list[MensagemValidacao]:
        return [m for m in self.mensagens if m.severidade == Severidade.INFORMACAO]

    @property
    def tem_erro(self) -> bool:
        return len(self.erros) > 0

    def mesclar(self, outro: "ResultadoValidacao") -> None:
        self.mensagens.extend(outro.mensagens)
