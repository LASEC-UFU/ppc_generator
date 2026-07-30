"""Orquestra a geração de todos os arquivos LaTeX do corpo do PPC em
``saida/<perfil_id>/latex/gerado/`` a partir do currículo validado.

Todo arquivo escrito aqui recebe o aviso de "gerado automaticamente" (Seção
13) e nenhum deve ser editado manualmente — o conteúdo manual dos capítulos
vive em ``textos/`` dentro da pasta do perfil e apenas usa ``\\input`` para
trazer estes arquivos.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ppcgen.calculo import carga_horaria_oficial, carga_por_tipo, componentes_oficiais
from ppcgen.config import Perfil
from ppcgen.geradores.fluxo import gerar_tabela_fluxo
from ppcgen.geradores.representacao_grafica import gerar_representacao_grafica
from ppcgen.geradores.tabelas import (
    tabela_carga_por_grupo,
    tabela_componentes,
    tabela_equivalencias,
    tabela_prerequisitos,
    tabela_referencia,
)
from ppcgen.leitores.yaml import ReferenciaisCurso
from ppcgen.modelos import ComponenteCurricular, Curriculo, TipoComponente
from ppcgen.utilitarios.latex import cabecalho_gerado, escapar
from ppcgen.utilitarios.textos import slug


def _escrever(pasta: Path, nome_arquivo: str, corpo: str, fonte: str, versao: str) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome_arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(cabecalho_gerado(fonte, versao))
        f.write(corpo)
    return caminho


def _ler_yaml_opcional(caminho: Path | None) -> dict:
    if caminho is None or not caminho.exists():
        return {}
    return yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}


def gerar_frontmatter(perfil: Perfil) -> str:
    """Gera a capa e a folha de rosto (autoridades/comissão) a partir de
    ``frontmatter/{capa,autoridades,comissao}.yaml`` do perfil (com fallback
    para o perfil base, via ``extends``) e das autoridades institucionais
    compartilhadas (``heranca.autoridades``), sem exigir que o perfil escreva
    LaTeX à mão para isso — ``frontmatter/folha_rosto.tex`` continua
    disponível para conteúdo adicional livre (ver templates/latex/Main.tex).

    O layout replica o do template original (capa com faixa/logo
    institucional em margens reduzidas, rodapé com a unidade acadêmica e
    contato).
    """

    pasta_front = perfil.arquivos.frontmatter
    capa = _ler_yaml_opcional(perfil.resolver_arquivo(f"{pasta_front}/capa.yaml")).get("capa", {})
    autoridades_perfil = _ler_yaml_opcional(
        perfil.resolver_arquivo(f"{pasta_front}/autoridades.yaml")
    ).get("autoridades", [])
    comissao = _ler_yaml_opcional(perfil.resolver_arquivo(f"{pasta_front}/comissao.yaml")).get(
        "comissao", {}
    )

    autoridades_compartilhadas = []
    if perfil.heranca.autoridades:
        autoridades_compartilhadas = _ler_yaml_opcional(
            perfil.caminho_compartilhado(perfil.heranca.autoridades)
        ).get("autoridades", [])

    logo_tex = ""
    if capa.get("logo_curso"):
        logo_tex = rf"""
\begin{{figure}}[H]
\centering
\vspace{{0.5cm}}
\includegraphics[width=0.4\linewidth]{{{capa['logo_curso']}}}
\end{{figure}}"""

    ano = capa.get("ano", "")
    extra = perfil.instituicao.extra
    orgao_superior = extra.get("orgao_superior", "")
    unidade_sigla = extra.get("unidade_sigla", "")
    unidade_site = extra.get("unidade_site", "")
    uf = extra.get("uf") or perfil.curso.estado
    municipio_uf = f"{perfil.curso.municipio}/{uf}" if perfil.curso.municipio and uf else perfil.curso.municipio
    localizacao = f"Campus {perfil.curso.campus}, {municipio_uf}" if perfil.curso.campus else municipio_uf

    linha_orgao = rf"\textsc{{\footnotesize {escapar(orgao_superior)}}}\\" if orgao_superior else ""

    rodape_unidade = ""
    if perfil.instituicao.unidade_academica:
        titulo_unidade = escapar(perfil.instituicao.unidade_academica).upper()
        if unidade_sigla:
            titulo_unidade += f" ({escapar(unidade_sigla)})"
        linha_site = rf"\href{{{unidade_site}}}{{{unidade_site}}}" if unidade_site else ""
        rodape_unidade = rf"""
