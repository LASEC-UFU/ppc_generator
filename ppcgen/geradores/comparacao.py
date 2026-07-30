"""Comparação entre duas versões da matriz curricular (Seção 17).

Recebe dois :class:`~ppcgen.modelos.Curriculo` (tipicamente lidos de dois
arquivos ``matriz_curricular.xlsx`` distintos, um "anterior" e um "atual") e
produz um relatório estruturado de diferenças, sem tentar adivinhar
renomeações de código — isso exige uma equivalência explícita, registrada em
``dados/equivalencias.xlsx`` ou na aba ``Equivalencias`` da matriz atual.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from ppcgen.modelos import ComponenteCurricular, Curriculo


@dataclass
class DiferencaComponente:
    codigo: str
    campo: str
    valor_anterior: object
    valor_atual: object


@dataclass
class RelatorioComparacao:
    versao_anterior: str
    versao_atual: str
    incluidos: list[str] = field(default_factory=list)
    removidos: list[str] = field(default_factory=list)
    alterados: list[DiferencaComponente] = field(default_factory=list)
    carga_total_anterior: int = 0
    carga_total_atual: int = 0
    carga_extensao_anterior: int = 0
    carga_extensao_atual: int = 0
    carga_ead_anterior: int = 0
    carga_ead_atual: int = 0
    competencias_perdidas: list[str] = field(default_factory=list)
    competencias_ganhas: list[str] = field(default_factory=list)


_CAMPOS_COMPARADOS = (
    "nome",
    "periodo",
    "nucleo",
    "areas",
    "obrigatorio",
    "ativo",
)


def _valor_campo(componente: ComponenteCurricular, campo: str):
    if campo == "carga_total":
        return componente.carga_total
    if campo == "pre_requisitos":
        return sorted(p.codigo for p in componente.pre_requisitos)
    if campo == "correquisitos":
        return sorted(c.codigo for c in componente.correquisitos)
    return getattr(componente, campo)


def comparar_curriculos(anterior: Curriculo, atual: Curriculo) -> RelatorioComparacao:
    por_codigo_anterior = anterior.por_codigo()
    por_codigo_atual = atual.por_codigo()

    codigos_anteriores = set(por_codigo_anterior)
    codigos_atuais = set(por_codigo_atual)

    relatorio = RelatorioComparacao(
        versao_anterior=anterior.versao,
        versao_atual=atual.versao,
        incluidos=sorted(codigos_atuais - codigos_anteriores),
        removidos=sorted(codigos_anteriores - codigos_atuais),
        carga_total_anterior=anterior.carga_horaria_total(),
        carga_total_atual=atual.carga_horaria_total(),
    )

    campos_a_comparar = _CAMPOS_COMPARADOS + ("carga_total", "pre_requisitos", "correquisitos")
    for codigo in sorted(codigos_anteriores & codigos_atuais):
        antigo = por_codigo_anterior[codigo]
        novo = por_codigo_atual[codigo]
        for campo in campos_a_comparar:
            valor_antigo = _valor_campo(antigo, campo)
            valor_novo = _valor_campo(novo, campo)
            if valor_antigo != valor_novo:
                relatorio.alterados.append(
                    DiferencaComponente(codigo, campo, valor_antigo, valor_novo)
                )

    from ppcgen.modelos import TipoComponente

    relatorio.carga_extensao_anterior = sum(
        c.carga_total for c in anterior.ativos() if c.tipo == TipoComponente.EXTENSAO
    )
    relatorio.carga_extensao_atual = sum(
        c.carga_total for c in atual.ativos() if c.tipo == TipoComponente.EXTENSAO
    )
    relatorio.carga_ead_anterior = sum((c.carga_horaria.ead or 0) for c in anterior.ativos())
    relatorio.carga_ead_atual = sum((c.carga_horaria.ead or 0) for c in atual.ativos())

    competencias_anteriores = {
        competencia for c in anterior.ativos() for competencia in c.competencias
    }
    competencias_atuais = {competencia for c in atual.ativos() for competencia in c.competencias}
    relatorio.competencias_perdidas = sorted(competencias_anteriores - competencias_atuais)
    relatorio.competencias_ganhas = sorted(competencias_atuais - competencias_anteriores)

    return relatorio


def relatorio_para_dict(relatorio: RelatorioComparacao) -> dict:
    dados = asdict(relatorio)
    dados["gerado_em"] = datetime.now().isoformat(timespec="seconds")
    return dados


def gerar_relatorio_comparacao_json(relatorio: RelatorioComparacao, caminho: Path) -> None:
    import json

    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(relatorio_para_dict(relatorio), f, ensure_ascii=False, indent=2)


def gerar_relatorio_comparacao_html(relatorio: RelatorioComparacao, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)

    linhas_incluidos = "".join(f"<li><code>{c}</code></li>" for c in relatorio.incluidos) or "<li>nenhum</li>"
    linhas_removidos = "".join(f"<li><code>{c}</code></li>" for c in relatorio.removidos) or "<li>nenhum</li>"
    linhas_alterados = "".join(
        f"<tr><td><code>{d.codigo}</code></td><td>{d.campo}</td>"
        f"<td>{d.valor_anterior}</td><td>{d.valor_atual}</td></tr>"
        for d in relatorio.alterados
    ) or '<tr><td colspan="4">nenhuma alteração</td></tr>'

    html = f"""<title>Comparação entre Versões Curriculares</title>
<style>
body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 2rem auto; max-width: 60rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: .4rem .6rem; font-size: .85rem; }}
th {{ background: #222; color: white; }}
.resumo {{ display: flex; gap: 1rem; margin: 1rem 0; }}
.card {{ border-radius: .5rem; padding: .75rem 1rem; background: #2b6ec9; color: white; }}
</style>
<h1>Comparação Curricular: {relatorio.versao_anterior} → {relatorio.versao_atual}</h1>
<div class="resumo">
    <div class="card">Carga total: {relatorio.carga_total_anterior}h → {relatorio.carga_total_atual}h</div>
    <div class="card">Extensão: {relatorio.carga_extensao_anterior}h → {relatorio.carga_extensao_atual}h</div>
    <div class="card">EaD: {relatorio.carga_ead_anterior}h → {relatorio.carga_ead_atual}h</div>
</div>
<h2>Componentes incluídos ({len(relatorio.incluidos)})</h2>
<ul>{linhas_incluidos}</ul>
<h2>Componentes removidos ({len(relatorio.removidos)})</h2>
<ul>{linhas_removidos}</ul>
<h2>Componentes alterados ({len(relatorio.alterados)})</h2>
<table>
<tr><th>Código</th><th>Campo</th><th>Valor anterior</th><th>Valor atual</th></tr>
{linhas_alterados}
</table>
<h2>Impacto sobre competências</h2>
<p>Perdidas: {", ".join(relatorio.competencias_perdidas) or "nenhuma"}</p>
<p>Ganhas: {", ".join(relatorio.competencias_ganhas) or "nenhuma"}</p>
"""
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
