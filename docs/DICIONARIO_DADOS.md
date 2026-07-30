# Dicionário de Dados

Este schema é o mesmo para a matriz curricular de qualquer perfil — o
caminho é `dados/perfis/<id>/matriz_curricular.xlsx` (configurável via
`arquivos.matriz` em `perfil.yaml`, ver `docs/PERFIS.md`). Não existe mais
uma matriz única na raiz de `dados/`.

## `matriz_curricular.xlsx`

### Aba `Curso`

Tabela chave/valor (colunas `campo`, `valor`), metadados desta versão da matriz.

| Campo | Tipo | Obrigatório | Exemplo | Descrição |
|---|---|---|---|---|
| `versao_curricular` | texto | sim | `2026-1-exemplo` | Identificador da versão curricular representada por este arquivo. Usado por `ppcgen comparar`. |
| `data_geracao` | data (`AAAA-MM-DD`) | não | `2026-07-29` | Data de criação/última edição relevante da planilha. |
| `observacoes` | texto | não | — | Observações livres sobre esta versão. |

### Aba `Componentes`

Uma linha por componente curricular (disciplina, extensão, projeto
integrador, estágio, TCC, atividade complementar, optativa...).

| Campo | Tipo | Obrigatório | Valores possíveis | Exemplo | Regra de validação |
|---|---|---|---|---|---|
| `codigo` | texto | sim, único | letras/números/`_`/`-`/`!`/`?` | `CTR401` | `CODIGO_DUPLICADO`, `CODIGO_CARACTERES_INVALIDOS` |
| `nome` | texto | sim | — | `Sistemas de Controle I` | `NOME_OBRIGATORIO` |
| `tipo` | texto (enum) | sim | `disciplina`, `projeto_integrador`, `extensao`, `estagio`, `tcc`, `atividade_complementar`, `carga_optativa`, `certificacao`, `outro` | `disciplina` | leitor rejeita valor fora do enum (`FormatoInvalido`) |
| `periodo` | inteiro ou vazio | condicional | `1`..`numero_periodos` | `4` | `PERIODO_FORA_DO_INTERVALO`, `COMPONENTE_OBRIGATORIO_SEM_PERIODO` |
| `ativo` | booleano | sim (recomendado explícito) | `TRUE`/`FALSE` | `TRUE` | célula em branco gera aviso `LEITURA_DADO_OMITIDO` (assume `TRUE`) |
| `obrigatorio` | booleano | sim | `TRUE`/`FALSE` | `TRUE` | combinado com `tipo=carga_optativa` gera `CLASSIFICACAO_CONTRADITORIA` |
| `codigo_provisorio` | booleano | não (padrão `FALSE`) | `TRUE`/`FALSE` | `FALSE` | gera `CODIGO_PROVISORIO` (alerta) quando `TRUE` ou código contém `!`/`?` |
| `cht` | inteiro ou vazio | não | ≥ 0 | `45` | `CARGA_NEGATIVA`, soma entra em `CARGA_TOTAL_INCONSISTENTE` |
| `chp` | inteiro ou vazio | não | ≥ 0 | `15` | idem |
| `chd` | inteiro ou vazio | não | ≥ 0 | `0` | idem; soma entra no percentual de EaD |
| `che` | inteiro ou vazio | não | ≥ 0 | `0` | idem; soma entra no percentual de extensão |
| `tot` | inteiro ou vazio | sim (recomendado) | ≥ 0 | `60` | deve ser igual a `cht+chp+chd+che` quando todas informadas |
| `nucleo_id` | texto | sim para componente ativo | id existente em `referenciais/nucleos.yaml` | `TECNOLOGICO` | `COMPONENTE_SEM_NUCLEO`, `NUCLEO_INEXISTENTE` |
| `unidade_oferta` | texto | não | — | `FEELT` | apenas informativo |
| `ementa` | texto | não | — | — | usado na tabela de disciplinas equivalentes |
| `observacoes` | texto | não | — | — | usado como "justificativa" para downgrade de `CLASSIFICACAO_CONTRADITORIA` |