\begin{{center}}
\textcolor{{AzulEscuro}}{{\rule{{1.1\textwidth}}{{0.8pt}}}}\\[2mm]
\textcolor{{AzulEscuro}}{{\small\textbf{{{titulo_unidade}}}}}\\
\setlength{{\parskip}}{{1mm}}
{{\small {escapar(localizacao)}, Brasil {ano} \\
{linha_site}}}\vspace{{1.5cm}}
\end{{center}}"""

    linhas_autoridades = "\\\\\n".join(
        rf"\textsc{{\tiny {escapar(a['cargo'])}}} \\ \hspace*{{5mm}} \textbf{{{escapar(a['nome'])}}}"
        for a in (*autoridades_compartilhadas, *autoridades_perfil)
    )

    membros_comissao = comissao.get("membros", [])
    itens_comissao = "\n".join(
        rf"    \item {escapar(m)}{';' if i < len(membros_comissao) - 1 else '.'}"
        for i, m in enumerate(membros_comissao)
    )
    bloco_comissao = ""
    if itens_comissao:
        titulo_comissao = escapar(comissao.get("titulo", "Equipe de elaboração deste Projeto Pedagógico"))
        bloco_comissao = rf"""
\textbf{{{titulo_comissao}:}}
\begin{{itemize}}
\setlength\itemsep{{-0.5em}}
{itens_comissao}
\end{{itemize}}"""

    return rf"""\begin{{titlepage}}
\newgeometry{{top=3cm, bottom=0.0cm, left=2.25cm, right=2.25cm}}
\vtop{{
\null\vspace{{-25mm}}
\IfFileExists{{figuras/compartilhadas/header_pattern.jpg}}{{\centerline{{\includegraphics[width=1.18\textwidth,height=80pt]{{figuras/compartilhadas/header_pattern.jpg}}}}\vspace{{-2.3cm}}}}{{}}
\IfFileExists{{figuras/compartilhadas/logo_ufu.png}}{{\hbox{{\hspace{{0mm}}\includegraphics[height=18mm]{{figuras/compartilhadas/logo_ufu.png}}}}}}{{}}
\centerline{{\textcolor{{AzulEscuro}}{{\rule{{1.18\textwidth}}{{4pt}}}}}}
}}
\mbox{{}}
\begin{{center}}
{linha_orgao}
\textsc{{\footnotesize \ppcinstituicao\\\ppcunidadeacademica\\Curso de Graduação em \ppccurso}}
\end{{center}}
\mbox{{}}
\vfill
\vspace{{1cm}}
\begin{{center}}
\textbf{{{{\Huge Projeto Pedagógico de Curso}}}}
\end{{center}}
{logo_tex}
\vspace{{0.25cm}}
\begin{{center}}
\textbf{{{{\LARGE Graduação em \ppccurso}}}} \\[0.5cm]
Versão Curricular: \ppcversao
\end{{center}}
\vfill
{rodape_unidade}
\restoregeometry
\end{{titlepage}}

