# Migração dos dados legados

Este documento registra o que foi encontrado nos dados do sistema anterior
(curso de Engenharia de Computação), o que foi migrado, o que foi
preservado sem alteração e quais inconsistências foram detectadas — sem
corrigi-las silenciosamente (Seção 23/29 do pedido de reestruturação).

> **Atualização**: as seções 1–2 e 6 abaixo documentam o levantamento
> inicial, feito antes de existir a arquitetura de múltiplos perfis
> (`dados/perfis/<id>/`). A migração de fato — produzindo um perfil
> completo e funcional, `dados/perfis/engenharia_computacao_2026_1/` — foi
> feita depois, e está descrita na Seção 7. Para o *processo* genérico de
> migração (aplicável a outro curso qualquer), veja
> `docs/MIGRAR_PERFIL.md`; este documento é específico do que aconteceu
> com os dados de Engenharia de Computação.
>
> **Nota sobre caminhos**: nas seções 1–6, os caminhos `py/gen_docs.py`,
> `py/PPC_disciplinas_final.csv`, `include/`, `figure/`, `fichas/SEI/`
> etc. referem-se a onde esses arquivos estavam **no momento do
> levantamento** (na raiz do repositório). Depois da migração (Seção 7),
> esse material foi consolidado em `legado/sistema_antigo/` para
> comparação e, uma vez confirmada a equivalência de resultado, removido
> do repositório de trabalho (continua no histórico do git — commit
> anterior à tag/limpeza descrita no `CHANGELOG.md`). Este documento
> preserva o relato de onde cada dado veio e o que foi decidido, mesmo
> que os arquivos de origem não estejam mais no working tree.

## 1. Qual arquivo é a fonte real

O script `py/gen_docs.py` abre, na linha 74, exatamente um arquivo:

```python
with open("py/PPC_disciplinas_final.csv") as f:
```

Portanto **`py/PPC_disciplinas_final.csv` é, e sempre foi, a única fonte
efetivamente usada** para gerar o PPC de Engenharia de Computação. Os
demais arquivos abaixo nunca foram lidos pelo gerador:

| Arquivo | Linhas | Colunas `QEXTR`/`DCN_base`/`DCN_ecp`? | Situação |
|---|---|---|---|
| `py/PPC_disciplinas_final.csv` | 160 | sim | **fonte real** |
| `py/PPC_disciplinas.csv` | 159 | `QEXTR` sim, DCN não | saída do `fichas/get_info_fichas.py`, não é insumo do gerador |
| `py/PPC_disciplinas_3450.csv` | 144 | não | variante não utilizada |
| `py/PPC_disciplinas_3850.csv` | 144 | não | variante não utilizada |
| `py/PPC_disciplinas_NAO_APAGAR.csv` | 144 | não | variante não utilizada |
| `py/PPC_disciplinas_XXX.csv` | 144 | não | variante não utilizada |
| `py/PPC disciplinas_final.xlsx` | 160 | sim | espelho Excel de aba única do CSV final — não é uma planilha estruturada |

As quatro variantes não utilizadas (`_3450`, `_3850`, `_NAO_APAGAR`, `_XXX`)
são **idênticas entre si e ao arquivo real**, exceto pelas horas placeholder
de 5 componentes (ACE1-4, OPT, AAC, ACC) — aparentemente rascunhos de
diferentes hipóteses de carga horária total do curso (3450h vs 3850h) feitos
em algum momento e nunca removidos.

**Nenhum dado foi perdido silenciosamente**: até a migração para o perfil
`engenharia_computacao_2026_1` estar completa e validada (Seção 7), as 4
variantes e todo o pipeline antigo (`py/PPC_disciplinas_final.csv`,
`py/gen_docs.py`) permaneceram intocados e funcionais no repositório —
primeiro na raiz, depois arquivados em `legado/`. Só foram removidos do
working tree depois de confirmada a equivalência de resultado; continuam
recuperáveis pelo histórico do git (ver `CHANGELOG.md`).

## 2. Inconsistências encontradas em `py/PPC_disciplinas_final.csv`

Levantamento automatizado (script usado documentado ao final deste arquivo):