### Aba `Pre-requisitos`

Uma linha por relação componente → pré-requisito (0 ou mais por componente).

| Campo | Tipo | Obrigatório | Exemplo | Regra de validação |
|---|---|---|---|---|
| `codigo_componente` | texto | sim | `CTR501` | deve existir em `Componentes` |
| `codigo_prerequisito` | texto ou vazio | condicional* | `CTR401` | `PREREQUISITO_INEXISTENTE`, `PREREQUISITO_AUTORREFERENCIA`, `PREREQUISITO_PERIODO_INVALIDO`, `CICLO_PREREQUISITOS` |
| `opcional` | booleano | não (padrão `FALSE`) | `FALSE` | rebaixa `PREREQUISITO_INEXISTENTE` de erro para alerta |
| `carga_horaria_minima` | inteiro ou vazio | condicional* | `1200` | usado em vez de `codigo_prerequisito` para requisitos por carga horária acumulada (nunca um código mágico como `"*"`) |

\* uma linha deve ter `codigo_prerequisito` **ou** `carga_horaria_minima`
preenchido — nunca os dois vazios (`PREREQUISITO_MALFORMADO`).

### Aba `Correquisitos`

| Campo | Tipo | Obrigatório | Regra de validação |
|---|---|---|---|
| `codigo_componente` | texto | sim | deve existir em `Componentes` |
| `codigo_correquisito` | texto | sim | `CORREQUISITO_INEXISTENTE`, `CORREQUISITO_AUTORREFERENCIA`; período diferente do componente gera `CORREQUISITO_PERIODO_DIVERGENTE` (alerta) |
| `opcional` | booleano | não | rebaixa `CORREQUISITO_INEXISTENTE` para alerta |

### Aba `Equivalencias`

Mesmo schema do arquivo dedicado `equivalencias.xlsx` (ver abaixo) — as
duas fontes são somadas em `Curriculo.equivalencias`; use a aba dentro da
matriz para equivalências que fazem sentido acompanhar a própria versão
curricular, e o arquivo dedicado para as demais.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `codigo_origem` | texto | sim | Código considerado equivalente (tipicamente um componente de um currículo anterior, que pode não existir mais na matriz atual). |
| `codigo_destino` | texto | sim | Código ao qual `codigo_origem` equivale — deve existir na matriz atual (`EQUIVALENCIA_DESTINO_INEXISTENTE` se não existir). |
| `observacao` | texto | não | Ex.: unidade acadêmica de origem, condição da equivalência. |

## `equivalencias.xlsx`

Arquivo dedicado por perfil (`arquivos.equivalencias`, padrão
`equivalencias.xlsx`), mesmo schema da aba `Equivalencias` acima (uma
única planilha sem nome fixo — lida como `wb[wb.sheetnames[0]]`). Gera a
tabela "Disciplinas Equivalentes" em `textos/estrutura_curricular.tex` via
`gerado/tab_disciplinas_equivalentes.tex` (só escrito se houver ao menos
uma equivalência).

### Aba `Areas`

Junção componente → área de formação (0 ou mais por componente; **não**
gera erro se vazia — mas `COMPONENTE_SEM_AREA` é emitido se um componente
ativo não aparecer aqui nenhuma vez).

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `codigo_componente` | texto | sim | `CTR401` |
| `area_id` | texto | sim | `CONTROLE` (deve existir em `referenciais/areas_formacao.yaml`) |

### Aba `Temas`

Junção componente → tema transversal (0 ou mais). `tema_id` deve existir em
`referenciais/temas_transversais.yaml` (`TEMA_TRANSVERSAL_INEXISTENTE`).

### Aba `Competencias`

Junção componente → competência (0 ou mais). `competencia_id` deve existir
em `referenciais/competencias.yaml` (`COMPETENCIA_INEXISTENTE`).

### Aba `Conteudos`

