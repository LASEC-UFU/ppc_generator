"""Validações contra os referenciais configuráveis (Seção 8): núcleos, áreas,
temas transversais e competências devem existir no catálogo carregado de
``referenciais/*.yaml`` — nenhum identificador é aceito "de graça". Também
reporta competências/conteúdos marcados como obrigatórios que não têm
nenhum componente ativo cobrindo-os.
"""

from __future__ import annotations

from ppcgen.leitores.yaml import ReferenciaisCurso
from ppcgen.modelos import AlertaValidacao, Curriculo, ErroValidacao, ResultadoValidacao


def validar_referenciais(curriculo: Curriculo, referenciais: ReferenciaisCurso) -> ResultadoValidacao:
    resultado = ResultadoValidacao()

    ids_nucleos = referenciais.ids_nucleos()
    ids_areas = referenciais.ids_areas()
    ids_temas = referenciais.ids_temas()
    ids_competencias = referenciais.ids_competencias()
    ids_conteudos = referenciais.ids_conteudos()

    for c in curriculo.ativos():
        if c.nucleo is None:
            resultado.adicionar(
                ErroValidacao(
                    "COMPONENTE_SEM_NUCLEO",
                    f"componente ativo '{c.codigo}' não possui núcleo curricular definido.",
                    componente=c.codigo,
                )
            )
        elif ids_nucleos and c.nucleo not in ids_nucleos:
            resultado.adicionar(
                ErroValidacao(
                    "NUCLEO_INEXISTENTE",
                    f"núcleo '{c.nucleo}' de '{c.codigo}' não está definido em "
                    "referenciais/nucleos.yaml.",
                    componente=c.codigo,
                )
            )

        if not c.areas:
            resultado.adicionar(
                ErroValidacao(
                    "COMPONENTE_SEM_AREA",
                    f"componente ativo '{c.codigo}' não possui área de formação definida.",
                    componente=c.codigo,
                )
            )
        elif ids_areas:
            for area in c.areas:
                if area not in ids_areas:
                    resultado.adicionar(
                        ErroValidacao(
                            "AREA_INEXISTENTE",
                            f"área '{area}' de '{c.codigo}' não está definida em "
                            "referenciais/areas_formacao.yaml.",
                            componente=c.codigo,
                        )
                    )

        if ids_temas:
            for tema in c.temas_transversais:
                if tema not in ids_temas:
                    resultado.adicionar(
                        ErroValidacao(
                            "TEMA_TRANSVERSAL_INEXISTENTE",
                            f"tema transversal '{tema}' de '{c.codigo}' não está definido "
                            "em referenciais/temas_transversais.yaml.",
                            componente=c.codigo,
                        )
                    )

        if ids_competencias:
            for competencia in c.competencias:
                if competencia not in ids_competencias:
                    resultado.adicionar(
                        ErroValidacao(
                            "COMPETENCIA_INEXISTENTE",
                            f"competência '{competencia}' de '{c.codigo}' não está definida "
                            "em referenciais/competencias.yaml.",
                            componente=c.codigo,
                        )
                    )

        if ids_conteudos:
            for conteudo in c.conteudos:
                if conteudo not in ids_conteudos:
                    resultado.adicionar(
                        ErroValidacao(
                            "CONTEUDO_INEXISTENTE",
                            f"conteúdo '{conteudo}' de '{c.codigo}' não está definido "
                            "em referenciais/conteudos.yaml.",
                            componente=c.codigo,
                        )
                    )

    competencias_cobertas = {
        competencia_id
        for c in curriculo.ativos()
        for competencia_id in c.competencias
    }
    for competencia in referenciais.competencias:
        if competencia.obrigatoria and competencia.id not in competencias_cobertas:
            resultado.adicionar(
                AlertaValidacao(
                    "COMPETENCIA_OBRIGATORIA_SEM_COBERTURA",
                    f"competência obrigatória '{competencia.id}' ({competencia.descricao}) "
                    "não é coberta por nenhum componente ativo.",
                )
            )

    temas_cobertos = {
        tema_id for c in curriculo.ativos() for tema_id in c.temas_transversais
    }
    for tema in referenciais.temas_transversais:
        if tema.status == "obrigatorio" and tema.id not in temas_cobertos:
            resultado.adicionar(
                AlertaValidacao(
                    "TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA",
                    f"tema transversal obrigatório '{tema.id}' ({tema.nome}) não é coberto "
                    "por nenhum componente ativo.",
                )
            )

    conteudos_cobertos = {
        conteudo_id for c in curriculo.ativos() for conteudo_id in c.conteudos
    }
    for conteudo in referenciais.conteudos:
        if conteudo.obrigatorio and conteudo.id not in conteudos_cobertos:
            resultado.adicionar(
                AlertaValidacao(
                    "CONTEUDO_OBRIGATORIO_SEM_COBERTURA",
                    f"conteúdo obrigatório '{conteudo.id}' ({conteudo.descricao}) não é "
                    "coberto por nenhum componente ativo.",
                )
            )

    return resultado