- **Códigos duplicados**: 2 encontrados.
  - `FEELT!PP` é usado para **duas disciplinas diferentes**: "Arte da
    Programação II" (3º período) e "Programação Procedimental" (2º
    período, obrigatória). É uma colisão real de código provisório — as
    abreviações coincidiram.
  - `GBC212` ("Mineração de Dados") aparece **duas vezes com o mesmo
    conteúdo** — linha duplicada por engano na lista de optativas.
  - No novo sistema, `ppcgen.validadores.codigos` reporta ambos como
    `[ERRO] CODIGO_DUPLICADO` e a geração seria interrompida
    (`interromper_em_erro: true`) até a correção manual. **Esta correção
    não foi feita aqui** — exige decisão de quem mantém o currículo sobre
    qual código correto atribuir a cada disciplina.
- **Códigos provisórios**: 47 dos 160 componentes têm código no formato
  `FEELT!XXX` (ex.: `FEELT!AA`, `FEELT!BD`, `FEELT!ESOF`), i.e. ainda sem
  código oficial atribuído. O novo validador sinaliza cada um como
  `[ALERTA] CODIGO_PROVISORIO`.
- **Cargas horárias inconsistentes** (TOT ≠ CHT+CHP+CHD+CHE): **nenhuma**
  encontrada entre os componentes com todas as parcelas não-negativas — a
  planilha legada é internamente consistente nesse quesito.
- **Pré-requisitos referenciando código inexistente**: **nenhum** encontrado.
- **Componentes ativos/inativos**: o schema legado **não tem** um conceito
  de componente ativo/inativo — toda linha do CSV é implicitamente "ativa".
  Ao migrar para o novo modelo (que exige esse campo explicitamente), todos
  os componentes foram marcados `ativo=True` por não haver informação para
  decidir o contrário; **nenhuma inativação foi inferida**.

## 3. O que foi migrado para o novo sistema (levantamento inicial)

*(Histórico — nesta fase o primeiro perfil configurado era o CST de
Controle e Automação, e a migração de Engenharia de Computação para um
perfil próprio ainda não tinha sido feita; ver Seção 7 para o resultado
final.)*

O curso configurado inicialmente (hoje `dados/perfis/controle_automacao_2027_1/`)
**não reaproveitou os dados do curso de Engenharia de Computação** — são
cursos diferentes, com matrizes próprias (Seção 24 exige não copiar
referenciais de Engenharia de Computação para o novo curso).

O que foi construído nesta fase para permitir a migração/comparação, sem
depender de reescrever os dados de Engenharia de Computação à mão:

- `ppcgen.leitores.csv.carregar_csv_legado()`: importador de compatibilidade
  que lê `py/PPC_disciplinas_final.csv` (ou qualquer CSV no mesmo formato) e
  o converte para o novo modelo (`Curriculo`/`ComponenteCurricular`),
  registrando em `alertas_migracao` tudo que não pôde ser mapeado com
  segurança:
  - período `"acc"` (Atividade de Conclusão de Curso) é mapeado para
    `TipoComponente.OUTRO` com alerta explícito, porque o CSV legado não
    distingue Estágio Supervisionado de TCC nessa linha — eram alternativas
    dentro do mesmo componente.
  - múltiplos núcleos marcados na mesma linha (`FORM_BAS`/`FORM_HUM`/
    `FORM_TEC`/`FORM_CMP`) geram alerta e mantêm apenas o primeiro.
  - as colunas `DCN_base`/`DCN_ecp` **não são migradas** — são índices para
    listas de conteúdo específicas da DCN de Computação/CC2020
    (`conteudos_curriculares`, `conteudos_basicos_tecnologicos` em
    `py/gen_docs.py`), que a Seção 24 explicitamente proíbe copiar para o
    novo curso. Ficam preservadas apenas no CSV original.
  - a coluna `QEXTR` (números 2-6 referenciando um dicionário posicional em
    `py/gen_docs.py`) é convertida para os identificadores estáveis
    (`RELACOES_ETNICO_RACIAIS`, `LIBRAS`, `DIREITOS_HUMANOS`,
    `EDUCACAO_AMBIENTAL`, `PREVENCAO_DESASTRES` —
    `ppcgen.leitores.csv.LEGADO_QEXTR_TEMAS`).
  - `CC_UO1`..`CC_HW6` (categorias CC2020/ACM) são convertidas em áreas
    prefixadas `CC2020_*`, mantidas apenas para fins de comparação — não
    fazem parte do catálogo de áreas do curso de Controle e Automação
    (`dados/perfis/controle_automacao_2027_1/referenciais/areas_formacao.yaml`).
