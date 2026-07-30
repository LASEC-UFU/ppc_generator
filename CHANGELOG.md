# Changelog

## [0.3.0] — 2026-07-30 — Limpeza: processo antigo arquivado, código morto removido

### Removido (código morto confirmado — zero referências)

- `ppcgen/excecoes.py`: `ReferenciaInexistente`, `ValidacaoFalhou`,
  `CicloDePrerequisitos` (nunca levantadas/capturadas).
- `ppcgen/modelos.py`: classes `Curso`/`VersaoCurricular` (rascunho
  pré-`CursoConfig`/`InfoPerfil`, nunca conectado), método
  `CargaHoraria.presencial()`, método `ResultadoValidacao.estender()`
  (substituído por `.mesclar()`).
- `ppcgen/perfis.py`: função `listar_perfis()` e campo
  `RefPerfil.origem_registro` (declarados, nunca usados).
- `ppcgen/utilitarios/caminhos.py`: função `resolver()`.
- `testes/conftest.py`: fixture `curriculo_minimo` (nenhum teste a usava).
- `fichas/get_info_fichas.py` e suas saídas abandonadas
  (`PPC_novo_1st.csv`, `PPC_novo_tes.csv`, `perinfo.csv`,
  `Fichas disciplinas 30h.zip`); `py/gera_fluxo_word.py`;
  `py/cleanlatexjunk.sh`; imagens de referência não usadas em nenhum
  `.tex` (`py/ComputerEngineering_CC2020.png`,
  `py/LCK_Landscape of Computing Knowledge.png`); mirrors não
  estruturados (`py/PPC_disciplinas.csv`, `py/PPC disciplinas_final.xlsx`);
  logos de backup sem nenhuma referência
  (`feelt-logo-squared{-white,}-bkp.png`).
- Diretórios vazios sem nenhuma referência no código:
  `templates/relatorios/`, `templates/latex/{componentes,frontmatter,tabelas}/`,
  `fichas/{aprovadas,consolidadas,editaveis,temporarias}/` (convenção do
  Task 1, substituída por `dados/perfis/<id>/fichas/{obrigatorias,...}`).

### Removido — gerador legado (decisão explícita do mantenedor)

- Todo o gerador legado — `Main.tex`, `Main.pdf`, `include/`, `figure/`,
  `py/gen_docs.py`, `py/PPC_disciplinas_final.csv`,
  `fichas/SEI/`, `fichas/Fichas disciplinas 30h/` — foi primeiro
  consolidado em `legado/sistema_antigo/` (confirmado antes: todo texto
  migrado para perfis, toda figura ativa e toda ficha, 52/52, com cópia
  byte-idêntica na nova estrutura — hash SHA-256 —, PPC atual compila sem
  depender de nenhum desses caminhos, nenhum teste os referencia) e, a
  pedido explícito do mantenedor (não pretende re-executar a migração),
  removido do repositório de trabalho. Recuperável pelo histórico do git
  (commit anterior a esta entrada / tag `pre-cleanup-checkpoint`).
- `legado/csv_historico/` e `legado/main_pdf_baseline/` também removidos
  (zero dependentes funcionais, valor apenas de consulta histórica).
- `scripts/migrar-perfil-legado.py` removido junto — sem a fonte antiga
  para ler, não tinha mais como ser executado. A lógica/decisões que ele
  implementava continuam documentadas em `docs/MIGRACAO.md`.

### Encontrado, não resolvido nesta limpeza (documentado para decisão futura)

- Campos de `perfil.yaml` documentados e configurados nos dois perfis
  reais, mas nunca lidos por nenhum validador/gerador:
  `geracao.anexar_fichas`, `geracao.gerar_fluxo_curricular`,
  `curriculo.carga_obrigatoria`, `curriculo.periodo_minimo_tcc`,
  `curriculo.periodo_minimo_estagio`, `curso.sigla`,
  `curso.regime_academico`, `curso.municipio`, `curso.estado`,
  `instituicao.sigla`. Não são código do processo antigo — são escopo
  incompleto da própria reestruturação de perfis.

## [0.2.0] — 2026-07-30 — Reestruturação para múltiplos perfis

### Adicionado

- Arquitetura de perfis: `dados/perfis/<id>/` autocontido (matriz,
  referenciais, textos, fichas, frontmatter, overrides) substitui o
  `config/curso.yaml` único — todo comando exige `--perfil <id>` explícito.
- `dados/compartilhados/` (instituição, legislação, identidade visual,
  referências) + herança explícita via `heranca:` em `perfil.yaml`.
- Herança entre perfis via `extends:` (perfil base), com detecção de
  herança circular e prioridade documentada (perfil atual > base >
  compartilhado > default).
