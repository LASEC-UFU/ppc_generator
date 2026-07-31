# Migrar um Curso Existente para um Perfil

Guia para trazer um PPC que já existe em outro formato (planilha solta,
CSV, um gerador LaTeX monolítico anterior...) para dentro da estrutura de
perfis deste repositório. Usa como exemplo real a migração do curso de
Engenharia de Computação (de um gerador LaTeX monolítico com CSV próprio)
para `dados/perfis/engenharia_computacao_2026_1/`. O sistema antigo em si
e o script que fez essa migração já cumpriram seu papel e não fazem mais
parte deste repositório (só do histórico do git) — o que segue é o
*processo* genérico, para migrar qualquer outro curso.

## Princípio geral: nunca perder dado silenciosamente

Toda migração real encontra dado ambíguo, incompleto ou que não mapeia
limpo para o novo modelo. A regra deste projeto (Seção 23/29 da
especificação original) é: **registre um alerta e preserve a decisão
manual necessária — nunca "corrija" ou descarte um dado curricular sem
que um humano veja isso.** `ppcgen.leitores.csv.carregar_csv_legado`
segue esse padrão à risca — vale ler o código como referência antes de
escrever um script de migração próprio.

## Passo a passo

### 1. Não apague a fonte antiga até validar a equivalência