- Testes automatizados (`testes/unitarios/test_leitores_csv_legado.py`)
  cobrem a importação do CSV legado, incluindo os casos acima.

*(O arquivo `config/perfis/engenharia_computacao.yaml`, mencionado em
versões anteriores desta seção, não existe mais — era uma reconstrução
manual de parâmetros para fins de documentação, na arquitetura de
configuração única do Task 1. Foi substituído pelo perfil de verdade,
`dados/perfis/engenharia_computacao_2026_1/perfil.yaml`, Seção 7.)*

## 4. Fichas curriculares (levantamento inicial)

*(Histórico — ver Seção 7 para a classificação final.)*

52 fichas em PDF foram encontradas em `fichas/SEI/` (46) e
`fichas/Fichas disciplinas 30h/` (6) — nenhuma foi movida ou apagada nesta
fase. O leitor de fichas (`ppcgen.leitores.fichas`) sabe ler esse mesmo
formato de PDF (campos `COMPONENTE CURRICULAR:`, `CÓDIGO:`, `EMENTA`,
`PROGRAMA` etc.).

## 5. Comparação de saída (antes/depois)

- Uma cópia do PDF do curso de Engenharia de Computação compilado a
  partir do estado original do repositório (99→102 páginas conforme a
  rodada; sem erros de compilação) foi preservada como baseline durante
  toda a migração (arquivada em `legado/main_pdf_baseline/` até a
  remoção final do gerador antigo do repositório — ver Seção 7.5).
- Até essa remoção, rodar `python py/gen_docs.py` (a partir da raiz, com
  `PYTHONUTF8=1` — ver nota abaixo) e depois `latexmk -pdf Main.tex`
  continuou reproduzindo exatamente essa saída — o pipeline antigo não
  foi alterado enquanto existiu no repositório.

### Bug de ambiente encontrado (não corrigido no script legado)

`py/gen_docs.py` quebra em `UnicodeDecodeError` no Windows porque nenhum
`open()` do script especifica `encoding="utf-8"` — funciona por acidente
apenas se o processo já estiver em modo UTF-8 (`PYTHONUTF8=1` ou
console/locale configurado). Isso **não foi corrigido no script legado**
(ele foi deixado intocado para preservar a baseline de comparação), mas o
novo sistema (`ppcgen`) especifica `encoding="utf-8"` em toda leitura e
escrita de arquivo, e força stdout/stderr para UTF-8 na CLI
(`ppcgen.cli._forcar_utf8_console`), eliminando a dependência de variáveis
de ambiente.

## 6. Inconsistências que exigiam decisão acadêmica

Levantadas aqui originalmente sem correção automática; os itens 1 e 2
foram resolvidos posteriormente por decisão do mantenedor (ver nota
abaixo) — mantidos registrados para quem assumir a manutenção do curso
poder auditar a decisão, revertê-la ou submetê-la a validação acadêmica
formal antes de qualquer submissão oficial do PPC.

1. ~~Qual disciplina deveria ficar com o código `FEELT!PP`~~ — resolvido:
   "Programação Procedimental" (2º período, ativa, obrigatória — todas as
   relações de pré-requisito reais, como ser pré-requisito de Estrutura de
   Dados/POO/Sistemas Operacionais e ter Programação Script como seu
   próprio pré-requisito, se encaixam logicamente nela) manteve o código
   `FEELT!PP`. "Arte da Programação II" (3º período, inativa) recebeu o
   código provisório distinto `FEELT!APROG2`. O pré-requisito
   autorreferenciado (`FEELT!PP` exigindo `FEELT!PP`) foi reatribuído como
   `FEELT!APROG2` exigindo `FEELT!PP` — leitura plausível dado o padrão de
   nome ("Parte II" dependendo da disciplina introdutória), mas é uma
   **interpretação, não um fato confirmado pela coordenação do curso** —
   revise antes de qualquer submissão formal.
2. ~~Se a segunda ocorrência de `GBC212`~~ — resolvido como duplicata: as
   duas linhas eram idênticas em todos os campos (nome, carga horária,
   sem nenhuma diferenciação), sem nenhuma referência própria em
   pré-requisitos/áreas/temas/competências — consistente com "linha
   duplicada por engano" (não duas ofertas distintas). A segunda
   ocorrência foi removida.
