# Dicionário de Dados

Este schema é o mesmo para a matriz curricular de qualquer perfil — o
caminho é `dados/perfis/<id>/matriz_curricular.xlsx` (configurável via
`arquivos.matriz` em `perfil.yaml`, ver `docs/PERFIS.md`).

**Fontes únicas, sem sobreposição**: cada dado deste projeto vive em
exatamente um lugar. A versão curricular é `perfil.info.versao` (não há
mais aba `Curso` na matriz). Núcleos, áreas de formação, temas
transversais e conteúdos curriculares são catálogos de registro em abas
próprias da matriz (`Nucleos`/`Areas`/`Temas`/`Conteudos`). Legislação e
competências são listas em `perfil.yaml` (não há mais pasta
`referenciais/`). Pré-requisitos, correquisitos e os vínculos
componente→área/tema/conteúdo/competência são colunas da própria aba
`Componentes` — não abas de junção separadas.

## `matriz_curricular.xlsx`

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
| `nucleo_id` | texto | sim para componente ativo | id existente na aba `Nucleos` | `TECNOLOGICO` | `COMPONENTE_SEM_NUCLEO`, `NUCLEO_INEXISTENTE` |
| `unidade_oferta` | texto | não | — | `FEELT` | apenas informativo |
| `observacoes` | texto | não | — | — | usado como "justificativa" para downgrade de `CLASSIFICACAO_CONTRADITORIA` |
| `pre_requisitos` | texto (lista) | não | ver sintaxe abaixo | `CTR401, CTR203 (opcional), >=1200h` | `PREREQUISITO_INEXISTENTE`, `PREREQUISITO_AUTORREFERENCIA`, `PREREQUISITO_PERIODO_INVALIDO`, `CICLO_PREREQUISITOS` |
| `correquisitos` | texto (lista) | não | ver sintaxe abaixo | `CTR305, CTR306 (opcional)` | `CORREQUISITO_INEXISTENTE`, `CORREQUISITO_AUTORREFERENCIA`, `CORREQUISITO_PERIODO_DIVERGENTE` |
| `areas` | texto (lista, ids separados por vírgula) | sim para componente ativo (0+, mas ao menos 1) | ids existentes na aba `Areas` | `CONTROLE, AUTOMACAO` | `COMPONENTE_SEM_AREA`, `AREA_INEXISTENTE` |
| `temas` | texto (lista, ids separados por vírgula) | não | ids existentes na aba `Temas` | `LIBRAS` | `TEMA_TRANSVERSAL_INEXISTENTE` |
| `conteudos` | texto (lista, ids separados por vírgula) | não | ids existentes na aba `Conteudos` | `DCN_BASE_00, DCN_BASE_03` | `CONTEUDO_INEXISTENTE` |
| `competencias` | texto (lista, ids separados por vírgula) | não | ids existentes em `perfil.competencias` | `PROJETAR_SISTEMAS_CONTROLE` | `COMPETENCIA_INEXISTENTE` |

#### Sintaxe de `pre_requisitos`/`correquisitos`

Célula com itens separados por vírgula. Cada item é um dos três formatos
abaixo — nunca um código mágico como `"*"` para "carga horária mínima"
(ver `ppcgen.validadores.prerequisitos`):

- **código simples** (obrigatório): `CTR401`
- **código opcional**: `CTR401 (opcional)` — rebaixa
  `PREREQUISITO_INEXISTENTE`/`CORREQUISITO_INEXISTENTE` de erro para
  alerta se o código não existir
- **carga horária mínima acumulada** (só em `pre_requisitos`, não existe
  equivalente em `correquisitos`): `>=1200h`

Não se usa `?` como marcador de "opcional" porque códigos de componente já
podem legitimamente conter `?`/`!` (convenção de código provisório, ver
`codigo_provisorio` acima) — usar `?` também para "opcional" criaria
ambiguidade.

Exemplo de célula combinando os três formatos:
`CTR401, CTR203 (opcional), >=1200h`

### Aba `Equivalencias`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `codigo_origem` | texto | sim | Código considerado equivalente (tipicamente um componente de um currículo anterior, que pode não existir mais na matriz atual). |
| `codigo_destino` | texto | sim | Código ao qual `codigo_origem` equivale — deve existir na matriz atual (`EQUIVALENCIA_DESTINO_INEXISTENTE` se não existir). |
| `observacao` | texto | não | Ex.: unidade acadêmica de origem, condição da equivalência. |

Gera a tabela "Disciplinas Equivalentes" em `textos/estrutura_curricular.tex`
via `gerado/tab_disciplinas_equivalentes.tex` (só escrito se houver ao
menos uma equivalência). Não existe mais um arquivo `equivalencias.xlsx`
separado — tudo fica nesta aba.

### Aba `Nucleos`

