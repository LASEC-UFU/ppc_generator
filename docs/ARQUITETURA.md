# Arquitetura do ppcgen

## Visão geral

O sistema é organizado em torno de **perfis** (`dados/perfis/<id>/`): cada
perfil é um curso/versão/proposta autocontido, e todo comando exige um
perfil explícito (`--perfil <id>`) — não existe um curso "padrão"
embutido no código. Ver `docs/PERFIS.md` para o conceito completo e
`docs/ESTRUTURA_DE_DIRETORIOS.md` para o mapa de diretórios.

```
dados/perfis/<id>/perfil.yaml + matriz_curricular.xlsx + referenciais/*.yaml
   (+ heranca: dados/compartilhados/..., + extends: outro perfil)
                              │
                              ▼
                  ppcgen.config.carregar_perfil  →  Perfil
                              │
                              ▼
                     ppcgen.leitores.* (matriz, referenciais, fichas)
                              │
                              ▼
                 ppcgen.modelos.Curriculo (+ ReferenciaisCurso)
                              │
                              ▼
        ppcgen.validadores.perfil.validar_perfil  (estrutura do perfil)
        ppcgen.validadores.curriculo.validar_curriculo
         (codigos, cargas, extensao, ead, prerequisitos/equivalencias,
          referenciais, fichas)
                              │
                     ResultadoValidacao (ERRO/ALERTA/INFORMACAO)
                              │
                 ┌────────────┴─────────────┐
                 ▼                          ▼
  saida/<id>/relatorios/validacao.*  ppcgen.geradores.latex
                                     (tabelas, fluxo, representação gráfica)
                                              │
                                              ▼
                                saida/<id>/latex/gerado/*.tex
                                              │
                       ppcgen.compiladores.latex.montar_arvore_latex
                    (templates/latex/ + textos/figuras do perfil, resolvidos
                     pela cadeia de `extends`, com overrides/ por cima)
                                              │
                                              ▼
                       ppcgen.compiladores.latex.compilar_pdf
                                              │
                                              ▼
                          saida/<id>/PPC_..._corpo.pdf
                                              │
                (+ fichas em PDF na ordem curricular, + anexos/resolucoes)
                                              ▼
                        saida/<id>/PPC_..._completo.pdf
```

Tudo isso é orquestrado pela CLI (`ppcgen.cli`), nunca por um script único —
cada seta acima corresponde a um módulo com responsabilidade única. Nenhum
módulo em `ppcgen/` conhece um curso específico: tudo o que varia entre
perfis entra através do objeto `Perfil` (`ppcgen/config.py`).

## Por que a estrutura de dados difere ligeiramente da Seção 2/3 da proposta

A proposta original sugere 11 abas na matriz curricular, incluindo "Núcleos"
e "Optativas" como abas próprias. A implementação usa 9 abas
(`ppcgen/leitores/excel.py`, schema completo em `docs/DICIONARIO_DADOS.md`),
por uma razão concreta:

- **Núcleo é uma coluna em `Componentes`, não uma aba separada.** Um
  componente tem exatamente um núcleo (cardinalidade 1) — uma aba de junção
  para uma relação 1:1 duplicaria a mesma informação em dois lugares sem
  nenhum ganho, violando a regra de não manter duas fontes para o mesmo
  dado (Seção 29). Área, tema transversal e competência, que são relações
  1:N, continuam como abas de junção próprias.
- **Optativa não é uma aba separada — é um valor de `tipo`
  (`carga_optativa`).** O modelo de domínio (Seção 5) já pede que o
  comportamento dependa do campo `tipo`, não de convenções de posição na
  planilha. Colocar as optativas em uma aba à parte reintroduziria a mesma
  ambiguidade que a Seção 3 pede para eliminar (qual aba é "a" fonte de uma
  optativa: a aba `Componentes` ou a aba `Optativas`?).

O catálogo dos núcleos/áreas/temas/competências/conteúdos (id →
nome/descrição/fonte) fica em `dados/perfis/<id>/referenciais/*.yaml`, não
na planilha — são vocabulários que mudam raramente e podem ser
compartilhados entre versões curriculares (via `extends`, ver
`docs/HERANCA_DE_PERFIS.md`); a planilha guarda apenas qual componente usa
qual item do catálogo.

## Carga horária "oficial" vs. soma bruta (`ppcgen/calculo.py`)

Um pool de disciplinas optativas pré-aprovadas quase sempre soma mais horas
do que o estudante de fato cursa (ele escolhe um subconjunto). Por isso:

- `Curriculo.carga_horaria_total()` — soma bruta de **todos** os
  componentes ativos, incluindo o pool inteiro de optativas. Útil para
  conferir se o pool oferece horas suficientes (`POOL_OPTATIVAS_INSUFICIENTE`).
