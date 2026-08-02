"""Carregamento de perfis de PPC (aba ``Perfil`` da matriz curricular).

Um **perfil** é o conjunto completo e autocontido de dados necessários para
gerar uma versão específica de um PPC (um curso, uma versão curricular, uma
proposta alternativa...). Nada específico de um curso vive no código — tudo
vem da aba ``Perfil`` de ``matriz_curricular.xlsx``/``.xlsm`` do perfil
selecionado (não existe mais ``perfil.yaml``), opcionalmente combinado com
um perfil base declarado em `extends:` (Seção 9).

Prioridade de valores (Seção 9):

    1. valores definidos no perfil atual
    2. valores herdados do perfil base (``extends``)
    3. valores padrão do sistema (defaults das dataclasses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ppcgen.excecoes import ConfiguracaoInvalida
from ppcgen.leitores.excel import ler_configuracao_perfil
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
    nome_mercadologico: str = ""
    """Nome de divulgação institucional (portal, comunicação ao público) —
    distinto de ``nome``, a denominação regulatória perante MEC/INEP, que
    continua sendo a única usada para fins normativos (CNCST etc.)."""
    enfase_curricular: str = ""
    """Linha formativa/ênfase do curso — texto curto que qualifica ``nome``
    sem alterar a denominação regulatória em si."""
    titulacao_conferida: str = ""
    tempo_minimo_integralizacao: str = ""
    tempo_maximo_integralizacao: str = ""
    vagas_ofertadas: str = ""
    eixo_tecnologico: str = ""
    area_tecnologica: str = ""
    codigo_cine: str = ""
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
    """Campos institucionais adicionais (endereço, CEP, site, telefone...)
    que o código genérico não precisa conhecer individualmente — os
    templates acessam por nome (ex.: ``extra.site``)."""


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
class CapaConfig:
    ano: int | None = None
    logo_curso: str = ""
    """Caminho (relativo à pasta do perfil, ex. ``figuras/logo.png``) da
    logomarca própria do curso exibida na capa — vazio omite a imagem
    (nem toda proposta tem uma logomarca aprovada ainda). Distinto do logo
    institucional da UFU, fixo no template e sempre exibido."""


@dataclass
class ComissaoConfig:
    titulo: str = "Equipe de elaboração deste Projeto Pedagógico"
    """Título da caixa de créditos na folha de rosto — os nomes dos
    membros vêm da aba ``Comissao`` (coluna ``membro``), não daqui."""


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


CAPITULOS_PADRAO: tuple[str, ...] = (
    "identificacao",
    "apresentacao",
    "justificativa",
    "principios",
    "perfil_egresso",
    "objetivos",
    "estrutura_curricular",
    "diretrizes_pedagogicas",
    "avaliacao",
    "atendimento_estudante",
    "acompanhamento_egresso",
    "consideracoes_finais",
)
"""Nomes (sem ``.tex``) dos capítulos do corpo do PPC, na ordem em que
entram no PDF — único lugar canônico dessa lista; ``ArquivosConfig.capitulos``
usa isto como default quando o perfil não declara ``arquivos.capitulos``
na aba ``Perfil``."""


@dataclass
class ArquivosConfig:
    matriz: str = "matriz_curricular.xlsx"
    textos: str = "textos"
    fichas: str = "fichas"
    figuras: str = "figuras"
    anexos: str = "anexos"
    overrides: str = "overrides"
    capitulos: list[str] = field(default_factory=lambda: list(CAPITULOS_PADRAO))
    """Nomes dos capítulos (sem ``.tex``, relativos a ``textos/``) e a
    ordem em que ``\\input`` entram no PDF — consumido por
    ``ppcgen.geradores.latex.gerar_capitulos_tex`` (gera ``gerado/capitulos.tex``,
    referenciado por ``templates/latex/Main.tex``) e por
    ``ppcgen.validadores.perfil`` (``PERFIL-003``)."""


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
class Perfil:
    info: InfoPerfil
    curso: CursoConfig
    instituicao: InstituicaoConfig
    curriculo: CurriculoConfig
    oferta: OfertaConfig
    capa: CapaConfig
    comissao: ComissaoConfig
    arquivos: ArquivosConfig
    geracao: GeracaoConfig
    saida: SaidaConfig
    diretorio: Path
    raiz_dados: Path
    perfil_base: "Perfil | None" = None
    _bruto_efetivo: dict = field(default_factory=dict, repr=False)

    def caminho(self, relativo: str) -> Path:
        """Resolve um caminho declarado em ``arquivos`` relativo à pasta do
        perfil. Rejeita caminhos que escapem da pasta do perfil (Seção 21) —
        perfis não compartilham arquivos entre si.
        """

        candidato = (self.diretorio / relativo).resolve()
        raiz = self.diretorio.resolve()
        if raiz not in candidato.parents and candidato != raiz:
            raise ConfiguracaoInvalida(
                f"Caminho '{relativo}' do perfil '{self.info.id}' escapa da sua própria pasta (Seção 21)."
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


def _merge_dict(base: dict, sobre: dict) -> dict:
    """Mescla recursiva: valores de ``sobre`` têm prioridade sobre ``base``."""

    resultado = dict(base)
    for chave, valor in sobre.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = _merge_dict(resultado[chave], valor)
        else:
            resultado[chave] = valor
    return resultado


NOMES_MATRIZ_PADRAO = ("matriz_curricular.xlsm", "matriz_curricular.xlsx")


def _localizar_matriz(pasta: Path) -> str | None:
    """Autodetecta o nome do arquivo de matriz numa pasta de perfil, quando
    não foi informado explicitamente (ex.: descoberta automática sem
    registro em ``dados/perfis.yaml`` — Seção 15)."""

    for nome in NOMES_MATRIZ_PADRAO:
        if (pasta / nome).exists():
            return nome
    return None


def _extrair_extra_instituicao(dados: dict) -> dict:
    campos_conhecidos = {"nome", "sigla", "unidade_academica"}
    return {k: v for k, v in dados.items() if k not in campos_conhecidos}


def _construir(cls, dados: dict):
    campos_validos = set(cls.__dataclass_fields__)
    filtrado = {}
    for chave, valor in dados.items():
        if chave not in campos_validos:
            continue
        campo = cls.__dataclass_fields__[chave]
        if campo.type == "list[str]" and isinstance(valor, str):
            # Célula única da aba `Perfil` com itens separados por `|` —
            # mesmo formato de `componentes`/`pre_requisitos` na matriz.
            valor = [item.strip() for item in valor.split("|") if item.strip()]
        filtrado[chave] = valor
    desconhecidos = set(dados) - campos_validos
    if desconhecidos:
        raise ConfiguracaoInvalida(f"Campo(s) desconhecido(s) em {cls.__name__}: {', '.join(sorted(desconhecidos))}")
    return cls(**filtrado)


_SECOES_PERFIL = frozenset(
    {"perfil", "curso", "instituicao", "curriculo", "oferta", "capa", "comissao", "arquivos", "geracao", "saida"}
)


def _validar_secoes_configuracao(dados: dict, caminho_matriz: Path) -> None:
    desconhecidas = set(dados) - _SECOES_PERFIL
    if desconhecidas:
        raise ConfiguracaoInvalida(
            f"Seção(ões) desconhecida(s) na aba 'Perfil' de {caminho_matriz}: {', '.join(sorted(desconhecidas))}."
        )


def carregar_perfil(
    perfil_dir: str | Path,
    *,
    raiz_dados: Path | None = None,
    matriz: str | None = None,
    _pilha: tuple[str, ...] = (),
) -> Perfil:
    """Carrega um perfil a partir da sua pasta (``dados/perfis/<id>/`` ou
    qualquer pasta registrada em ``dados/perfis.yaml``) — lê a aba
    ``Perfil`` do arquivo de matriz (nome em ``matriz``, vindo do registro;
    se omitido, autodetectado por ``_localizar_matriz``)."""

    perfil_dir = Path(perfil_dir)
    if not perfil_dir.is_absolute():
        perfil_dir = raiz_projeto() / perfil_dir

    nome_matriz = matriz or _localizar_matriz(perfil_dir)
    if nome_matriz is None:
        raise ConfiguracaoInvalida(f"Nenhum matriz_curricular.xlsm/.xlsx encontrado em {perfil_dir}")
    caminho_matriz = perfil_dir / nome_matriz
    if not caminho_matriz.exists():
        raise ConfiguracaoInvalida(f"Arquivo de matriz não encontrado: {caminho_matriz}")

    bruto = ler_configuracao_perfil(caminho_matriz)
    _validar_secoes_configuracao(bruto, caminho_matriz)
    info_bruta = bruto.get("perfil") or {}
    if "id" not in info_bruta:
        raise ConfiguracaoInvalida(f"{caminho_matriz}: aba 'Perfil' deve declarar 'perfil.id'.")
    perfil_id = info_bruta["id"]

    if perfil_id in _pilha:
        raise ConfiguracaoInvalida("Herança circular de perfis detectada: " + " -> ".join((*_pilha, perfil_id)))

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

    efetivo: dict = {}
    efetivo = _merge_dict(efetivo, base_efetivo)
    efetivo = _merge_dict(efetivo, bruto)

    instituicao_dados = dict(efetivo.get("instituicao") or {})
    instituicao_extra = _extrair_extra_instituicao(instituicao_dados)

    arquivos = _construir(ArquivosConfig, efetivo.get("arquivos") or {})
    arquivos.matriz = nome_matriz  # sempre o arquivo que acabou de ser lido, nunca vem da aba

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
        capa=_construir(CapaConfig, efetivo.get("capa") or {}),
        comissao=_construir(ComissaoConfig, efetivo.get("comissao") or {}),
        arquivos=arquivos,
        geracao=_construir(GeracaoConfig, efetivo.get("geracao") or {}),
        saida=_construir(SaidaConfig, efetivo.get("saida") or {}),
        diretorio=perfil_dir,
        raiz_dados=raiz_dados,
        perfil_base=perfil_base,
        _bruto_efetivo=efetivo,
    )
    return perfil
