"""Geração do fluxo curricular (Seção 13).

Diferente do script legado — que dependia de números fixos (``PER_ACC = 5``)
e de prefixos de código (``"ACE"``, ``"AAC"``, ``"ACC"``) para decidir onde
cada componente entrava no fluxo — aqui o agrupamento usa exclusivamente
``periodo`` (quando definido) e ``tipo`` (para os componentes sem período
fixo: TCC/Estágio, Atividades Complementares e Optativas).

A tabela gerada usa uma linha por componente (sem mesclagem de células por
``rowspan``) — uma simplificação deliberada em relação ao layout do script
legado.
"""

from __future__ import annotations

from ppcgen.config import Perfil
from ppcgen.geradores.tabelas import formatar_lista_requisitos
from ppcgen.modelos import ComponenteCurricular, Curriculo, TipoComponente
from ppcgen.utilitarios.latex import escapar
from ppcgen.utilitarios.textos import ordinal, texto_ou_travessao

_ROTULOS_TIPO_SEM_PERIODO = {
    TipoComponente.TCC: "Conclusão de Curso",
    TipoComponente.ESTAGIO: "Conclusão de Curso",
    TipoComponente.ATIVIDADE_COMPLEMENTAR: "Atividades Complementares",
    TipoComponente.CARGA_OPTATIVA: "Optativas",
    TipoComponente.OUTRO: "Outros",
}


def montar_grupos_fluxo(
    curriculo: Curriculo, numero_periodos: int
) -> dict[str, list[ComponenteCurricular]]:
    grupos: dict[str, list[ComponenteCurricular]] = {str(p): [] for p in range(1, numero_periodos + 1)}
    for c in curriculo.ativos():
        if c.periodo is not None:
            grupos.setdefault(str(c.periodo), []).append(c)
        else:
            rotulo = _ROTULOS_TIPO_SEM_PERIODO.get(c.tipo, "Outros")
            grupos.setdefault(rotulo, []).append(c)
    return {chave: valor for chave, valor in grupos.items() if valor}


def _rotulo_grupo(chave: str) -> str:
    return ordinal(int(chave)) if chave.isdigit() else escapar(chave)


def gerar_tabela_fluxo(curriculo: Curriculo, perfil: Perfil, nomes_por_codigo: dict[str, str]) -> str:
    grupos = montar_grupos_fluxo(curriculo, perfil.curso.numero_periodos)

    cabecalho = r"""\begin{longtblr}[
    theme = ppc,
    caption = {Fluxo Curricular},
    label = {tab:fluxo_curricular},
]{
    colspec = {|Q[c,m,wd=14mm]|Q[l,m,wd=45mm]|Q[c,m,wd=16mm]|Q[c,m,wd=8mm]|Q[c,m,wd=8mm]|Q[c,m,wd=8mm]|Q[c,m,wd=8mm]|Q[c,m,wd=10mm]|Q[l,m,wd=25mm]|Q[l,m,wd=25mm]|Q[c,m,wd=14mm]|},
    rowhead = 1,
    hlines = {fg=AzulEscuro},
    vlines = {fg=AzulEscuro},
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    cells = {font=\fontsize{8pt}{9pt}\selectfont},
}
    \textbf{PER} & \textbf{Componente Curricular} & \textbf{Natureza} & \textbf{CHT} & \textbf{CHP} & \textbf{CHD} & \textbf{CHE} & \textbf{TOT} & \textbf{PREQ} & \textbf{CREQ} & \textbf{UA Oferta} \\
"""
    corpo = ""
    for chave, componentes in grupos.items():
        rotulo = _rotulo_grupo(chave)
        for c in componentes:
            ch = c.carga_horaria
            natureza = "Obrigatória" if c.obrigatorio else "Optativa"
            preq = formatar_lista_requisitos(c.pre_requisitos, nomes_por_codigo)
            creq = formatar_lista_requisitos(c.correquisitos, nomes_por_codigo)
            corpo += (
                "    "
                + " & ".join(
                    [
                        rotulo,
                        escapar(c.nome),
                        natureza,
                        texto_ou_travessao(ch.teorica),
                        texto_ou_travessao(ch.pratica),
                        texto_ou_travessao(ch.ead),
                        texto_ou_travessao(ch.extensao),
                        texto_ou_travessao(ch.total),
                        preq,
                        creq,
                        escapar(c.unidade_oferta) or "--",
                    ]
                )
                + r" \\"
                + "\n"
            )
    return cabecalho + corpo + r"\end{longtblr}" + "\n"