Junção componente → conteúdo curricular (0 ou mais). `conteudo_id` deve
existir em `referenciais/conteudos.yaml` (`CONTEUDO_INEXISTENTE`). Usada
para currículos regidos por DCN que exigem cobertura explícita de uma
lista de conteúdos obrigatórios (ex.: DCN de Computação) — opcional para
cursos cujas diretrizes não exigem esse rastreamento.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `codigo_componente` | texto | sim | `CTR401` |
| `conteudo_id` | texto | sim | `DCN_BASE_00` (deve existir em `referenciais/conteudos.yaml`) |

### Aba `Certificacoes` (opcional)

Só é lida se existir. `certificacao_id`, `nome`, `codigo_componente` (uma
linha por componente que conta para aquela certificação).

## `referenciais/nucleos.yaml`

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `TECNOLOGICO` |
| `nome` | texto | sim | `Formação Tecnológica e Profissional` |
| `descricao` | texto | não | — |

## `referenciais/areas_formacao.yaml`

Mesmos campos de `nucleos.yaml` (`id`, `nome`, `descricao`).

## `referenciais/temas_transversais.yaml`

| Campo | Tipo | Obrigatório | Valores possíveis | Exemplo |
|---|---|---|---|---|
| `id` | texto | sim | — | `LIBRAS` |
| `nome` | texto | sim | — | `Ensino de Libras` |
| `descricao` | texto | não | — | — |
| `fonte_normativa` | texto | não | — | `Decreto nº 5.626/2005` |
| `status` | texto | não (padrão `ativo`) | `obrigatorio`, `sugerido`, `ativo` | `obrigatorio` |

`status: obrigatorio` faz o validador emitir
`TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA` se nenhum componente ativo
referenciar o tema.

## `referenciais/competencias.yaml`

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `PROJETAR_SISTEMAS_CONTROLE` |
| `descricao` | texto | sim | `Projetar, especificar e sintonizar sistemas de controle...` |
| `obrigatoria` | booleano | não (padrão `FALSE`) | `TRUE` |
| `fonte` | texto | não | id de um item em `legislacao.yaml`, ex. `MEC_CATALOGO_CST` |

## `referenciais/legislacao.yaml`

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `MEC_CNE_CES_7_2018` |
| `nome` | texto | sim | `Diretrizes para a extensão na Educação Superior` |
| `tipo` | texto | não | `resolucao`, `lei`, `decreto`, `catalogo`, `parecer` |
| `documento` | texto | não | `Resolução CNE/CES nº 7, de 18 de dezembro de 2018` |
| `ano` | inteiro ou vazio | não | `2018` |
| `observacoes` | texto | não | — |

Pode ser complementado (nunca sobrescrito) por `heranca.legislacao`, campo
de `perfil.yaml` (ver `docs/PERFIS.md`).

## `referenciais/conteudos.yaml`

Catálogo de conteúdos curriculares obrigatórios exigidos por uma DCN
específica (ex.: DCN de Computação) — opcional, só necessário para cursos
cujas diretrizes exigem rastrear cobertura de conteúdo, não só de carga
horária/competência.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `DCN_BASE_00` |
| `descricao` | texto | sim | `Algoritmos e estruturas de dados` |
| `obrigatorio` | booleano | não (padrão `FALSE`) | `TRUE` |
| `fonte` | texto | não | `Resolução CNE/CES nº 5/2016, Art. 5º` |

`obrigatorio: TRUE` faz o validador emitir
`CONTEUDO_OBRIGATORIO_SEM_COBERTURA` (alerta) se nenhum componente ativo
referenciar o conteúdo na aba `Conteudos` da matriz.

## `perfil.yaml`

Ver `docs/PERFIS.md` para a lista comentada de todas as seções e
`ppcgen/config.py` para a lista definitiva de campos de cada uma
(`InfoPerfil`, `CursoConfig`, `InstituicaoConfig`, `CurriculoConfig`,
`ArquivosConfig`, `GeracaoConfig`, `SaidaConfig`, `HerancaConfig`) — os
nomes dos campos no YAML são idênticos aos atributos das dataclasses, e um
campo desconhecido causa erro imediato ao carregar (`ConfiguracaoInvalida`).
Substituiu o `config/curso.yaml` único de versões anteriores deste projeto
— agora cada perfil tem o seu.
