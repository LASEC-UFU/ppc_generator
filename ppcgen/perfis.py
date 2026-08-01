"""Descoberta e registro de perfis de PPC (Seção 15).

Um perfil é descoberto automaticamente pela presença de
``dados/perfis/<id>/matriz_curricular.xlsm`` ou ``.xlsx`` (aba ``Perfil``
declarando ``perfil.id`` — não existe mais ``perfil.yaml``). O registro
opcional ``dados/perfis.yaml`` tem prioridade sobre a descoberta automática
quando os dois divergem em ``caminho``/``matriz``/``ativo`` para o mesmo id
— ver ``docs/PERFIS.md`` para a justificativa desta prioridade.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ppcgen.config import NOMES_MATRIZ_PADRAO, Perfil, carregar_perfil
from ppcgen.leitores.excel import ler_configuracao_perfil
from ppcgen.utilitarios.caminhos import raiz_projeto


@dataclass
class RefPerfil:
    id: str
    caminho: Path
    matriz: str = "matriz_curricular.xlsx"
    ativo: bool = True


def _pasta_perfis(raiz_dados: Path | None = None) -> Path:
    return (raiz_dados or raiz_projeto() / "dados") / "perfis"


def descobrir_perfis(raiz_dados: Path | None = None) -> dict[str, RefPerfil]:
    """Descoberta automática: qualquer subpasta de ``dados/perfis/`` com um
    ``matriz_curricular.xlsm``/``.xlsx`` cuja aba ``Perfil`` declare um
    ``perfil.id`` válido."""

    pasta = _pasta_perfis(raiz_dados)
    encontrados: dict[str, RefPerfil] = {}
    if not pasta.exists():
        return encontrados
    for candidato in sorted(pasta.iterdir()):
        nome_matriz = next(
            (nome for nome in NOMES_MATRIZ_PADRAO if (candidato / nome).is_file()), None
        )
        if nome_matriz is None:
            continue
        try:
            bruto = ler_configuracao_perfil(candidato / nome_matriz)
        except Exception:
            continue
        perfil_id = (bruto.get("perfil") or {}).get("id")
        if not perfil_id:
            continue
        encontrados[perfil_id] = RefPerfil(
            id=perfil_id, caminho=candidato, matriz=nome_matriz, ativo=True
        )
    return encontrados


def _ler_registro(raiz_dados: Path) -> dict[str, RefPerfil]:
    caminho_registro = raiz_dados / "perfis.yaml"
    if not caminho_registro.exists():
        return {}
    bruto = yaml.safe_load(caminho_registro.read_text(encoding="utf-8")) or {}
    registro: dict[str, RefPerfil] = {}
    for item in bruto.get("perfis", []):
        registro[item["id"]] = RefPerfil(
            id=item["id"],
            caminho=raiz_dados / item["caminho"],
            matriz=item.get("matriz", "matriz_curricular.xlsx"),
            ativo=item.get("ativo", True),
        )
    return registro


def listar_referencias(raiz_dados: Path | None = None) -> dict[str, RefPerfil]:
    """União de descoberta automática + ``dados/perfis.yaml``, com o
    registro explícito sobrescrevendo ``caminho``/``ativo`` quando presente
    para o mesmo id (prioridade documentada em ``docs/PERFIS.md``)."""

    raiz_dados = raiz_dados or raiz_projeto() / "dados"
    combinados = descobrir_perfis(raiz_dados)
    for perfil_id, ref in _ler_registro(raiz_dados).items():
        combinados[perfil_id] = ref
    return combinados


def resolver_perfil_dir(
    *, perfil_id: str | None = None, perfil_dir: str | Path | None = None, raiz_dados: Path | None = None
) -> Path:
    """Resolve a pasta de um perfil a partir do id ou de um caminho explícito
    (Seção 10) — nunca escolhe um perfil implicitamente."""

    if perfil_dir is not None:
        caminho = Path(perfil_dir)
        return caminho if caminho.is_absolute() else raiz_projeto() / caminho
    if perfil_id is not None:
        referencias = listar_referencias(raiz_dados)
        ref = referencias.get(perfil_id)
        if ref is not None:
            return ref.caminho
        return _pasta_perfis(raiz_dados) / perfil_id
    raise ValueError("Informe --perfil ou --perfil-dir.")


def carregar(
    *, perfil_id: str | None = None, perfil_dir: str | Path | None = None, raiz_dados: Path | None = None
) -> Perfil:
    caminho = resolver_perfil_dir(perfil_id=perfil_id, perfil_dir=perfil_dir, raiz_dados=raiz_dados)
    matriz = None
    if perfil_id is not None:
        ref = listar_referencias(raiz_dados).get(perfil_id)
        if ref is not None:
            matriz = ref.matriz
    return carregar_perfil(caminho, raiz_dados=raiz_dados, matriz=matriz)
