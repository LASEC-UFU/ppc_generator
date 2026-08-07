"""Orquestração de todo o pipeline de validação (Seção 9 — ESTRUTURA
CURRICULAR).

``validar_curriculo`` é o ponto de entrada único usado pela CLI: chama, nesta
ordem, os validadores de código/identificação, carga horária, extensão, EaD,
pré-requisitos/correquisitos (com detecção de ciclos), referenciais e — se
fichas forem fornecidas — fichas curriculares. Nenhum destes módulos lança
exceção por problema de dado; o resultado agregado é sempre um
:class:`~ppcgen.modelos.ResultadoValidacao` que a CLI decide como reportar.

Não existe mais uma checagem isolada de "componente obrigatório sem
período": um componente sem ``periodo`` é sempre considerado ``outro`` na
prática, qualquer que seja o ``tipo`` cadastrado — não haveria sentido em
manter duas fontes de informação (``tipo`` declarado e presença de
``periodo``) que pudessem divergir entre si. Por isso a ausência de
``periodo`` nunca é, por si só, um erro a reportar."""

from __future__ import annotations

from ppcgen.config import Perfil
from ppcgen.modelos import (
    AlertaValidacao,
    Curriculo,
    FichaCurricular,
    ReferenciaisCurso,
    ResultadoValidacao,
)
from ppcgen.validadores.cargas import validar_cargas
from ppcgen.validadores.codigos import validar_codigos
from ppcgen.validadores.ead import validar_ead
from ppcgen.validadores.enfases_formativas import validar_enfases_formativas
from ppcgen.validadores.extensao import validar_extensao
from ppcgen.validadores.fichas import SituacaoFichas, avaliar_fichas
from ppcgen.validadores.prerequisitos import validar_equivalencias, validar_prerequisitos
from ppcgen.validadores.referenciais import validar_referenciais


def validar_curriculo(
    curriculo: Curriculo,
    perfil: Perfil,
    referenciais: ReferenciaisCurso,
    fichas: list[FichaCurricular] | None = None,
    avisos_leitura: list[str] | None = None,
) -> tuple[ResultadoValidacao, SituacaoFichas | None]:
    resultado = ResultadoValidacao()

    for aviso in avisos_leitura or []:
        resultado.adicionar(AlertaValidacao("LEITURA_DADO_OMITIDO", aviso))

    resultado.mesclar(validar_codigos(curriculo, perfil))
    resultado.mesclar(validar_cargas(curriculo, perfil))
    resultado.mesclar(validar_extensao(curriculo, perfil))
    resultado.mesclar(validar_ead(curriculo, perfil))
    resultado.mesclar(validar_prerequisitos(curriculo, perfil))
    resultado.mesclar(validar_equivalencias(curriculo))
    resultado.mesclar(validar_referenciais(curriculo, referenciais))
    resultado.mesclar(validar_enfases_formativas(curriculo, perfil, referenciais))

    situacao_fichas: SituacaoFichas | None = None
    if fichas is not None:
        resultado_fichas, situacao_fichas = avaliar_fichas(curriculo, fichas)
        resultado.mesclar(resultado_fichas)

    return resultado, situacao_fichas
