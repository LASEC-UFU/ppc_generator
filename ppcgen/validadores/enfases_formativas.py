"""Validação das Ênfases Formativas (áreas de formação optativa) — Seção 9.

A vinculação entre um componente curricular e sua ênfase é inferida do
próprio nome do componente (padrão ``SIGLA NÚMERO: Nome``, ver
``ppcgen.utilitarios.textos.analisar_prefixo_enfase_formativa``), não de
nenhuma coluna cadastrada separadamente — este módulo reaplica o mesmo
parser usado pelo leitor (``ppcgen.leitores.excel``) para reportar, de
forma fina, os casos em que um componente parece pretender pertencer a uma
ênfase mas o nome está malformado, além de conferir se a carga horária
disponível em cada ênfase é suficiente para o mínimo configurado na aba
``Perfil``.
"""

from __future__ import annotations

from collections import defaultdict

from ppcgen.config import Perfil
from ppcgen.modelos import AlertaValidacao, Curriculo, ErroValidacao, ReferenciaisCurso, ResultadoValidacao
from ppcgen.utilitarios.textos import analisar_prefixo_enfase_formativa


def validar_enfases_formativas(
    curriculo: Curriculo, perfil: Perfil, referenciais: ReferenciaisCurso
) -> ResultadoValidacao:
    resultado = ResultadoValidacao()
    if not referenciais.enfases_formativas:
        return resultado  # curso não usa o mecanismo (ex.: Tecnólogo) — nada a checar

    siglas_cadastradas = {e.sigla: e for e in referenciais.enfases_formativas if e.sigla}
    ativos = curriculo.ativos()

    contagem_numeros: dict[tuple[str, int], list[str]] = defaultdict(list)
    numeros_por_sigla: dict[str, list[int]] = defaultdict(list)

    for c in ativos:
        prefixo = analisar_prefixo_enfase_formativa(c.nome)
        if prefixo is None:
            continue  # disciplina comum, sem prefixo de ênfase — não é erro

        if not prefixo.nome_disciplina:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_NOMENCLATURA_INVALIDA",
                    f"componente '{c.codigo}' (nome '{c.nome}') parece ter prefixo de ênfase "
                    "formativa, mas não tem denominação após os dois-pontos.",
                    componente=c.codigo,
                )
            )
            continue

        if prefixo.sigla not in siglas_cadastradas:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_SIGLA_INEXISTENTE",
                    f"componente '{c.codigo}' (nome '{c.nome}') usa a sigla '{prefixo.sigla}', que "
                    "não está cadastrada na aba EnfasesFormativas.",
                    componente=c.codigo,
                )
            )
            continue

        if prefixo.numero_valido is None:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_NUMERO_INVALIDO",
                    f"componente '{c.codigo}' (nome '{c.nome}') tem número de ênfase inválido "
                    f"('{prefixo.numero_bruto}') — deve ser um inteiro positivo (1, 2, 3...).",
                    componente=c.codigo,
                )
            )
            continue

        contagem_numeros[(prefixo.sigla, prefixo.numero_valido)].append(c.codigo)
        numeros_por_sigla[prefixo.sigla].append(prefixo.numero_valido)

    for (sigla, numero), codigos in contagem_numeros.items():
        if len(codigos) > 1:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_NUMERO_DUPLICADO",
                    f"mais de um componente usa '{sigla} {numero}': {', '.join(sorted(codigos))}.",
                )
            )

    for sigla, numeros in numeros_por_sigla.items():
        numeros_unicos = sorted(set(numeros))
        esperado = list(range(1, len(numeros_unicos) + 1))
        if numeros_unicos != esperado:
            resultado.adicionar(
                AlertaValidacao(
                    "ENFASE_FORMATIVA_SEQUENCIA_INCONSISTENTE",
                    f"numeração da ênfase '{sigla}' tem lacunas ou não começa em 1: "
                    f"{numeros_unicos} (esperado {esperado}).",
                )
            )

    carga_por_enfase: dict[str, int] = defaultdict(int)
    for c in ativos:
        if c.enfase_formativa_id is not None:
            carga_por_enfase[c.enfase_formativa_id] += c.carga_total

    for enfase in referenciais.enfases_formativas:
        if carga_por_enfase.get(enfase.id, 0) == 0:
            resultado.adicionar(
                AlertaValidacao(
                    "ENFASE_FORMATIVA_SEM_COMPONENTES",
                    f"ênfase formativa '{enfase.id}' ({enfase.nome}) não tem nenhum componente "
                    "ativo vinculado pelo nome (padrão 'SIGLA NÚMERO: Nome').",
                )
            )

    minimas = perfil.curriculo.enfases_formativas_minimas
    if minimas is None or minimas < 1 or minimas > len(referenciais.enfases_formativas):
        resultado.adicionar(
            ErroValidacao(
                "ENFASES_FORMATIVAS_MINIMAS_INVALIDAS",
                f"curriculo.enfases_formativas_minimas ({minimas}) precisa ser um inteiro entre 1 "
                f"e {len(referenciais.enfases_formativas)} (número de ênfases cadastradas).",
            )
        )
        return resultado  # sem um mínimo válido, as checagens de suficiência abaixo não fazem sentido

    carga_minima = perfil.curriculo.carga_horaria_minima_por_enfase
    if carga_minima is None or carga_minima <= 0:
        resultado.adicionar(
            ErroValidacao(
                "ENFASE_FORMATIVA_CARGA_MINIMA_INVALIDA",
                f"curriculo.carga_horaria_minima_por_enfase ({carga_minima}) precisa ser um número "
                "positivo de horas.",
            )
        )
        return resultado

    enfases_suficientes = 0
    for enfase in referenciais.enfases_formativas:
        disponivel = carga_por_enfase.get(enfase.id, 0)
        if disponivel < carga_minima:
            resultado.adicionar(
                ErroValidacao(
                    "ENFASE_FORMATIVA_CARGA_INSUFICIENTE",
                    f"ênfase formativa '{enfase.id}' ({enfase.nome}) tem apenas {disponivel}h de "
                    f"componentes ativos vinculados, insuficiente para o mínimo de {carga_minima}h.",
                )
            )
        else:
            enfases_suficientes += 1

    if enfases_suficientes < minimas:
        resultado.adicionar(
            ErroValidacao(
                "ENFASES_FORMATIVAS_INTEGRALIZACAO_INVIAVEL",
                f"apenas {enfases_suficientes} ênfase(s) formativa(s) têm carga horária suficiente "
                f"({carga_minima}h) — são necessárias, no mínimo, {minimas}.",
            )
        )

    return resultado
