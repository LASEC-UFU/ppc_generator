"""Geração dos relatórios de validação (``saida/relatorio_validacao.json`` e
``.html``) e do relatório de situação das fichas curriculares.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ppcgen.geradores.html import escapar_html
from ppcgen.modelos import ResultadoValidacao
from ppcgen.validadores.fichas import SituacaoFichas

_CSS = """
body { font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 2rem auto; max-width: 60rem; color: #1a1a1a; }
h1 { font-size: 1.4rem; }
h2 { font-size: 1.1rem; margin-top: 2rem; }
table { border-collapse: collapse; width: 100%; margin-top: .5rem; }
th, td { border: 1px solid #ddd; padding: .4rem .6rem; text-align: left; font-size: .85rem; vertical-align: top; }
th { background: #222; color: white; }
tr.erro { background: #fdecea; }
tr.alerta { background: #fff8e1; }
tr.informacao { background: #eef6ff; }
.resumo { display: flex; gap: 1rem; margin: 1rem 0; }
.card { border-radius: .5rem; padding: .75rem 1rem; color: white; min-width: 8rem; }
.card.erro { background: #c0392b; }
.card.alerta { background: #c9962b; }
.card.informacao { background: #2b6ec9; }
.card .n { font-size: 1.6rem; font-weight: bold; display: block; }
code { background: #f0f0f0; padding: 0 .2rem; border-radius: .2rem; }
"""


def _mensagem_para_dict(m) -> dict:
    return {
        "severidade": m.severidade.value,
        "codigo_regra": m.codigo_regra,
        "mensagem": m.mensagem,
        "componente": m.componente,
        "campo": m.campo,
    }


def resultado_para_dict(resultado: ResultadoValidacao, situacao_fichas: SituacaoFichas | None = None) -> dict:
    dados = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "resumo": {
            "erros": len(resultado.erros),
            "alertas": len(resultado.alertas),
            "informacoes": len(resultado.informacoes),
        },
        "mensagens": [_mensagem_para_dict(m) for m in resultado.mensagens],
    }
    if situacao_fichas is not None:
        dados["fichas"] = {
            "status_por_componente": {
                codigo: status.value for codigo, status in situacao_fichas.status_por_componente.items()
            },
            "fichas_orfas": situacao_fichas.fichas_orfas,
        }
    return dados


def gerar_relatorio_json(
    resultado: ResultadoValidacao, caminho: Path, situacao_fichas: SituacaoFichas | None = None
) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados = resultado_para_dict(resultado, situacao_fichas)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _linha_html(m) -> str:
    componente = escapar_html(m.componente or "-")
    campo = escapar_html(m.campo or "-")
    return (
        f'<tr class="{m.severidade.value}">'
        f"<td>{escapar_html(m.severidade.value.upper())}</td>"
        f"<td><code>{componente}</code></td>"
        f"<td><code>{escapar_html(m.codigo_regra)}</code></td>"
        f"<td>{campo}</td>"
        f"<td>{escapar_html(m.mensagem)}</td>"
        f"</tr>"
    )


def gerar_relatorio_html(
    resultado: ResultadoValidacao, caminho: Path, situacao_fichas: SituacaoFichas | None = None
) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)

    linhas = "\n".join(_linha_html(m) for m in resultado.mensagens) or (
        '<tr><td colspan="5">Nenhuma inconsistência encontrada.</td></tr>'
    )

    fichas_html = ""
    if situacao_fichas is not None:
        linhas_fichas = "\n".join(
            f"<tr><td><code>{escapar_html(codigo)}</code></td><td>{escapar_html(status.value)}</td></tr>"
            for codigo, status in sorted(situacao_fichas.status_por_componente.items())
        )
        orfas_html = "".join(f"<li><code>{escapar_html(c)}</code></li>" for c in situacao_fichas.fichas_orfas)
        fichas_html = f"""
        <h2>Situação das fichas curriculares</h2>
        <table>
        <tr><th>Componente</th><th>Status</th></tr>
        {linhas_fichas}
        </table>
        {"<h3>Fichas sem componente correspondente na matriz atual</h3><ul>" + orfas_html + "</ul>" if orfas_html else ""}
        """

    html = f"""<title>Relatório de Validação do PPC</title>
<style>{_CSS}</style>
<h1>Relatório de Validação Curricular</h1>
<p>Gerado em {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<div class="resumo">
    <div class="card erro"><span class="n">{len(resultado.erros)}</span>erro(s)</div>
    <div class="card alerta"><span class="n">{len(resultado.alertas)}</span>alerta(s)</div>
    <div class="card informacao"><span class="n">{len(resultado.informacoes)}</span>informação(ões)</div>
</div>
<table>
<tr><th>Severidade</th><th>Componente</th><th>Regra</th><th>Campo</th><th>Mensagem</th></tr>
{linhas}
</table>
{fichas_html}
"""
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)


def imprimir_resumo_terminal(resultado: ResultadoValidacao) -> None:
    """Imprime as mensagens no formato ``[SEVERIDADE] CODIGO — mensagem``."""

    for m in resultado.mensagens:
        prefixo = f"[{m.severidade.value.upper()}]"
        componente = f"{m.componente} — " if m.componente else ""
        print(f"{prefixo} {componente}{m.mensagem}")
    print(
        f"\nResumo: {len(resultado.erros)} erro(s), {len(resultado.alertas)} alerta(s), "
        f"{len(resultado.informacoes)} informação(ões)."
    )