- `templates/latex/` genérico (sem texto de curso) +
  `ppcgen.compiladores.latex.montar_arvore_latex` (substitui
  `ppcgen.geradores.pdf`), montando a árvore final por perfil em
  `saida/<id>/latex/`.
- Novos comandos: `perfis`, `perfil-info`, `perfil-validar`,
  `perfil-criar`, `perfil-clonar`, `validar-todos`/`gerar-todos`/
  `completo-todos` (com filtro `--status`), `limpar --perfil <id>|--todos`.
- Isolamento entre perfis: `Perfil.caminho()` rejeita qualquer caminho
  que escape da pasta do perfil; saída sempre em `saida/<id>/`, nunca
  dentro de `dados/perfis/<id>/`.
- Migração completa do curso de Engenharia de Computação para
  `dados/perfis/engenharia_computacao_2026_1/` (`scripts/migrar-perfil-legado.py`,
  `docs/MIGRACAO.md`) e perfil inicial de Controle e Automação
  (`dados/perfis/controle_automacao_2027_1/`).
- Documentação nova: `docs/PERFIS.md`, `docs/CRIAR_PERFIL.md`,
  `docs/MIGRAR_PERFIL.md`, `docs/DADOS_COMPARTILHADOS.md`,
  `docs/HERANCA_DE_PERFIS.md`, `docs/ESTRUTURA_DE_DIRETORIOS.md`.

### Corrigido

- `ppcgen.calculo.carga_horaria_oficial`: filtrava por
  `componente.obrigatorio` em vez de `tipo != carga_optativa`, excluindo
  componentes de Extensão do total oficial quando `OBR=FALSE` na fonte.
- `ppcgen.leitores.csv`: período negativo (`-1`) lido como período literal
  em vez de indefinido; coluna `FLX` ignorada (todo componente virava
  `ativo=True`); código mágico `"*"` em pré-requisito não convertido para
  `carga_horaria_minima`.
- `ppcgen.leitores.excel.carregar_matriz`: código duplicado na aba
  `Componentes` apagava silenciosamente a primeira ocorrência (dict
  indexado por código) — agora preserva todas as linhas e
  `CODIGO_DUPLICADO` relata corretamente a duplicata.

## [0.1.0] — 2026-07-29 — Reestruturação para gerador configurável

### Adicionado

- Pacote `ppcgen/` (modelos, config, leitores, validadores, geradores, CLI)
  substituindo a lógica monolítica de `py/gen_docs.py` para novos cursos.
- Configuração central do curso (`config/curso.yaml` + `config/perfis/`).
- Referenciais configuráveis fora do código
  (`referenciais/{nucleos,areas_formacao,temas_transversais,competencias,legislacao}.yaml`).
- Matriz curricular oficial estruturada em abas (`dados/matriz_curricular.xlsx`),
  substituindo a ambiguidade de múltiplos arquivos `PPC_disciplinas*.csv`.
- Validador curricular completo (identificação, cargas, extensão, EaD,
  pré-requisitos/correquisitos com detecção de ciclos, referenciais, fichas),
  com relatórios em terminal, HTML e JSON.
- Geradores de tabelas, fluxo curricular, representação gráfica e arquivos
  LaTeX (`latex/gerado/`), cada um com aviso de "gerado automaticamente".
- Comparação entre versões curriculares (`ppcgen comparar`).
- Compilação e consolidação do PDF completo com fichas anexadas
  (`ppcgen completo`).
- Perfil inicial do Curso Superior de Tecnologia em Controle e Automação
  (`config/curso.yaml` ativo, matriz de exemplo em
  `dados/matriz_curricular.xlsx`, gerada por
  `scripts/criar_matriz_exemplo_cst.py`).
- Suíte de testes automatizados (`testes/unitarios`, `testes/integracao`)
  e configuração de lint/formatação (`ruff`).
- `Makefile`, `pyproject.toml`, `.gitignore`.
- Documentação: `README.md`, `docs/ARQUITETURA.md`,
  `docs/DICIONARIO_DADOS.md`, `docs/VALIDACOES.md`,
  `docs/CRIAR_NOVO_CURSO.md`, `docs/MIGRACAO.md`.

### Preservado sem alteração

- `py/gen_docs.py`, `py/PPC_disciplinas_final.csv`, `py/PPC_disciplinas.csv`,
  `Main.tex` (raiz) e `include/**` — o curso de Engenharia de Computação
  continua sendo gerado exatamente como antes.

### Movido (não apagado)

- `py/PPC_disciplinas_{3450,3850,NAO_APAGAR,XXX}.csv` →
  `legado/csv_historico/` (eram variantes não utilizadas pelo gerador; ver
  `docs/MIGRACAO.md`).

### Conhecido/limitações desta versão

- Ver a seção "Limitações conhecidas" em `docs/ARQUITETURA.md`.