- `ppcgen.calculo.carga_horaria_oficial(curriculo, perfil)` — soma dos
  componentes **ativos com `tipo != carga_optativa`** +
  `curriculo.carga_optativa_minima` configurado. É este valor (não o
  anterior) que é comparado contra `curriculo.carga_horaria_total` do
  `perfil.yaml`, usado como denominador dos percentuais de EaD/extensão, e
  usado nas tabelas de distribuição de carga por núcleo/área/modalidade
  geradas em LaTeX.

  O filtro é por **tipo**, não pelo campo `obrigatorio` — um componente de
  extensão ou de atividade complementar pode ter `obrigatorio=FALSE` na
  fonte de dados (ele não é "uma disciplina obrigatória") e, ainda assim,
  ser de cumprimento mandatório para todo estudante, contando no total do
  curso. Foi exatamente essa distinção que a migração do curso de
  Engenharia de Computação expôs (`docs/MIGRACAO.md`, Seção 7.2): os
  componentes de extensão do CSV legado têm `OBR=FALSE`, mas somam no
  total histórico de 3450h — filtrar por `obrigatorio` excluía a carga de
  extensão inteira do total oficial.

Essa distinção evita um problema real: se o percentual de EaD ou de
extensão fosse calculado sobre a soma bruta (que cresce conforme mais
optativas são cadastradas), aumentar o catálogo de optativas — sem qualquer
mudança curricular real — mudaria artificialmente esses percentuais.

## O que é versionado e o que é gerado

- **`saida/` é inteiramente gitignorado.** Cada arquivo em
  `saida/<perfil>/latex/gerado/*.tex` carrega um timestamp no cabeçalho
  (`% Gerado em: ...`), então toda execução de `python -m ppcgen gerar`
  produziria um diff no controle de versão mesmo sem nenhuma mudança real
  — puro ruído. A reprodutibilidade não depende de versionar esses
  arquivos: rodar `ppcgen gerar` a partir de
  `dados/perfis/<id>/matriz_curricular.xlsx` sempre os recria de forma
  determinística (dado o mesmo insumo, o único campo que varia é o
  timestamp).
- **O gerador antigo não faz mais parte do working tree.** Durante a
  migração do curso de Engenharia de Computação ele foi mantido
  versionado e intocado (primeiro na raiz, depois arquivado em
  `legado/sistema_antigo/`) exatamente para permitir essa comparação —
  capacidade exigida pela especificação original (Seção 21) e usada em
  `docs/MIGRACAO.md`. Uma vez confirmada a equivalência de resultado
  (Seção 7.5 de `docs/MIGRACAO.md`), foi removido; continua recuperável
  pelo histórico do git (ver `CHANGELOG.md`).

## Compatibilidade com o CSV legado

`ppcgen.leitores.csv.carregar_csv_legado()` lê o formato usado pelo CSV
do gerador antigo (`PPC_disciplinas_final.csv` — ver `docs/MIGRACAO.md`)
e converte para o novo modelo — usado para migração/comparação (ver
`docs/MIGRACAO.md`/`docs/MIGRAR_PERFIL.md`), não como fonte oficial do
novo sistema (essa é sempre `dados/perfis/<id>/matriz_curricular.xlsx`).

## Fichas: adaptadores por formato, sem OCR como estratégia principal

`ppcgen.leitores.fichas` define uma interface (`LeitorFicha`) com um
adaptador por formato (`LeitorFichaPDF`, `LeitorFichaDOCX`), em vez de uma
bateria de regex genéricas tentando cobrir todos os casos. Um PDF sem
camada de texto extraível (menos de 200 caracteres) é marcado
`confianca_extracao=0.0` e classificado como "não reconhecida" — esta
versão **não** embute um motor de OCR; é uma limitação registrada, não uma
tentativa de resolver o problema por um caminho frágil.

## Limitações conhecidas desta versão

- A representação gráfica do fluxo curricular usa uma tabela simples (uma
  linha por componente) em vez do layout com células mescladas
  (`\SetCell[r=n]`) do script legado — mais simples de gerar e manter
  corretamente, ao custo de um pouco de densidade visual.
- `ppcgen.compiladores.latex.montar_pdf_completo` só anexa fichas que já
  estão em PDF; fichas em DOCX são reportadas para conversão manual, não
  convertidas automaticamente (evita depender de um conversor DOCX→PDF
  externo).
- Comparação entre versões curriculares (`ppcgen.geradores.comparacao`) não
  tenta inferir renomeações de código automaticamente — usa apenas
  correspondência exata de código. Renomeações reais devem ser registradas
  na aba `Equivalencias` ou no arquivo dedicado `equivalencias.xlsx` (ver
  `docs/DICIONARIO_DADOS.md`).
- A tabela "Disciplinas Equivalentes" (`docs/DICIONARIO_DADOS.md`,
  `equivalencias.xlsx`) e a comparação entre versões curriculares
  (`ppcgen.geradores.comparacao`) modelam conceitos diferentes: a primeira
  é para o texto do PPC ("se não puder cursar X, Y é equivalente"); a
  segunda é uma ferramenta de auditoria entre duas matrizes, não usada na
  geração do documento.
