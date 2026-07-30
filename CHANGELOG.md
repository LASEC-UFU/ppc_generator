# Changelog

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
