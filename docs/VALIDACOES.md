# Validações Curriculares

Todas as regras abaixo são executadas por `python -m ppcgen validar` (e,
implicitamente, por `gerar`/`completo`) através de
`ppcgen.validadores.curriculo.validar_curriculo`. Cada mensagem carrega uma
severidade (`ERRO`, `ALERTA`, `INFORMACAO`) e um `codigo_regra` estável, que
aparece igual no terminal, no HTML e no JSON.

Com `interromper_em_erro: true` (padrão), qualquer `ERRO` interrompe
`gerar`/`compilar`/`completo` antes de produzir arquivos — `ALERTA` nunca
interrompe.

## Estrutura do perfil (`ppcgen.validadores.perfil`, prefixo `PERFIL-`)

Roda **antes** da validação do currículo, via `python -m ppcgen
perfil-validar` (isoladamente) ou implicitamente em `validar`/`completo`.
Verifica que o perfil está minimamente bem-formado — não olha o conteúdo
da matriz, só a presença/coerência dos arquivos declarados.

Na aba `Perfil`, cada chave preenchida deve ter exatamente o formato
`secao.campo`, sem duplicatas. Seções diferentes de `perfil`, `curso`,
`instituicao`, `curriculo`, `oferta`, `arquivos`, `geracao` e `saida` são
rejeitadas no carregamento, para que erros de digitação não sejam ignorados.
Campos adicionais em `instituicao.*` continuam aceitos e ficam disponíveis em
`instituicao.extra` para os templates.

| Código | Severidade | Condição |
|---|---|---|
| `PERFIL-000` | ERRO | `perfil.id` não bate com `^[a-z0-9_]+$`, ou começa com `00` (prefixo reservado para material de referência em `saida/`, ex. `saida/00old/`) |
| `PERFIL-001` | ERRO | matriz curricular não localizada (nem no perfil, nem no perfil base) |
| `PERFIL-002` | ERRO | `perfil.extends` aponta para um perfil base inexistente |
| `PERFIL-003` | ALERTA | um dos 12 capítulos obrigatórios de `textos/` está ausente ou vazio |
| `PERFIL-004` | ALERTA | nenhuma ficha em `fichas/optativas/` (perfil nem perfil base) |
| `PERFIL-006` | ALERTA | uma das subpastas padrão de `fichas/` não existe (só quando o perfil não tem `extends`) |
| `PERFIL-008` | ERRO | `geracao.template` diferente de `"padrao"` e a pasta correspondente não existe em `templates/latex/` |

## Identificação (`ppcgen.validadores.codigos`)

| Código | Severidade | Condição |
|---|---|---|
| `CODIGO_DUPLICADO` | ERRO | mesmo `codigo` em duas ou mais linhas de `Componentes` |
| `NOME_OBRIGATORIO` | ERRO | `nome` vazio |
| `NOME_DUPLICADO` | ALERTA | dois componentes diferentes com o mesmo nome (normalizado) |
| `CODIGO_CARACTERES_INVALIDOS` | ERRO | código fora do padrão `[A-Za-z0-9_!?-]+` |
| `CODIGO_PROVISORIO` | ALERTA | `codigo_provisorio` (derivado: `codigo` começa com `FEELT!`) ou código contém `!`/`?` |
| `NOME_COM_ASPAS` | INFORMACAO | nome contém `"` (possível artefato de exportação) |
| `PERIODO_FORA_DO_INTERVALO` | ERRO | `periodo` fora de `1..numero_periodos` |

## Carga horária (`ppcgen.validadores.cargas`)

| Código | Severidade | Condição |
|---|---|---|
| `CARGA_NEGATIVA` | ERRO | qualquer de CHT/CHP/CHD/CHE/TOT `< 0` |
| `CARGA_TOTAL_INCONSISTENTE` | ERRO | `TOT ≠ CHT+CHP+CHD+CHE` quando todas as parcelas estão informadas |
| `CARGA_TOTAL_CURSO_DIVERGENTE` | ERRO | carga oficial calculada (ver `ppcgen/calculo.py`) ≠ `curriculo.carga_horaria_total` configurado |
| `POOL_OPTATIVAS_INSUFICIENTE` | ERRO | soma dos componentes `tipo=carga_optativa` (excluído o agregador, por nome) < carga horária do componente agregador (ver `ppcgen.calculo.carga_optativa_minima`) |
| `CARGA_TIPO_DIVERGENTE` | ALERTA | soma de AAC/estágio/TCC na matriz ≠ configurado na aba `Perfil` |
| `CARGA_MAXIMA_PERIODO_EXCEDIDA` | ERRO | soma de CHT+CHP (carga presencial) de um período > `curriculo.carga_horaria_presencial_maxima_periodo` |

## Extensão (`ppcgen.validadores.extensao`)

| Código | Severidade | Condição |
|---|---|---|
| `EXTENSAO_ABAIXO_DO_MINIMO` | ERRO | carga de componentes `tipo=extensao` / carga oficial < `curriculo.percentual_minimo_extensao` |