3. Os 47 códigos provisórios `FEELT!*` (agora 48, incluindo o novo
   `FEELT!APROG2`) ainda precisam do código oficial definitivo antes de
   qualquer submissão formal do PPC — isso não foi resolvido, só a
   colisão entre dois deles.

## 7. Migração final para `dados/perfis/engenharia_computacao_2026_1/`

Depois que a arquitetura de múltiplos perfis existiu, o curso de
Engenharia de Computação foi de fato migrado para um perfil completo e
funcional — não mais só analisado. Processo genérico documentado em
`docs/MIGRAR_PERFIL.md`; esta seção registra o que é específico deste
curso.

### 7.1 Script de migração

Um script dedicado (`scripts/migrar-perfil-legado.py`, removido do
repositório depois de a migração estar completa e confirmada — ver nota
sobre caminhos no topo deste documento) leu
`py/PPC_disciplinas_final.csv` via `ppcgen.leitores.csv.carregar_csv_legado`
e escreveu a árvore completa do perfil: `matriz_curricular.xlsx` (160
componentes), `equivalencias.xlsx` (ver 7.4),
`referenciais/{nucleos,areas_formacao,conteudos,legislacao,temas_transversais}.yaml`,
`figuras/ecp_logo.png`, `referencias/bibliografia.bib` (cópia integral de
`include/backmatter/ppc2025.bib`) e classificou as 52 fichas de
`fichas/SEI/` e `fichas/Fichas disciplinas 30h/` nas subpastas por tipo
(`fichas/{obrigatorias,optativas,extensao,tcc,estagio,complementares}/`),
usando o leitor real de fichas (`ppcgen.leitores.fichas.carregar_fichas`,
não um regex genérico) para casar cada PDF com um componente da matriz por
código extraído do próprio texto, com *fallback* por nome. Resultado: 26
fichas casadas automaticamente, 26 sinalizadas em `fichas/complementares/`
para revisão manual — nenhuma foi descartada nem casada por adivinhação.

Os 12 capítulos de `textos/` foram migrados manualmente a partir de
`include/*.tex` (prosa quase verbatim, ajustando apenas macros e caminhos
de figura) — ver `docs/MIGRAR_PERFIL.md` para o que foi encontrado nesse
processo (seções inteiras de prosa real que o capítulo de Estrutura
Curricular do gerador antigo continha e que precisaram ser migradas à
parte, fora das tabelas geradas automaticamente).

### 7.2 Bugs de leitor encontrados e corrigidos (não são decisões de migração)

Estes eram defeitos genuínos em `ppcgen/leitores/csv.py` e
`ppcgen/leitores/excel.py` — produziam dado incorreto para **qualquer**
curso, não só este; corrigidos com testes cobrindo cada caso:

1. **`PER` negativo lido como período literal.** `"-1"` (convenção do
   script antigo para o pool de equivalências/optativas pré-aprovadas)
   virava `periodo=-1` em vez de `periodo=None`.
2. **Coluna `FLX` ignorada.** Decidia, no script antigo, se uma linha do
   pool de equivalências entrava na soma de carga horária — todo
   componente estava sendo lido como `ativo=True` independente do valor
   real de `FLX`.
3. **Código mágico `"*"` em `PREQ`** (que o script antigo resolvia
   dinamicamente para "carga horária mínima acumulada até o 5º período")
   virava um pré-requisito literal de código `"*"`, disparando
   `PREREQUISITO_CODIGO_MAGICO` em vez de virar
   `carga_horaria_minima` explícito.
4. **`ppcgen.calculo.carga_horaria_oficial` filtrava por
   `componente.obrigatorio`** em vez de `componente.tipo !=
   carga_optativa` — excluía os componentes de Extensão do total oficial
   do curso porque, no CSV legado, extensão tem `OBR=FALSE` (não é "uma
   disciplina obrigatória" no sentido estreito, mas soma no total do
   curso do mesmo jeito). O sintoma que expôs o bug: a carga oficial
   calculada (3105h) divergia da configurada (3450h) por exatamente a
   carga de extensão (345h).