\newpage
\restoregeometry
\thispagestyle{{plain}}
\begin{{center}}
\textsc{{Projeto Pedagógico do Curso de Graduação em\\\ppccurso}}
\end{{center}}
\vfill
\begin{{center}}
\parbox{{0.8\textwidth}}{{
{linhas_autoridades}
}}
\end{{center}}
\vfill
{bloco_comissao}
\vfill
\centerline{{{escapar(municipio_uf)}, Brasil {ano}}}
"""


def gerar_arquivos_latex(
    curriculo: Curriculo,
    perfil: Perfil,
    referenciais: ReferenciaisCurso,
    pasta_gerado: Path,
) -> list[Path]:
    fonte = str(perfil.arquivos.matriz)
    versao = curriculo.versao
    gerados: list[Path] = []

    def escrever(nome_arquivo: str, corpo: str) -> None:
        gerados.append(_escrever(pasta_gerado, nome_arquivo, corpo, fonte, versao))

    ativos = curriculo.ativos()
    nomes_por_codigo = {c.codigo: c.nome for c in curriculo.componentes}

    # --- Macros de identificação do curso (Seção 14) -----------------------
    # Centraliza nome/versão/instituição em um único lugar gerado a partir de
    # perfil.yaml — os textos do perfil usam estas macros em vez de repetir
    # o nome do curso literalmente.
    curso = perfil.curso
    instituicao = perfil.instituicao
    macros = (
        rf"\newcommand{{\PerfilId}}{{{escapar(perfil.info.id)}}}" "\n"
        rf"\newcommand{{\ppccurso}}{{{escapar(curso.nome)}\xspace}}" "\n"
        rf"\newcommand{{\ppccursocurto}}{{{escapar(curso.nome_curto)}\xspace}}" "\n"
        rf"\newcommand{{\ppcversao}}{{{escapar(perfil.info.versao)}}}" "\n"
        rf"\newcommand{{\ppcgrau}}{{{escapar(curso.grau)}\xspace}}" "\n"
        rf"\newcommand{{\ppcmodalidade}}{{{escapar(curso.modalidade)}\xspace}}" "\n"
        rf"\newcommand{{\ppcinstituicao}}{{{escapar(instituicao.nome)}\xspace}}" "\n"
        rf"\newcommand{{\ppcunidadeacademica}}{{{escapar(instituicao.unidade_academica)}\xspace}}" "\n"
        rf"\newcommand{{\ppccampus}}{{{escapar(curso.campus)}\xspace}}" "\n"
        rf"\newcommand{{\ppcturno}}{{{escapar(curso.turno)}\xspace}}" "\n"
    )
    escrever("curso_macros.tex", macros)
    escrever("frontmatter.tex", gerar_frontmatter(perfil))

    # --- Fluxo curricular e representação gráfica -------------------------
    escrever("tab_fluxo_curricular.tex", gerar_tabela_fluxo(curriculo, perfil, nomes_por_codigo))
    if perfil.geracao.gerar_representacao_grafica:
        escrever("representacao_grafica.tex", gerar_representacao_grafica(curriculo, perfil))

    # Nota sobre optativas nas tabelas agregadas abaixo: o pool inteiro de
    # componentes tipo=carga_optativa soma mais horas do que o estudante de
    # fato cursa (ele escolhe um subconjunto). Por isso, nas tabelas de
    # carga por núcleo/área/modalidade, o grupo de optativas não é somado
    # componente a componente — ele entra uma única vez, com o valor de
    # ``curriculo.carga_optativa_minima`` (Seção 3/6) — mantendo os totais
    # consistentes com ``ppcgen.calculo.carga_horaria_oficial``. A listagem
    # completa do pool aparece à parte, em "Disciplinas Optativas
    # Pré-Aprovadas", sem linha de total (Seção 13).
    total_geral = carga_horaria_oficial(curriculo, perfil)
    optativa_minima = perfil.curriculo.carga_optativa_minima or 0
    # `oficiais`: população usada nos totais/percentuais (todo tipo exceto
    # optativa — ver ppcgen.calculo.componentes_oficiais). `obrigatorios`:
    # população da tabela "Componentes Curriculares Obrigatórios" — um
    # conceito distinto (o campo `obrigatorio`, não o `tipo`): um componente
    # de extensão pode contar no total oficial sem ser uma "disciplina
    # obrigatória" listada nessa tabela.
    oficiais = componentes_oficiais(curriculo)
    obrigatorios = [c for c in ativos if c.obrigatorio]

    # --- Tabelas por núcleo -------------------------------------------------
    por_nucleo: dict[str, list[ComponenteCurricular]] = {}
    for c in ativos:
        por_nucleo.setdefault(c.nucleo or "sem_nucleo", []).append(c)

    nomes_nucleo = {n.id: n.nome for n in referenciais.nucleos}
    for nucleo_id, componentes in por_nucleo.items():
        titulo = f"Núcleo de {nomes_nucleo.get(nucleo_id, nucleo_id)}"
        eh_nucleo_optativo = all(c.tipo == TipoComponente.CARGA_OPTATIVA for c in componentes)
        escrever(
            f"tab_nucleo_{slug(nucleo_id)}.tex",
            tabela_componentes(
                componentes, titulo, f"nucleo_{slug(nucleo_id)}", incluir_total=not eh_nucleo_optativo
            ),
        )

    carga_por_nucleo: dict[str, int] = {}
    for nucleo_id, componentes in por_nucleo.items():
        nome = nomes_nucleo.get(nucleo_id, nucleo_id)
        if all(c.tipo == TipoComponente.CARGA_OPTATIVA for c in componentes):
            carga_por_nucleo[nome] = optativa_minima
        else:
            carga_por_nucleo[nome] = sum(
                c.carga_total for c in componentes if c.tipo != TipoComponente.CARGA_OPTATIVA
            )
    escrever(
        "tab_carga_horaria_por_nucleo.tex",
        tabela_carga_por_grupo(
            carga_por_nucleo, "Carga Horária por Núcleo de Formação", "carga_horaria_por_nucleo", total_geral
        ),
    )

    # --- Tabelas por área de formação --------------------------------------
    nomes_area = {a.id: a.nome for a in referenciais.areas}
    carga_por_area: dict[str, int] = {}
    for c in oficiais:
        for area_id in c.areas or ["sem_area"]:
            nome_area = nomes_area.get(area_id, area_id)
            carga_por_area[nome_area] = carga_por_area.get(nome_area, 0) + c.carga_total
    if optativa_minima:
        carga_por_area["Formação Optativa (mínimo exigido)"] = optativa_minima
    escrever(
        "tab_carga_horaria_por_area.tex",
        tabela_carga_por_grupo(
            carga_por_area, "Carga Horária por Área de Formação", "carga_horaria_por_area", total_geral
        ),
    )

    # --- Distribuição teórica/prática/EaD/extensão -------------------------
    # Calculada sobre os componentes obrigatórios: a repartição CHT/CHP/CHD/CHE
    # do pool de optativas depende de quais o estudante escolher, portanto
    # entra como um único bloco "Optativas", não decomposto por modalidade.
    distribuicao = {
        "Carga Teórica": sum((c.carga_horaria.teorica or 0) for c in oficiais),
        "Carga Prática": sum((c.carga_horaria.pratica or 0) for c in oficiais),
        "Carga a Distância (EaD)": sum((c.carga_horaria.ead or 0) for c in oficiais),
        "Carga de Extensão": sum((c.carga_horaria.extensao or 0) for c in oficiais),
    }
    # Componentes sem repartição teórica/prática/EaD/extensão definida (ex.:
    # Atividades Acadêmicas Complementares, cuja natureza é heterogênea) não
    # somem do total: entram como um bloco à parte.
    sem_modalidade = sum(
        c.carga_total for c in oficiais if c.carga_horaria.soma_parcelas() is None
    )
    if sem_modalidade:
        distribuicao["Carga sem Modalidade Classificada (ex.: AAC)"] = sem_modalidade
    if optativa_minima:
        distribuicao["Optativas (mínimo exigido)"] = optativa_minima
    escrever(
        "tab_distribuicao_modalidades.tex",
        tabela_carga_por_grupo(
            distribuicao, "Distribuição da Carga Horária por Modalidade", "distribuicao_modalidades", total_geral
        ),
    )

    # --- Obrigatórios / optativos ------------------------------------------
    optativos = [c for c in ativos if c.tipo == TipoComponente.CARGA_OPTATIVA]
    escrever(
        "tab_componentes_obrigatorios.tex",
        tabela_componentes(obrigatorios, "Componentes Curriculares Obrigatórios", "componentes_obrigatorios"),
    )
    escrever(
        "tab_disciplinas_optativas.tex",
        tabela_componentes(optativos, "Disciplinas Optativas Pré-Aprovadas", "disciplinas_optativas", incluir_total=False),
    )

    # --- Disciplinas equivalentes -------------------------------------------
    if curriculo.equivalencias:
        escrever(
            "tab_disciplinas_equivalentes.tex",
            tabela_equivalencias(
                curriculo.equivalencias,
                curriculo.por_codigo(),
                "Disciplinas Equivalentes Pré-Aprovadas",
                "disciplinas_equivalentes",
            ),
        )

    # --- Pré-requisitos / correquisitos ------------------------------------
    com_requisitos = [c for c in ativos if c.pre_requisitos or c.correquisitos]
    escrever(
        "tab_prerequisitos.tex",
        tabela_prerequisitos(
            com_requisitos, "Pré-requisitos e Correquisitos", "prerequisitos_correquisitos", nomes_por_codigo
        ),
    )

    # --- Temas transversais -------------------------------------------------
    for tema in referenciais.temas_transversais:
        componentes_tema = sorted(
            (c for c in ativos if tema.id in c.temas_transversais),
            key=lambda c: (c.periodo if c.periodo is not None else 99, c.nome),
        )
        if not componentes_tema:
            continue
        escrever(
            f"tab_tema_{slug(tema.id)}.tex",
            tabela_referencia(
                componentes_tema,
                f"Distribuição dos Conteúdos Curriculares Referentes a {tema.nome}",
                f"tema_{slug(tema.id)}",
                tema.fonte_normativa,
            ),
        )

    # --- Aderência às competências ------------------------------------------
    for competencia in referenciais.competencias:
        componentes_comp = sorted(
            (c for c in ativos if competencia.id in c.competencias),
            key=lambda c: (c.periodo if c.periodo is not None else 99, c.nome),
        )
        if not componentes_comp:
            continue
        escrever(
            f"tab_competencia_{slug(competencia.id)}.tex",
            tabela_referencia(
                componentes_comp,
                f"Aderência Curricular à Competência: {competencia.descricao}",
                f"competencia_{slug(competencia.id)}",
                competencia.fonte,
            ),
        )

    # --- Aderência aos conteúdos curriculares -------------------------------
    for conteudo in referenciais.conteudos:
        componentes_conteudo = sorted(
            (c for c in ativos if conteudo.id in c.conteudos),
            key=lambda c: (c.periodo if c.periodo is not None else 99, c.nome),
        )
        if not componentes_conteudo:
            continue
        escrever(
            f"tab_conteudo_{slug(conteudo.id)}.tex",
            tabela_referencia(
                componentes_conteudo,
                f"Distribuição Curricular do Conteúdo: {conteudo.descricao}",
                f"conteudo_{slug(conteudo.id)}",
                conteudo.fonte,
            ),
        )

    # --- Indicadores / totais usados em parágrafos (Seção 14) --------------
    def escrever_indicador(nome_arquivo: str, valor: str) -> None:
        escrever(nome_arquivo, valor + "\n")

    escrever_indicador("par_carga_horaria_total.tex", f"{total_geral} horas")
    escrever_indicador("par_carga_horaria_optativa.tex", f"{optativa_minima} horas")
    for tipo, nome_arquivo in (
        (TipoComponente.EXTENSAO, "par_carga_horaria_extensao.tex"),
        (TipoComponente.ATIVIDADE_COMPLEMENTAR, "par_carga_horaria_aac.tex"),
        (TipoComponente.ESTAGIO, "par_carga_horaria_estagio.tex"),
        (TipoComponente.TCC, "par_carga_horaria_tcc.tex"),
    ):
        soma = carga_por_tipo(curriculo, tipo)
        escrever_indicador(nome_arquivo, f"{soma} horas")

    # Numerador de EaD restrito à população oficial pelo mesmo motivo do
    # validador (ppcgen.validadores.ead): o pool de optativas tem repartição
    # de EaD desconhecida até a escolha do estudante.
    percentual_ead = (
        100 * sum((c.carga_horaria.ead or 0) for c in oficiais) / total_geral if total_geral else 0
    )
    percentual_extensao = (
        100 * carga_por_tipo(curriculo, TipoComponente.EXTENSAO) / total_geral if total_geral else 0
    )
    escrever_indicador("par_percentual_ead.tex", f"{percentual_ead:.1f}\\%".replace(".", ","))
    escrever_indicador("par_percentual_extensao.tex", f"{percentual_extensao:.1f}\\%".replace(".", ","))
    escrever_indicador("par_numero_componentes.tex", str(len(ativos)))

    return gerados