## EaD e formato de oferta (`ppcgen.validadores.ead`)

| Código | Severidade | Condição |
|---|---|---|
| `EAD_ACIMA_DO_MAXIMO` | ERRO | carga em EaD dos componentes obrigatórios / carga oficial > `curriculo.percentual_maximo_ead` |
| `OFERTA_FORMATO_DESCONHECIDO` | ERRO | `oferta.formato` não é `presencial`, `semipresencial` ou `distancia` |
| `EAD_ACIMA_DO_TETO_LEGAL_FORMATO` | ERRO | `curriculo.percentual_maximo_ead` configurado excede o teto legal do `oferta.formato` declarado — Decreto nº 12.456/2025: presencial ≤30%, semipresencial ≤70%, distância ≤90% (`ppcgen.validadores.ead.TETO_EAD_POR_FORMATO`) |
| `OFERTA_SEM_NORMA_INSTITUCIONAL_CONFIRMADA` | ALERTA | `oferta.possui_carga_ead: true` mas `oferta.status_validacao_institucional` ainda é `pendente` |

`EAD_ACIMA_DO_MAXIMO` só executa se `curriculo.percentual_maximo_ead`
estiver configurado (`None` = regra desativada, nunca assumida); o mesmo
vale para `EXTENSAO_ABAIXO_DO_MINIMO` acima. `EAD_ACIMA_DO_TETO_LEGAL_FORMATO`
e `OFERTA_FORMATO_DESCONHECIDO` não dependem dos componentes da matriz —
comparam a aba `Perfil` diretamente contra a lei, então rodam mesmo sem
nenhum componente cadastrado. O Decreto nº 12.456/2025 também define pisos de
atividade síncrona mediada por componente que este projeto ainda não
modela (não há campo de carga síncrona/assíncrona na matriz) — só o teto
presencial/EaD agregado é verificado.

## Pré-requisitos e correquisitos (`ppcgen.validadores.prerequisitos`)

Lidos da coluna `pre_requisitos`/`correquisitos` da aba `Componentes`
(sintaxe em `docs/DICIONARIO_DADOS.md`) — célula
`CTR401|CTR203 (opcional)|>=1200h` vira três `PreRequisito`.

| Código | Severidade | Condição |
|---|---|---|
| `PREREQUISITO_MALFORMADO` | ERRO | pré-requisito sem código e sem carga horária mínima |
| `PREREQUISITO_CODIGO_MAGICO` | ERRO | código de pré-requisito começando com `*` — sintaxe antiga; use `>=NNNh` na célula |
| `PREREQUISITO_AUTORREFERENCIA` | ERRO | componente é pré-requisito de si mesmo |
| `PREREQUISITO_INEXISTENTE` | ERRO (ALERTA se `opcional=TRUE`) | código de pré-requisito não existe na matriz |
| `PREREQUISITO_INATIVO` | ERRO | pré-requisito existe mas está `ativo=FALSE` |
| `PREREQUISITO_PERIODO_INVALIDO` | ERRO | pré-requisito com período ≥ período do componente |
| `CORREQUISITO_AUTORREFERENCIA` | ERRO | componente é correquisito de si mesmo |
| `CORREQUISITO_INEXISTENTE` | ERRO (ALERTA se `opcional=TRUE`) | código de correquisito não existe |
| `CORREQUISITO_PERIODO_DIVERGENTE` | ALERTA | correquisito em período diferente do componente |
| `CICLO_PREREQUISITOS` | ERRO | ciclo detectado no grafo de pré-requisitos (caminho completo na mensagem, ex. `AUT201 → AUT302 → AUT401 → AUT201`) |

## Referenciais (`ppcgen.validadores.referenciais`)

Núcleos, áreas, temas, conteúdos e competências vivem nas abas de registro
da própria matriz (`Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`),
cada uma vinculando os componentes que cobre via sua coluna `componentes`
(códigos separados por `|`) — a direção é catálogo → componente, não o
contrário. Ver "Padrão `componentes`" em `docs/DICIONARIO_DADOS.md`.