Catálogo dos núcleos curriculares do curso — substitui o antigo
`referenciais/nucleos.yaml`.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `TECNOLOGICO` |
| `nome` | texto | sim | `Formação Tecnológica e Profissional` |
| `descricao` | texto | não | — |

### Aba `Areas`

Catálogo das áreas de formação — substitui o antigo
`referenciais/areas_formacao.yaml`. Mesmos campos de `Nucleos` (`id`,
`nome`, `descricao`).

### Aba `Temas`

Catálogo dos temas transversais — substitui o antigo
`referenciais/temas_transversais.yaml`.

| Campo | Tipo | Obrigatório | Valores possíveis | Exemplo |
|---|---|---|---|---|
| `id` | texto | sim | — | `LIBRAS` |
| `nome` | texto | sim | — | `Ensino de Libras` |
| `descricao` | texto | não | — | — |
| `fonte_normativa` | texto | não | — | `Decreto nº 5.626/2005` |
| `status` | texto | não (padrão `ativo`) | `obrigatorio`, `sugerido`, `ativo` | `obrigatorio` |

`status: obrigatorio` faz o validador emitir
`TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA` se nenhum componente ativo
referenciar o tema (coluna `temas` da aba `Componentes`).

### Aba `Conteudos`

Catálogo de conteúdos curriculares obrigatórios exigidos por uma DCN
específica (ex.: DCN de Computação) — opcional, só necessário para cursos
cujas diretrizes exigem rastrear cobertura de conteúdo, não só de carga
horária/competência. Substitui o antigo `referenciais/conteudos.yaml`.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `DCN_BASE_00` |
| `descricao` | texto | sim | `Algoritmos e estruturas de dados` |
| `obrigatorio` | booleano | não (padrão `FALSE`) | `TRUE` |
| `fonte` | texto | não | `Resolução CNE/CES nº 5/2016, Art. 5º` |

`obrigatorio: TRUE` faz o validador emitir
`CONTEUDO_OBRIGATORIO_SEM_COBERTURA` (alerta) se nenhum componente ativo
referenciar o conteúdo na coluna `conteudos` da aba `Componentes`.

### Aba `Certificacoes` (opcional)

Só é lida se existir. `certificacao_id`, `nome`, `codigo_componente` (uma
linha por componente que conta para aquela certificação).

### Outras abas

A matriz pode conter abas fora deste esquema (ex.: um fluxograma visual
próprio do curso) — o leitor (`ppcgen.leitores.excel`) as ignora
silenciosamente; elas não são validadas nem geram nenhuma saída.

## `perfil.yaml`

Ver `docs/PERFIS.md` para a lista comentada de todas as seções e
`ppcgen/config.py` para a lista definitiva de campos de cada uma
(`InfoPerfil`, `CursoConfig`, `InstituicaoConfig`, `CurriculoConfig`,
`OfertaConfig`, `ArquivosConfig`, `GeracaoConfig`, `SaidaConfig`,
`HerancaConfig`) — os nomes dos campos no YAML são idênticos aos
atributos das dataclasses, e um campo desconhecido causa erro imediato ao
carregar (`ConfiguracaoInvalida`).

### `legislacao:` (lista, top-level em `perfil.yaml`)

Catálogo de referenciais legais deste perfil — substitui o antigo
`referenciais/legislacao.yaml` **e** o mecanismo `heranca.legislacao`
(arquivos compartilhados em `dados/compartilhados/legislacao/`, que não
existe mais). Cada perfil declara sua própria lista completa, sem
arquivo externo para editar em separado.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `MEC_CNE_CES_7_2018` |
| `nome` | texto | sim | `Diretrizes para a extensão na Educação Superior` |
| `tipo` | texto | não | `resolucao`, `lei`, `decreto`, `catalogo`, `parecer`, `portaria` |
| `documento` | texto | não | `Resolução CNE/CES nº 7, de 18 de dezembro de 2018` |
| `ano` | inteiro ou vazio | não | `2018` |
| `observacoes` | texto | não | — |

Se `perfil.extends` aponta para um perfil base, as listas de `legislacao`
de ambos são mescladas por `id` (o perfil atual sobrescreve o base em caso
de colisão) — ver Seção 9 de `docs/PERFIS.md`.

### `competencias:` (lista, top-level em `perfil.yaml`)

Catálogo de competências deste perfil — substitui o antigo
`referenciais/competencias.yaml`. Mesma semântica de herança por `id` que
`legislacao:`, acima.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `PROJETAR_SISTEMAS_CONTROLE` |
| `descricao` | texto | sim | `Projetar, especificar e sintonizar sistemas de controle...` |
| `obrigatoria` | booleano | não (padrão `FALSE`) | `TRUE` |
| `fonte` | texto | não | id de um item em `legislacao:`, ex. `MEC_CATALOGO_CST` |