Mantenha o gerador/dados antigos funcionando até confirmar que o perfil
novo produz um resultado equivalente (ver "Comparando com o resultado
antigo" abaixo) — só depois disso arquive ou remova a fonte antiga. Foi
assim que a migração de Engenharia de Computação foi feita: o gerador
antigo (`gen_docs.py` + `include/*.tex` + o CSV de origem) ficou
preservado e funcional durante toda a migração — primeiro arquivado em
`legado/sistema_antigo/` para comparação, e só removido do repositório
depois de confirmada a equivalência e decidido que a capacidade de
recompilar o original do zero não seria mais necessária (essa decisão é
sua para cada migração — nada obriga a remover a fonte antiga depois).

### 2. Escreva um script de migração, não migre à mão

Um script de migração deve:

- ler a fonte antiga com um leitor dedicado (ex.:
  `ppcgen.leitores.csv.carregar_csv_legado`, usado para o CSV legado de
  Engenharia de Computação — só existe para compatibilidade/migração,
  nunca é a fonte oficial do sistema novo);
- escrever `matriz_curricular.xlsx` no schema novo
  (`docs/DICIONARIO_DADOS.md`);
- extrair catálogos hardcoded do gerador antigo (ex.: listas de conteúdo
  fixas no código-fonte de um gerador anterior) para as abas de registro
  da matriz (`Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`,
  populando a coluna `componentes` de cada uma) ou para `legislacao:` em
  `perfil.yaml`, conforme o caso — ver `docs/DICIONARIO_DADOS.md` —
  documentando de onde vieram, nunca inventando ids novos silenciosamente;
- copiar fichas curriculares para as subpastas por tipo, usando o leitor
  real de fichas (`ppcgen.leitores.fichas.carregar_fichas`) para casar
  cada arquivo com um componente da matriz — fichas não reconhecidas vão
  para `fichas/complementares/` e ficam sinalizadas para revisão manual,
  nunca descartadas nem "adivinhadas";
- recusar sobrescrever um perfil já existente (proteção contra rodar
  duas vezes por engano e perder edições manuais feitas depois da
  primeira migração).

O script usado para migrar Engenharia de Computação seguiu exatamente
esse padrão — depois de a migração estar completa e confirmada, ele
deixou de ter utilidade (não há mais fonte antiga para ler) e foi
removido junto do gerador antigo. Continua disponível no histórico do
git de quem quiser usá-lo como ponto de partida.

### 3. Decisões de migração são decisões, não bugs

Ao migrar dados reais você vai encontrar casos que o formato antigo
resolvia de um jeito que o novo modelo não reproduz 1:1. Documente a
decisão explicitamente (comentário no script + entrada abaixo, "Decisões
de migração registradas"), não silencie. Exemplos reais encontrados nesta
migração:

- O CSV legado tinha um período `"acc"` que cobria tanto Estágio quanto
  TCC sem distinguir qual — mapeado para `TipoComponente.OUTRO` com um
  alerta explícito, em vez de adivinhar um dos dois.
- Colunas `DCN_base`/`DCN_ecp` eram índices em listas Python hardcoded no
  gerador antigo, específicas da DCN de Computação — não fazem sentido
  para outro curso, então não viraram um campo genérico do modelo; os
  valores ficam preservados via `referenciais/conteudos.yaml` só para
  este perfil.
- Um código duplicado genuíno no currículo de origem (`FEELT!PP` aparece
  como pré-requisito de si mesmo) foi **mantido e reportado como erro de
  validação**, não corrigido silenciosamente — é um problema real dos
  dados de origem que precisa de decisão acadêmica, não de código.

### 4. Bugs de leitor encontrados e corrigidos durante esta migração

Estes eram bugs genuínos no leitor (`ppcgen/leitores/csv.py`), não
decisões de migração — corrigidos porque produziam dado errado, com
testes cobrindo cada caso depois:

- `PER` negativo (ex. `-1`, convenção do script antigo para "pool sem
  período fixo") estava sendo lido como um período literal `-1` em vez de
  `None`.
- A coluna `FLX` (que no script antigo decidia se uma linha do pool de
  equivalências entrava na soma de carga horária) não era lida — todo
  componente virava `ativo=True` independente de `FLX`.
- O código mágico `"*"` em `PREQ` (que o script antigo resolvia
  dinamicamente para "carga horária mínima acumulada até o 5º período")
  virava um `PreRequisito(codigo="*")` literal, disparando
  `PREREQUISITO_CODIGO_MAGICO` em vez de ser convertido para
  `carga_horaria_minima` explícito.
- `ppcgen.calculo.carga_horaria_oficial` somava por `componente.obrigatorio`
  em vez de `componente.tipo != carga_optativa` — excluía componentes de
  Extensão do total oficial porque o CSV legado marca extensão como
  `OBR=FALSE` (não é "uma disciplina obrigatória", mas ainda soma no
  total do curso). O gap era exatamente a carga de extensão configurada
  (345h), o que ajudou a localizar a causa.

Se você migrar outro curso e encontrar um padrão parecido (leitor
silenciosamente errado vs. decisão de migração legítima), corrija o
leitor — ele deve estar certo para qualquer curso, não só para o que foi
usado para descobrir o bug.

### 5. `interromper_em_erro: false` — use com uma linha de justificativa

Um perfil migrado de dados reais tipicamente chega com alguns erros
genuínos pré-existentes nos dados de origem (como o `FEELT!PP`
autorreferenciado acima) que não bloqueiam o uso prático do PPC enquanto
uma decisão acadêmica não é tomada. Nesse caso, `perfil.yaml` pode setar
`geracao.interromper_em_erro: false` — mas sempre com um comentário no
próprio YAML explicando qual erro é tolerado e por quê, nunca como forma
de silenciar validação de verdade.

### 6. Comparando com o resultado antigo

Depois que o perfil novo compila:

- **Carga horária total**: confira `saida/<id>/latex/gerado/par_carga_horaria_total.tex`
  contra o valor histórico conhecido do curso.
- **Contagem de páginas**: compare o PDF novo
  (`saida/<id>/PPC_..._corpo.pdf`) com o PDF antigo — diferença grande
  geralmente indica conteúdo do capítulo antigo que não foi migrado (ex.:
  seções de prosa que o gerador antigo produzia via tabelas bespoke que o
  novo sistema não reproduz automaticamente).
- **Capítulos**: confira que os 12 capítulos têm conteúdo real
  equivalente, não só os placeholders do scaffold.
- **Bibliografia**: as referências vão na aba `Bibliografia` da matriz
  (uma linha por entrada — ver `docs/DICIONARIO_DADOS.md`), nunca num
  `.bib` solto. Confira que as citações usadas nos capítulos migrados
  resolvem (`latexmk`/`biber` avisam sobre citação indefinida no log).
- **Erros/alertas de validação**: rode `python -m ppcgen validar --perfil
  <id>` e revise cada um — a meta não é zero alertas (dados reais têm
  imperfeições reais), é que cada um seja **conhecido e intencional**, não
  uma surpresa.

Nesta migração específica, o resultado final ficou em ~95 páginas (corpo)
contra 102 do PDF de referência do gerador antigo (comparação feita antes
do gerador antigo ser removido do repositório). A diferença remanescente
vem de conteúdo bespoke do capítulo
de estrutura curricular que o gerador antigo produzia via tabelas fixas em
LaTeX (quadro de carga horária semanal por período, uma tabela alternativa
de fluxo "conforme guia", e um quadro de mapeamento de conteúdo específico
de IA) e que não foi reproduzido — cada um exigiria um gerador novo e
dedicado, fora do escopo desta migração inicial. Ver comentário em
`dados/perfis/engenharia_computacao_2026_1/textos/estrutura_curricular.tex`.