| Código | Severidade | Condição |
|---|---|---|
| `COMPONENTE_SEM_NUCLEO` | ERRO | componente ativo não aparece em `componentes` de nenhuma linha da aba `Nucleos` |
| `COMPONENTE_SEM_AREA` | ERRO | componente ativo não aparece em `componentes` de nenhuma linha da aba `Areas` |
| `NUCLEO_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `Nucleos` não existe na aba `Componentes` |
| `AREA_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `Areas` não existe na aba `Componentes` |
| `TEMA_TRANSVERSAL_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `Temas` não existe na aba `Componentes` |
| `CONTEUDO_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `Conteudos` não existe na aba `Componentes` |
| `COMPETENCIA_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `Competencias` não existe na aba `Componentes` |
| `ENFASE_FORMATIVA_COMPONENTE_INEXISTENTE` | ERRO | código em `componentes` de uma linha de `EnfasesFormativas` não existe na aba `Componentes` |
| `NUCLEO_MULTIPLO_PARA_COMPONENTE` | ERRO | mesmo código aparece em `componentes` de mais de uma linha da aba `Nucleos` — núcleo é cardinalidade 1 (única relação N:1 deste grupo; área/tema/conteúdo/competência/ênfase formativa são N:N e não geram este tipo de erro) |
| `COMPETENCIA_OBRIGATORIA_SEM_COBERTURA` | ALERTA | competência com `obrigatoria: true` sem nenhum componente ativo em `componentes` |
| `TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA` | ALERTA | tema com `status: obrigatorio` sem cobertura |
| `CONTEUDO_OBRIGATORIO_SEM_COBERTURA` | ALERTA | conteúdo com `obrigatorio: true` sem nenhum componente ativo em `componentes` |

## Ênfases formativas (`ppcgen.validadores.enfases_formativas`)

Áreas de formação optativa (aba `EnfasesFormativas`) entre as quais o curso
pode exigir a integralização de um número mínimo (`curriculo.enfases_formativas_minimas`),
cada uma com uma carga horária mínima própria (`curriculo.carga_horaria_minima_por_enfase`).
O vínculo componente ↔ ênfase segue o mesmo padrão `componentes` das demais
abas de referencial (ver seção anterior) — inclusive a cardinalidade N:N: um
componente pode contar integralmente para mais de uma ênfase. Curso que não
cadastra nenhuma linha em `EnfasesFormativas` (ex.: o Tecnólogo) não sofre
nenhuma destas checagens.

| Código | Severidade | Condição |
|---|---|---|
| `ENFASE_FORMATIVA_SEM_COMPONENTES` | ALERTA | ênfase cadastrada sem nenhum componente ativo vinculado em `componentes` |
| `ENFASES_FORMATIVAS_MINIMAS_INVALIDAS` | ERRO | `curriculo.enfases_formativas_minimas` ausente, `< 1` ou maior que o número de ênfases cadastradas |
| `ENFASE_FORMATIVA_CARGA_MINIMA_INVALIDA` | ERRO | `curriculo.carga_horaria_minima_por_enfase` ausente ou `<= 0` |
| `ENFASE_FORMATIVA_CARGA_INSUFICIENTE` | ERRO | soma de `carga_total` dos componentes ativos vinculados a uma ênfase é menor que `carga_horaria_minima_por_enfase` |
| `ENFASES_FORMATIVAS_INTEGRALIZACAO_INVIAVEL` | ERRO | menos ênfases têm carga suficiente do que `enfases_formativas_minimas` exige |

## Equivalências (`ppcgen.validadores.prerequisitos.validar_equivalencias`)

| Código | Severidade | Condição |
|---|---|---|
| `EQUIVALENCIA_DESTINO_INEXISTENTE` | ALERTA | `codigo_destino` de uma equivalência não existe na matriz atual |
| `EQUIVALENCIA_ORIGEM_AINDA_ATIVA` | ALERTA | `codigo_origem` ainda existe **e está ativo** na matriz atual — o caso normal é a origem ser um componente de um currículo anterior (inativo ou ausente); se ainda está ativo, confirme se a equivalência é mesmo intencional |

## Fichas curriculares (`ppcgen.validadores.fichas`, com `--incluir-fichas` ou `validar-fichas`/`completo`)

| Código | Severidade | Condição |
|---|---|---|
| `FICHA_AUSENTE` | ALERTA | nenhuma ficha localizada para o componente |
| `FICHA_NAO_RECONHECIDA` | ALERTA | ficha localizada mas ilegível (ex. PDF sem texto — `confianca_extracao=0`) |
| `FICHA_DUPLICADA` | ALERTA | mais de uma ficha reconhecida para o mesmo código |
| `FICHA_NOME_DIVERGENTE` | ALERTA | nome na ficha ≠ nome na matriz |
| `FICHA_CARGA_DIVERGENTE` | ERRO | carga total na ficha ≠ carga total na matriz |
| `FICHA_PREREQUISITOS_DIVERGENTES` | ALERTA | pré-requisitos na ficha ≠ pré-requisitos na matriz |
| `FICHA_CAMPO_VAZIO` | ALERTA | ementa/objetivos/programa/metodologia/avaliação/bibliografia básica ou complementar vazios |
| `FICHA_SEM_COMPONENTE_CORRESPONDENTE` | ALERTA | ficha encontrada cujo código não existe na matriz atual (possível currículo anterior) |

## Leitura (avisos que não são bem regras de negócio, mas não são silenciados)

| Código | Severidade | Condição |
|---|---|---|
| `LEITURA_DADO_OMITIDO` | ALERTA | ex.: célula `ativo` em branco na aba `Componentes` (assumido `TRUE`, mas registrado) |