5. **Perda silenciosa de componente com código duplicado
   (`ppcgen.leitores.excel.carregar_matriz`).** A matriz oficial
   (`.xlsx`, não o CSV legado) indexava os componentes lidos num dict por
   `codigo` — se duas linhas tivessem o mesmo código, a segunda
   sobrescrevia a primeira **silenciosamente**, sem nenhum aviso, e o
   validador `CODIGO_DUPLICADO` nunca chegava a ver a duplicata (porque a
   duplicata já não existia mais na estrutura em memória). Foi assim que
   o código duplicado real `FEELT!PP` (Seção 2) ficou invisível mesmo
   depois de migrado para a matriz oficial: "Arte da Programação II"
   desaparecia silenciosamente, restando só "Programação Procedimental"
   sob o mesmo código. Corrigido preservando todas as linhas numa lista
   (o índice por código, usado só para anexar as abas de junção como
   Pré-requisitos/Áreas/Temas, passou a ser uma estrutura auxiliar
   separada) — `CODIGO_DUPLICADO` agora relata corretamente os dois casos
   reais da Seção 2 (`FEELT!PP` e `GBC212`).

### 7.3 `interromper_em_erro: false` — usado temporariamente, depois revertido

Enquanto os 4 erros pré-existentes nos dados de origem (`FEELT!PP`
duplicado e autorreferenciado como pré-requisito de si mesmo, formando um
ciclo; `GBC212` duplicado — Seção 2/6) não tinham sido resolvidos,
`dados/perfis/engenharia_computacao_2026_1/perfil.yaml` declarava
`geracao.interromper_em_erro: false`, com comentário explicando que eram
defeitos da fonte, não da migração, e não impediam a geração de um PPC
utilizável. Depois que a Seção 6 foi resolvida (códigos desambiguados,
duplicata removida), a matriz passou a validar com 0 erros e o campo foi
revertido para `true` — o padrão de todo outro perfil deste repositório.

### 7.4 Disciplinas equivalentes

O gerador antigo produzia um quadro de "Disciplinas Equivalentes"
(`include/auto/tab_disciplinas_equivalentes.tex`) a partir de uma lista
que **não existia em nenhum CSV** — só no LaTeX já gerado. As 18 duplas
reais foram extraídas de lá para
`dados/perfis/engenharia_computacao_2026_1/equivalencias.xlsx` (schema em
`docs/DICIONARIO_DADOS.md`). Quatro entradas do quadro antigo
(`FEELT!PEC30/45/60/75`, "Perspectivas em Engenharia de Computação") não
apontavam para um código de destino real — o quadro antigo usava
`[por tipo]` como texto livre, não um código — e por isso **não foram
migradas** como equivalências estruturadas; ficam para decisão acadêmica
futura, não inventadas.

A funcionalidade de gerar esse quadro a partir de `equivalencias.xlsx`
(`ppcgen.geradores.tabelas.tabela_equivalencias`,
`ppcgen.validadores.prerequisitos.validar_equivalencias`) não existia
antes desta migração — foi construída durante ela, motivada por este caso
real, e agora está disponível para qualquer perfil.

### 7.5 Resultado

- `python -m ppcgen validar --perfil engenharia_computacao_2026_1`: 0
  erros (os 4 pré-existentes nos dados de origem, Seção 6, foram
  resolvidos), ~96 alertas (a maioria: os 48 códigos provisórios
  `FEELT!*` e fichas não reconhecidas/ausentes — esperado antes de uma
  revisão manual completa das 26 fichas em `fichas/complementares/`).
- `python -m ppcgen completo --perfil engenharia_computacao_2026_1`:
  gera com sucesso (`interromper_em_erro: true`, igual aos demais
  perfis), produzindo corpo em ~95 páginas contra 102 do PDF de
  referência do gerador antigo — a diferença remanescente é conteúdo
  bespoke não reproduzido, documentado em comentário no topo de
  `textos/estrutura_curricular.tex` deste perfil.

---

*Script usado para o levantamento da Seção 2 (não faz parte do pacote
`ppcgen` — é uma consulta pontual sobre o CSV legado):*

```python
import csv
from collections import Counter

with open("py/PPC_disciplinas_final.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter=";"))

codigos = Counter(r["Código"] for r in rows)
duplicados = {k: v for k, v in codigos.items() if v > 1}
provisorios = [r["Código"] for r in rows if "?" in r["Código"] or "!" in r["Código"]]
```
