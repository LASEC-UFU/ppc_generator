"""Validações contra os referenciais configuráveis (Seção 8): núcleos, áreas,
temas transversais, conteúdos, competências e ênfases formativas vivem nas
abas de registro da matriz (``Nucleos``/``Areas``/``Temas``/``Conteudos``/
``Competencias``/``EnfasesFormativas``), cada uma vinculando os componentes
que cobre via a coluna ``componentes`` (códigos separados por ``|``) — a
direção é catálogo → componente, não o contrário
(``ppcgen.leitores.excel._aplicar_vinculos_catalogo`` monta o índice
invertido no momento da carga). Este módulo confere as duas pontas dessa
relação: que todo componente ativo tenha núcleo/área definidos, que todo
código listado em ``componentes`` de um item de catálogo exista de fato na
aba ``Componentes``, e que nenhum componente seja reivindicado por mais de um
núcleo (única relação N:1 deste grupo — área/tema/conteúdo/competência/
ênfase formativa são N:N, um componente pode legitimamente pertencer a mais
de um item). Também reporta competências/conteúdos/temas marcados como
obrigatórios que não têm nenhum componente ativo cobrindo-os.
"""

from __future__ import annotations

from collections import Counter

from ppcgen.modelos import AlertaValidacao, Curriculo, ErroValidacao, ReferenciaisCurso, ResultadoValidacao


def validar_referenciais(curriculo: Curriculo, referenciais: ReferenciaisCurso) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    componentes_ativos = curriculo.ativos()

    for c in componentes_ativos:
        if c.nucleo is None:
            resultado.adicionar(
                ErroValidacao(
                    "COMPONENTE_SEM_NUCLEO",
                    f"componente ativo '{c.codigo}' não possui núcleo curricular definido.",
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

    por_codigo = curriculo.por_codigo()

    def _checar_componentes_do_catalogo(itens, tipo: str, codigo_regra: str) -> None:
        for item in itens:
            for codigo in item.componentes:
                if codigo not in por_codigo:
                    resultado.adicionar(
                        ErroValidacao(
                            codigo_regra,
                            f"código '{codigo}' listado em 'componentes' de {tipo} "
                            f"'{item.id}' não existe na aba Componentes da matriz curricular.",
                            componente=codigo,
                        )
                    )

    _checar_componentes_do_catalogo(referenciais.nucleos, "núcleo", "NUCLEO_COMPONENTE_INEXISTENTE")
    _checar_componentes_do_catalogo(referenciais.areas, "área", "AREA_COMPONENTE_INEXISTENTE")
    _checar_componentes_do_catalogo(
        referenciais.temas_transversais, "tema transversal", "TEMA_TRANSVERSAL_COMPONENTE_INEXISTENTE"
    )
    _checar_componentes_do_catalogo(referenciais.conteudos, "conteúdo", "CONTEUDO_COMPONENTE_INEXISTENTE")
    _checar_componentes_do_catalogo(referenciais.competencias, "competência", "COMPETENCIA_COMPONENTE_INEXISTENTE")
    _checar_componentes_do_catalogo(
        referenciais.enfases_formativas, "ênfase formativa", "ENFASE_FORMATIVA_COMPONENTE_INEXISTENTE"
    )

    contagem_nucleos = Counter(codigo for nucleo in referenciais.nucleos for codigo in nucleo.componentes)
    for codigo, qtd in contagem_nucleos.items():
        if qtd > 1:
            nucleos_reivindicantes = [n.id for n in referenciais.nucleos if codigo in n.componentes]
            resultado.adicionar(
                ErroValidacao(
                    "NUCLEO_MULTIPLO_PARA_COMPONENTE",
                    f"componente '{codigo}' aparece em 'componentes' de mais de um núcleo "
                    f"({', '.join(nucleos_reivindicantes)}) — cada componente pertence a um só núcleo.",
                    componente=codigo,
                )
            )

    competencias_cobertas = {competencia_id for c in componentes_ativos for competencia_id in c.competencias}
    for competencia in referenciais.competencias:
        if competencia.obrigatoria and competencia.id not in competencias_cobertas:
            resultado.adicionar(
                AlertaValidacao(
                    "COMPETENCIA_OBRIGATORIA_SEM_COBERTURA",
                    f"competência obrigatória '{competencia.id}' ({competencia.descricao}) "
                    "não é coberta por nenhum componente ativo.",
                )
            )

    temas_cobertos = {tema_id for c in componentes_ativos for tema_id in c.temas_transversais}
    for tema in referenciais.temas_transversais:
        if tema.status == "obrigatorio" and tema.id not in temas_cobertos:
            resultado.adicionar(
                AlertaValidacao(
                    "TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA",
                    f"tema transversal obrigatório '{tema.id}' ({tema.nome}) não é coberto "
                    "por nenhum componente ativo.",
                )
            )

    conteudos_cobertos = {conteudo_id for c in componentes_ativos for conteudo_id in c.conteudos}
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
