# Dicionário de Dados

Este schema é o mesmo para a matriz curricular de qualquer perfil — o
caminho é `dados/perfis/<id>/matriz_curricular.xlsx`/`.xlsm` (nome
configurável via `matriz:` em `dados/perfis.yaml`, ver `docs/PERFIS.md`).
**Não existe mais `perfil.yaml`** — a planilha concentra toda a
configuração do perfil (aba `Perfil`) além dos dados curriculares.

**Fontes únicas, sem sobreposição**: cada dado deste projeto vive em
exatamente um lugar. A versão curricular é `perfil.info.versao` (não há
mais aba `Curso` na matriz — o campo vem da aba `Perfil`). Núcleos, áreas
de formação, temas transversais, conteúdos curriculares e competências
são catálogos de registro em abas próprias da matriz (`Nucleos`/`Areas`/
`Temas`/`Conteudos`/`Competencias`) — cada uma vincula os componentes que
cobre via sua própria coluna `componentes` (ver "Padrão `componentes`"
abaixo); a aba `Componentes` não tem colunas equivalentes, a direção é
catálogo → componente, não o contrário. Bibliografia é a aba
`Bibliografia`, uma linha por referência — o `.bib` compilado é sempre
gerado a partir dela, nunca um arquivo `.bib` estático (ver "Aba
`Bibliografia`" abaixo). Legislação é a aba `Legislacao`, também um
registro por linha. Pré-requisitos e correquisitos são colunas da própria
aba `Componentes`.

## `matriz_curricular.xlsx`

### Aba `Perfil`

Chave/valor — uma linha por campo de configuração do perfil (não
curricular): identificação, curso, instituição, currículo, oferta, capa,
comissão de elaboração, arquivos, geração e saída. Substitui inteiramente
o antigo `perfil.yaml`.

| Coluna | Descrição |
|---|---|
| `chave` | caminho pontilhado `secao.campo` — ex.: `curso.numero_periodos`, `curriculo.carga_horaria_total`, `geracao.compilar_pdf` |
| `valor` | o valor daquele campo |

Seções e campos válidos (mesmos nomes/defaults das dataclasses em
`ppcgen/config.py` — `perfil.*` usa `InfoPerfil`, `curso.*` usa
`CursoConfig`, e assim por diante): `perfil.id`/`nome`/`status`/`versao`/
`descricao`/`extends`; `curso.nome`/`nome_curto`/`nome_mercadologico`/
`enfase_curricular`/`sigla`/`grau`/`modalidade`/`turno`/`regime_academico`/
`numero_periodos`/`campus`/`municipio`/`estado` (`nome` é a denominação
regulatória perante MEC/INEP — a única usada para fins normativos;
`nome_mercadologico`/`enfase_curricular` são opcionais, texto livre de
divulgação institucional, sem efeito em validações); `instituicao.nome`/`sigla`/`unidade_academica` (mais
qualquer outra chave `instituicao.*` livre — endereço, CEP, site,
telefone... — vira `InstituicaoConfig.extra`, acessível pelos templates
por nome); `curriculo.carga_horaria_total`/`carga_obrigatoria`/
`carga_extensao`/`carga_aac`/`carga_estagio`/
`carga_tcc`/`percentual_minimo_extensao`/`percentual_maximo_ead`/
`carga_horaria_presencial_maxima_periodo` (máximo de CHT+CHP por período —
carga a distância e de extensão não entram nessa soma)/`periodo_minimo_tcc`/
`periodo_minimo_estagio`; `oferta.formato`/`possui_carga_ead`/
`norma_federal`/`norma_institucional`/`status_validacao_institucional`;
`capa.ano`/`logo_curso` (`logo_curso` é o caminho, relativo à pasta do
perfil, de uma logomarca própria do curso — ex.: `figuras/logo.png`;
vazio omite a imagem na capa, distinto do logo institucional da UFU, fixo
no template); `comissao.titulo` (título da caixa de créditos na folha de
rosto — os nomes dos membros vêm da aba `Comissao`, ver abaixo);
`arquivos.textos`/`fichas`/`figuras`/`anexos`/`overrides`/
`capitulos` (não existe linha `arquivos.matriz` — o nome do arquivo de
matriz é sempre o arquivo que acabou de ser aberto para ler esta própria
aba, nunca configurável de dentro dela); `geracao.template`/`anexar_fichas`/
`anexar_resolucoes`/`gerar_fluxo_curricular`/
`gerar_representacao_grafica`/`gerar_relatorio_validacao`/
`compilar_pdf`/`interromper_em_erro`; `saida.nome_base`/`gerar_corpo`/
`gerar_completo`.

Célula `valor` em branco omite aquele campo — o default da dataclass
correspondente se aplica (idêntico a omitir a chave no antigo YAML). Sem
coluna de tipo separada: número/booleano nativos do Excel passam direto;
texto `TRUE`/`FALSE`/`VERDADEIRO`/`FALSO` (case-insensitive) vira `bool`;
texto numérico vira `int`/`float`; o resto fica string — exceto
`arquivos.capitulos`, o único campo de lista: itens separados por `|`
(mesmo formato de `componentes`/`pre_requisitos` nas outras abas), sem a
extensão `.tex`, um `\input{textos/<nome>}` por item **na ordem em que
aparecem na célula** — essa é a lista/ordem dos capítulos do corpo do PPC
(substitui a lista antes fixa em `templates/latex/Main.tex`); célula
vazia ou linha ausente cai no default de 12 capítulos padrão
(`ppcgen.config.CAPITULOS_PADRAO`).

### Aba `Componentes`

Uma linha por componente curricular (disciplina, extensão, projeto
integrador, estágio, TCC, atividade complementar, optativa...).

| Campo | Tipo | Obrigatório | Valores possíveis | Exemplo | Regra de validação |
|---|---|---|---|---|---|
| `codigo` | texto | sim, único | letras/números/`_`/`-`/`!`/`?` | `CTR401` | `CODIGO_DUPLICADO`, `CODIGO_CARACTERES_INVALIDOS` |
| `nome` | texto | sim | — | `Sistemas de Controle I` | `NOME_OBRIGATORIO` |
| `tipo` | texto (enum) | sim | `disciplina`, `projeto_integrador`, `extensao`, `estagio`, `tcc`, `atividade_complementar`, `carga_optativa`, `certificacao`, `outro` | `disciplina` | leitor rejeita valor fora do enum (`FormatoInvalido`) |
| `periodo` | inteiro ou vazio | condicional | `1`..`numero_periodos` | `4` | `PERIODO_FORA_DO_INTERVALO` — vazio não é erro: um componente sem período é sempre tratado como `outro` na lógica de tipo (`ComponenteCurricular.tipo_efetivo`), qualquer que seja o `tipo` cadastrado |
| `ativo` | booleano | sim (recomendado explícito) | `TRUE`/`FALSE` | `TRUE` | célula em branco gera aviso `LEITURA_DADO_OMITIDO` (assume `TRUE`) |
| `cht` | inteiro ou vazio | não | ≥ 0 | `45` | `CARGA_NEGATIVA`, soma entra em `CARGA_TOTAL_INCONSISTENTE` |
| `chp` | inteiro ou vazio | não | ≥ 0 | `15` | idem |
| `chd` | inteiro ou vazio | não | ≥ 0 | `0` | idem; soma entra no percentual de EaD |
| `che` | inteiro ou vazio | não | ≥ 0 | `0` | idem; soma entra no percentual de extensão |
| `tot` | inteiro ou vazio | sim (recomendado) | ≥ 0 | `60` | deve ser igual a `cht+chp+chd+che` quando todas informadas |
| `observacoes` | texto | não | — | — | texto livre, sem papel em nenhuma validação |
| `pre_requisitos` | texto (lista, itens separados por `\|`) | não | ver sintaxe abaixo | `CTR401\|CTR203 (opcional)\|>=1200h` | `PREREQUISITO_INEXISTENTE`, `PREREQUISITO_AUTORREFERENCIA`, `PREREQUISITO_PERIODO_INVALIDO`, `CICLO_PREREQUISITOS` |
| `correquisitos` | texto (lista, itens separados por `\|`) | não | ver sintaxe abaixo | `CTR305\|CTR306 (opcional)` | `CORREQUISITO_INEXISTENTE`, `CORREQUISITO_AUTORREFERENCIA`, `CORREQUISITO_PERIODO_DIVERGENTE` |

Não há colunas `nucleo_id`/`areas`/`temas`/`conteudos`/`competencias`
aqui — um componente ativo sem núcleo/área vinculado por nenhuma aba de
catálogo gera `COMPONENTE_SEM_NUCLEO`/`COMPONENTE_SEM_AREA` (ver "Padrão
`componentes`" abaixo).

#### Campos derivados (não são colunas da planilha)

`codigo_provisorio`, `unidade_oferta` e `obrigatorio`
(`ComponenteCurricular`, `ppcgen/modelos.py`) não são preenchidos na
matriz — são propriedades calculadas sempre que o componente é
carregado, para não ter dois dados divergindo:

- `unidade_oferta`: prefixo de `codigo` até o primeiro dígito ou `!`
  (não incluídos) — `FAMAT31011` → `FAMAT`, `FEELT!TDCA` → `FEELT`.
- `codigo_provisorio`: `True` quando `codigo` começa com `FEELT!` (marca
  disciplinas propostas sem código oficial/SIGAA ainda atribuído),
  `False` caso contrário. Continua gerando `CODIGO_PROVISORIO` (ver
  `docs/VALIDACOES.md`).
- `obrigatorio`: `True` sse `tipo != carga_optativa` — não existe mais
  como coluna própria (nem o campo, nem a contradição possível entre os
  dois); é exatamente esse critério, por `tipo`, que já decidia o que
  conta na carga horária oficial do curso (`ppcgen/calculo.py`) e agora
  também decide o rótulo "Obrigatória"/"Optativa" no fluxograma e a
  população da tabela "Componentes Curriculares Obrigatórios" no PDF.

**Componente agregador (carga horária optativa mínima).** A carga horária
optativa mínima do curso não é um parâmetro da aba `Perfil` — é lida
diretamente da `carga_total` de um componente-resumo cadastrado na aba
`Componentes`, cujo `nome` (normalizado, sem acento) seja um de "módulo
optativo", "carga optativa", "pool optativo" ou "bloco optativo" (ver
`ppcgen.calculo.eh_agregador_optativo`/`carga_optativa_minima`). O que o
distingue de uma disciplina real é o **nome**, não os campos `ativo`/`tipo`
— ele pode estar `ativo=True` (decisão de cada perfil) sem afetar nenhum
cálculo: `ppcgen.calculo.componentes_oficiais` e a soma do pool real de
optativas (`ppcgen.validadores.cargas`) sempre o excluem por nome, para que
sua carga entre uma única vez. Manter esse valor em dois lugares (a aba
`Perfil` e este componente) já foi um bug real deste projeto — os dois
números divergiam sempre que só um era atualizado —, por isso a aba
`Perfil` não tem mais campo equivalente.

#### Sintaxe de `pre_requisitos`/`correquisitos`

Célula com itens separados por `|` (mesmo separador da coluna
`componentes` das abas de catálogo — nunca vírgula). Cada item é um dos
três formatos abaixo — nunca um código mágico como `"*"` para "carga
horária mínima" (ver `ppcgen.validadores.prerequisitos`):

- **código simples** (obrigatório): `CTR401`
- **código opcional**: `CTR401 (opcional)` — rebaixa
  `PREREQUISITO_INEXISTENTE`/`CORREQUISITO_INEXISTENTE` de erro para
  alerta se o código não existir
- **carga horária mínima acumulada** (só em `pre_requisitos`, não existe
  equivalente em `correquisitos`): `>=1200h`

Não se usa `?` como marcador de "opcional" porque códigos de componente já
podem legitimamente conter `?`/`!` (convenção de código provisório, ver
"Campos derivados de `codigo`" acima) — usar `?` também para "opcional"
criaria ambiguidade.

Exemplo de célula combinando os três formatos:
`CTR401|CTR203 (opcional)|>=1200h`

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

### Padrão `componentes` (comum a `Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`/`EnfasesFormativas`)

As seis abas de catálogo abaixo têm, todas, uma coluna `componentes`:
texto com os códigos dos componentes vinculados àquele item, separados
por `|` (ex.: `FAMAT31011|FEELT31204`) — nunca por vírgula, para não
colidir com o separador usado em `pre_requisitos`/`correquisitos`. É essa
coluna, não uma coluna na aba `Componentes`, que define o vínculo — a
direção é catálogo → componente.

No carregamento (`ppcgen.leitores.excel._aplicar_vinculos_catalogo`), cada
código listado em `componentes` é usado para preencher o campo
correspondente do componente (`nucleo`/`areas`/`temas_transversais`/
`conteudos`/`competencias`/`enfases_formativas`, em
`ppcgen.modelos.ComponenteCurricular`) — o resultado final tem exatamente
a mesma forma de antes, só muda de onde vem. `nucleo` é cardinalidade 1:
se o mesmo código aparecer em `componentes` de mais de uma linha da aba
`Nucleos`, o primeiro vence e o validador emite
`NUCLEO_MULTIPLO_PARA_COMPONENTE` (erro); os demais campos — inclusive
`enfases_formativas` — aceitam qualquer número de vínculos (um componente
pode legitimamente pertencer a mais de uma ênfase formativa).

Um código em `componentes` que não existe na aba `Componentes` não é
descartado silenciosamente — o leitor preserva a lista bruta em
`<Catalogo>.componentes` e `ppcgen.validadores.referenciais` reporta um
erro por catálogo: `NUCLEO_COMPONENTE_INEXISTENTE`,
`AREA_COMPONENTE_INEXISTENTE`, `TEMA_TRANSVERSAL_COMPONENTE_INEXISTENTE`,
`CONTEUDO_COMPONENTE_INEXISTENTE`, `COMPETENCIA_COMPONENTE_INEXISTENTE`,
`ENFASE_FORMATIVA_COMPONENTE_INEXISTENTE`.

### Aba `Nucleos`

Catálogo dos núcleos curriculares do curso — substitui o antigo
`referenciais/nucleos.yaml`.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `TECNOLOGICO` |
| `nome` | texto | sim | `Formação Tecnológica e Profissional` |
| `descricao` | texto | não | — |
| `componentes` | texto (lista, códigos separados por `\|`) | não | `FEELT31301\|FEELT31401` |

### Aba `Areas`

Catálogo das áreas de formação — substitui o antigo
`referenciais/areas_formacao.yaml`. Mesmos campos de `Nucleos` (`id`,
`nome`, `descricao`, `componentes`).

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
| `componentes` | texto (lista, códigos separados por `\|`) | não | `LIBRAS01\|LIBRAS02` |

`status: obrigatorio` faz o validador emitir
`TEMA_TRANSVERSAL_OBRIGATORIO_SEM_COBERTURA` se `componentes` estiver
vazio ou só tiver códigos inativos.

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
| `componentes` | texto (lista, códigos separados por `\|`) | não | `FACOM31201\|FACOM31303` |

`obrigatorio: TRUE` faz o validador emitir
`CONTEUDO_OBRIGATORIO_SEM_COBERTURA` (alerta) se `componentes` estiver
vazio ou só tiver códigos inativos.

### Aba `Competencias`

Catálogo de competências do curso — substitui o antigo
`referenciais/competencias.yaml`; não vive mais em `perfil.yaml`.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `PROJETAR_SISTEMAS_CONTROLE` |
| `descricao` | texto | sim | `Projetar, especificar e sintonizar sistemas de controle...` |
| `obrigatoria` | booleano | não (padrão `FALSE`) | `TRUE` |
| `fonte` | texto | não | id de um item na aba `Legislacao`, ex. `MEC_CATALOGO_CST` |
| `componentes` | texto (lista, códigos separados por `\|`) | não | `FEELT!SCON` |

`obrigatoria: TRUE` faz o validador emitir
`COMPETENCIA_OBRIGATORIA_SEM_COBERTURA` (alerta) se `componentes` estiver
vazio ou só tiver códigos inativos.

### Aba `EnfasesFormativas` (opcional)

Catálogo das ênfases formativas (áreas de formação optativa) do curso —
percursos de aprofundamento entre os quais o curso pode exigir a
integralização de um número mínimo (`curriculo.enfases_formativas_minimas`
na aba `Perfil`), cada uma com sua própria carga horária mínima
(`curriculo.carga_horaria_minima_por_enfase`). Aba ausente ou vazia
significa que o curso não usa o mecanismo (ex.: o Tecnólogo) —
`ppcgen.validadores.enfases_formativas` não emite nenhuma checagem nesse
caso.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `id` | texto | sim | `MIAPI` |
| `nome` | texto | sim | `Máquinas Inteligentes, Acionamentos e Proteção Industrial` |
| `sigla` | texto | não | `MIAPI` |
| `conteudos_estruturantes` | texto | não | — |
| `aderencia_profissional` | texto | não | — |
| `componentes` | texto (lista, códigos separados por `\|`) | não | `FEELT!TEC1\|FEELT!TEC2` |

Vínculo componente ↔ ênfase é N:N (ver "Padrão `componentes`" acima): um
componente pode ser pertinente a mais de uma ênfase, contando
integralmente para a carga horária de cada uma.

### Aba `Bibliografia`

Catálogo de referências bibliográficas do PPC — uma linha por entrada
BibTeX/biblatex. Não existe `.bib` estático em `dados/`: o único `.bib` do
projeto é gerado a partir desta aba, em `saida/<id>/latex/gerado/
bibliografia.bib`, toda vez que `ppcgen gerar`/`completo` roda (ver
`ppcgen.geradores.bibliografia`) — editar essa aba é a única forma de
mudar a bibliografia; o `.bib` gerado nunca deve ser editado à mão. A geração
também inclui as normas da aba `Legislacao`; não repita uma norma aqui quando
ela já estiver cadastrada naquela aba.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `chave` | texto | sim, único | `ufu_guia_ppc_2021` |
| `tipo` | texto (tipo de entrada BibTeX) | sim | `misc`, `book`, `techreport`, `article`... |
| `autor` | texto | não | `Universidade Federal de Uberlândia (UFU)` |
| `titulo` | texto | não | `Guia de Elaboração de Projetos Pedagógicos...` |
| `ano` | texto | não | `2021` |
| `mes` | texto | não | `mar` |
| `dia` | texto | não | `18` |
| `endereco` | texto | não | `Uberlândia, MG` |
| `editora` | texto | não | `UNESCO Publishing` |
| `organizacao` | texto | não | `Ministério da Educação` |
| `instituicao` | texto | não | `Association for Computing Machinery` |
| `edicao` | texto | não | `3` |
| `serie` | texto | não | `Conversations for Tomorrow` |
| `doi` | texto | não | `10.1145/3408839` |
| `paginas` | texto | não | `30--31` |
| `url` | texto | não | `https://prograd.ufu.br/.../guia_ppc_3a_edicao.pdf` |
| `nota` | texto | não | observação livre — vira o campo BibTeX `note` |

Texto UTF-8 normal, sem escapes de LaTeX (nada de `{\c c}`/`\~a`) — o
gerador aplica o escape necessário automaticamente, exceto em `url`, que
vira o campo nativo `url` do biblatex (tipo `verbatim` no datamodel padrão
— biber o escreve no `.bbl` com `\verb{url}...\endverb`, imune a
`%`/`_`/`&`; não precisa e não deve ser escapado, e não deve ser
reconstruído manualmente com `\url{...}` dentro de outro campo comum —
ver a docstring de `ppcgen.geradores.bibliografia` para o motivo). `autor`
e `titulo` viram os campos BibTeX `author`/`title`; os demais campos têm o
mesmo nome em português e em BibTeX (`endereco`→`address`,
`editora`→`publisher` etc. — ver `ppcgen.geradores.bibliografia` para o
mapeamento completo). O estilo bibliográfico (`style=numeric` em
`Main.tex`) exibe o campo `url` automaticamente como "Disponível em: ..."
via a localização `brazilian.lbx`.

### Aba `Legislacao`

Catálogo de referenciais legais do curso — substitui o antigo
`referenciais/legislacao.yaml` **e** a antiga chave `legislacao:` de
`perfil.yaml` (não vive mais lá). Cada perfil declara sua própria lista
completa, sem arquivo externo para editar em separado.

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

### Aba `Autoridades` (opcional)

Folha de rosto do PPC — reitor, vice-reitor, pró-reitores, direção da
unidade, coordenação do curso etc. Uma linha por autoridade, **na ordem em
que devem aparecer** na folha de rosto (não há coluna de ordenação — a
ordem é a das linhas na planilha).

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `cargo` | texto | sim | `Coordenador(a) do Curso de Tecnologia em Automação Industrial` |
| `nome` | texto | não | `Prof. Dr. Fulano de Tal` |
| `observacoes` | texto | não | ex.: aviso de nome ainda pendente de confirmação |

Se `perfil.extends` aponta para um perfil base, as listas são mescladas
por `cargo` (o perfil atual sobrescreve o base em caso de colisão) — mesma
regra dos demais catálogos (Seção 9 de `docs/PERFIS.md`); útil para vários
cursos da mesma instituição herdarem reitor/vice-reitor de um perfil base
comum e só declararem a própria coordenação.

### Aba `Comissao` (opcional)

Membros da comissão de elaboração deste PPC (o título da caixa de
créditos é `comissao.titulo`, na aba `Perfil`, não aqui). Uma linha por
membro, texto livre, na ordem de exibição.

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `membro` | texto | sim | `Prof. Dr. Fulano de Tal -- presidente da Comissão` |

Diferente dos demais catálogos, a lista **não** é mesclada item a item
entre perfil atual e base quando há `extends`: um perfil que declara sua
própria aba `Comissao` substitui a comissão inteira do base (não faz
sentido combinar comissões de propostas diferentes por item) — se a aba
estiver vazia/ausente, herda a lista completa do base.

### Aba `Certificacoes` (opcional)

Só é lida se existir. `certificacao_id`, `nome`, `codigo_componente` (uma
linha por componente que conta para aquela certificação).

### Outras abas

A matriz pode conter abas fora deste esquema (ex.: um fluxograma visual
próprio do curso) — o leitor (`ppcgen.leitores.excel`) as ignora
silenciosamente; elas não são validadas nem geram nenhuma saída.

## Configuração do perfil

Não existe mais `perfil.yaml` — ver "Aba `Perfil`" acima. Ver
`docs/PERFIS.md` para a lista comentada de todas as seções e
`ppcgen/config.py` para a lista definitiva de campos de cada uma
(`InfoPerfil`, `CursoConfig`, `InstituicaoConfig`, `CurriculoConfig`,
`OfertaConfig`, `CapaConfig`, `ComissaoConfig`, `ArquivosConfig`,
`GeracaoConfig`, `SaidaConfig`) — os
nomes dos campos na aba são idênticos aos atributos das dataclasses, e um
campo desconhecido causa erro imediato ao carregar (`ConfiguracaoInvalida`).
