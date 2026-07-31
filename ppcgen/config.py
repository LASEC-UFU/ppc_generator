"""Carregamento de perfis de PPC (``perfil.yaml``).

Um **perfil** é o conjunto completo e autocontido de dados necessários para
gerar uma versão específica de um PPC (um curso, uma versão curricular, uma
proposta alternativa...). Nada específico de um curso vive no código — tudo
vem do `perfil.yaml` do perfil selecionado, mais os dados compartilhados que
ele declarar explicitamente em `heranca:` (Seção 8) e, opcionalmente, de um
perfil base declarado em `extends:` (Seção 9).

Prioridade de valores (Seção 9):

    1. valores definidos no perfil atual
    2. valores herdados do perfil base (``extends``)
    3. valores compartilhados (``heranca``)
    4. valores padrão do sistema (defaults das dataclasses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ppcgen.excecoes import ConfiguracaoInvalida
from ppcgen.modelos import ReferencialCurricular
from ppcgen.utilitarios.caminhos import raiz_projeto


@dataclass
class InfoPerfil:
    id: str
    nome: str = ""
    status: str = "rascunho"
    versao: str = ""
    descricao: str = ""
    extends: str | None = None
    origem_clonagem: str | None = None
    """Id do perfil de onde este foi clonado (``ppcgen perfil-clonar``), só
    para rastreabilidade — não afeta carregamento nem herança."""


@dataclass
class CursoConfig:
    nome: str = ""
    nome_curto: str = ""
    sigla: str = ""
    grau: str = ""
    modalidade: str = ""
    turno: str = ""
    regime_academico: str = ""
    numero_periodos: int = 8
    campus: str = ""
    municipio: str = ""
    estado: str = ""


@dataclass
class InstituicaoConfig:
    nome: str = ""
    sigla: str = ""
    unidade_academica: str = ""
    extra: dict = field(default_factory=dict)
    """Campos institucionais adicionais vindos de ``heranca`` (endereço, CEP,
    site, telefone...) que o código genérico não precisa conhecer
    individualmente — os templates acessam por nome (ex.: ``extra.site``)."""


@dataclass
class CurriculoConfig:
    carga_horaria_total: int | None = None
    carga_obrigatoria: int | None = None
    carga_optativa_minima: int | None = None
    carga_extensao: int | None = None
    carga_aac: int | None = None
    carga_estagio: int | None = None
    carga_tcc: int | None = None
    percentual_minimo_extensao: float | None = None
    """Em pontos percentuais (0-100), não fração — ex.: ``10`` = 10%."""
    percentual_maximo_ead: float | None = None
    carga_horaria_maxima_periodo: int | None = None
    periodo_minimo_tcc: int | None = None
    periodo_minimo_estagio: int | None = None


@dataclass
class OfertaConfig:
    """Formato de oferta do curso (Decreto nº 12.456/2025) — decisão
    explícita do perfil, nunca inferida automaticamente do percentual de
    EaD (``curriculo.percentual_maximo_ead``, que continua sendo a única
    fonte da carga horária em si)."""

    formato: str = "presencial"
    """``presencial`` | ``semipresencial`` | ``distancia`` — nunca termos
    como "híbrido"/"remoto"/"flexível" (esses cabem só como descrição
    pedagógica em prosa, não aqui)."""
    possui_carga_ead: bool = False
    norma_federal: str = ""
    norma_institucional: str | None = None
    status_validacao_institucional: str = "pendente"
    """``pendente`` | ``confirmado`` — ``pendente`` enquanto
    ``norma_institucional`` não estiver preenchida com um ato publicado."""


@dataclass
class ArquivosConfig:
    matriz: str = "matriz_curricular.xlsx"
    bibliografia: str = "referencias/bibliografia.bib"
    textos: str = "textos"
    fichas: str = "fichas"
    figuras: str = "figuras"
    anexos: str = "anexos"
    frontmatter: str = "frontmatter"
    overrides: str = "overrides"


@dataclass
class GeracaoConfig:
    template: str = "padrao"
    anexar_fichas: bool = True
    anexar_resolucoes: bool = True
    gerar_fluxo_curricular: bool = True
    gerar_representacao_grafica: bool = True
    gerar_relatorio_validacao: bool = True
    compilar_pdf: bool = True
    interromper_em_erro: bool = True


@dataclass
class SaidaConfig:
    nome_base: str = "PPC"
    gerar_corpo: bool = True
    gerar_completo: bool = True


@dataclass
class HerancaConfig:
    instituicao: str | None = None
    unidade: str | None = None
    identidade_visual: str | None = None
    autoridades: str | None = None
    referencias: list[str] = field(default_factory=list)


@dataclass
class Perfil:
    info: InfoPerfil
    curso: CursoConfig
    instituicao: InstituicaoConfig
    curriculo: CurriculoConfig
    oferta: OfertaConfig
    arquivos: ArquivosConfig
    geracao: GeracaoConfig
    saida: SaidaConfig
    heranca: HerancaConfig
    diretorio: Path
    raiz_dados: Path
    legislacao: list[ReferencialCurricular] = field(default_factory=list)
    """Catálogo de referenciais legais deste perfil — substitui o antigo
    ``referenciais/legislacao.yaml`` (e o ``heranca.legislacao`` que
    apontava para arquivos compartilhados): tudo fica direto em
    ``perfil.yaml`` agora, sem arquivo externo para editar em separado."""
    perfil_base: "Perfil | None" = None
    _bruto_efetivo: dict = field(default_factory=dict, repr=False)

    def caminho(self, relativo: str) -> Path:
        """Resolve um caminho declarado em ``arquivos`` relativo à pasta do
        perfil. Rejeita caminhos que escapem da pasta do perfil (Seção 21) —
        compartilhamento entre perfis só é permitido explicitamente, via
        ``heranca``/``caminho_compartilhado``.
        """

        candidato = (self.diretorio / relativo).resolve()
        raiz = self.diretorio.resolve()
        if raiz not in candidato.parents and candidato != raiz:
            raise ConfiguracaoInvalida(
                f"Caminho '{relativo}' do perfil '{self.info.id}' escapa da sua própria "
                "pasta — use `heranca` para compartilhar arquivos entre perfis (Seção 21)."
            )
        return self.diretorio / relativo

    def resolver_arquivo(self, relativo: str) -> Path | None:
        """Procura ``relativo`` no perfil atual e, se ausente, no perfil base
        (``extends``), recursivamente. Retorna ``None`` se não encontrado em
        nenhum nível — nunca levanta exceção (quem chama decide a severidade).
        """

        caminho = self.caminho(relativo)
        if caminho.exists():
            return caminho
        if self.perfil_base is not None:
            return self.perfil_base.resolver_arquivo(relativo)
        return None

    def caminho_compartilhado(self, relativo: str) -> Path:
        """Resolve um caminho declarado em ``heranca`` relativo a ``dados/``."""

        return self.raiz_dados / relativo


def _merge_dict(base: dict, sobre: dict) -> dict:
    """Mescla recursiva: valores de ``sobre`` têm prioridade sobre ``base``."""

    resultado = dict(base)
    for chave, valor in sobre.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = _merge_dict(resultado[chave], valor)
        else:
            resultado[chave] = valor
    return resultado


def _ler_yaml(caminho: Path) -> dict:
    if not caminho.exists():
        raise ConfiguracaoInvalida(f"Arquivo compartilhado não encontrado: {caminho}")
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolver_heranca_config(heranca_bruta: dict, raiz_dados: Path) -> dict:
    """Carrega os YAML declarados em ``heranca.instituicao``/``heranca.unidade``
    e devolve um dict mesclável nos blocos de configuração do perfil (hoje,
    apenas ``instituicao``). Recursos ausentes geram erro claro (Seção 8):
    "o perfil deverá continuar válido... produzindo uma mensagem de erro
    clara" é satisfeito por ``ConfiguracaoInvalida`` apontando o arquivo.
    """

    combinado: dict = {}
    for chave in ("instituicao", "unidade"):
        caminho_rel = heranca_bruta.get(chave)
        if not caminho_rel:
            continue
        dados = _ler_yaml(raiz_dados / caminho_rel)
        combinado = _merge_dict(combinado, {"instituicao": dados.get("instituicao", {})})
    return combinado


def _extrair_extra_instituicao(dados: dict) -> dict:
    campos_conhecidos = {"nome", "sigla", "unidade_academica"}
    return {k: v for k, v in dados.items() if k not in campos_conhecidos}


def _construir(cls, dados: dict):
    campos_validos = set(cls.__dataclass_fields__)
    filtrado = {k: v for k, v in dados.items() if k in campos_validos}
    desconhecidos = set(dados) - campos_validos
    if desconhecidos:
        raise ConfiguracaoInvalida(
            f"Campo(s) desconhecido(s) em {cls.__name__}: {', '.join(sorted(desconhecidos))}"
        )
    return cls(**filtrado)


def _construir_lista(cls, itens: list):
    return [_construir(cls, item) for item in itens]


def _mesclar_por_id(base: list, atual: list) -> list:
    """Entradas do perfil atual sobrescrevem as do perfil base (``extends``,
    Seção 9) quando o ``id`` coincide; o restante é concatenado."""

    por_id = {item.id: item for item in base}
    for item in atual:
        por_id[item.id] = item
    return list(por_id.values())


def carregar_perfil(
    perfil_dir: str | Path,
    *,
    raiz_dados: Path | None = None,
    _pilha: tuple[str, ...] = (),
) -> Perfil:
    """Carrega um perfil a partir da sua pasta (``dados/perfis/<id>/``)."""

    perfil_dir = Path(perfil_dir)
    if not perfil_dir.is_absolute():
        perfil_dir = raiz_projeto() / perfil_dir
    caminho_yaml = perfil_dir / "perfil.yaml"
    if not caminho_yaml.exists():
        raise ConfiguracaoInvalida(f"perfil.yaml não encontrado em {perfil_dir}")

    bruto = _ler_yaml(caminho_yaml)
    info_bruta = bruto.get("perfil") or {}
    if "id" not in info_bruta:
        raise ConfiguracaoInvalida(f"{caminho_yaml}: seção 'perfil' deve declarar um 'id'.")
    perfil_id = info_bruta["id"]

    if perfil_id in _pilha:
        raise ConfiguracaoInvalida(
            "Herança circular de perfis detectada: " + " -> ".join((*_pilha, perfil_id))
        )

    raiz_dados = raiz_dados or perfil_dir.parent.parent

    perfil_base: Perfil | None = None
    extends_id = info_bruta.get("extends")
    base_efetivo: dict = {}
    if extends_id:
        base_dir = raiz_dados / "perfis" / extends_id
        if not base_dir.exists():
            raise ConfiguracaoInvalida(
                f"Perfil base '{extends_id}' (declarado em '{perfil_id}') não existe em {base_dir}."
            )
        perfil_base = carregar_perfil(base_dir, raiz_dados=raiz_dados, _pilha=(*_pilha, perfil_id))
        base_efetivo = perfil_base._bruto_efetivo

    heranca_bruta = bruto.get("heranca") or {}
    compartilhado = _resolver_heranca_config(heranca_bruta, raiz_dados)

    efetivo: dict = {}
    efetivo = _merge_dict(efetivo, compartilhado)
    efetivo = _merge_dict(efetivo, base_efetivo)
    efetivo = _merge_dict(efetivo, bruto)

    instituicao_dados = dict(efetivo.get("instituicao") or {})
    instituicao_extra = _extrair_extra_instituicao(instituicao_dados)

    legislacao = _mesclar_por_id(
        _construir_lista(ReferencialCurricular, base_efetivo.get("legislacao") or []),
        _construir_lista(ReferencialCurricular, bruto.get("legislacao") or []),
    )

    perfil = Perfil(
        info=_construir(InfoPerfil, info_bruta),
        curso=_construir(CursoConfig, efetivo.get("curso") or {}),
        instituicao=InstituicaoConfig(
            nome=instituicao_dados.get("nome", ""),
            sigla=instituicao_dados.get("sigla", ""),
            unidade_academica=instituicao_dados.get("unidade_academica", ""),
            extra=instituicao_extra,
        ),
        curriculo=_construir(CurriculoConfig, efetivo.get("curriculo") or {}),
        oferta=_construir(OfertaConfig, efetivo.get("oferta") or {}),
        arquivos=_construir(ArquivosConfig, efetivo.get("arquivos") or {}),
        geracao=_construir(GeracaoConfig, efetivo.get("geracao") or {}),
        saida=_construir(SaidaConfig, efetivo.get("saida") or {}),
        heranca=_construir(HerancaConfig, heranca_bruta or (base_efetivo.get("heranca") or {})),
        diretorio=perfil_dir,
        raiz_dados=raiz_dados,
        legislacao=legislacao,
        perfil_base=perfil_base,
        _bruto_efetivo=efetivo,
    )
    return perfil
