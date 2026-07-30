# ppcgen — Gerador de Projeto Pedagógico de Curso

## 1. Objetivo

Gera o corpo e a versão completa (com fichas de componentes e resoluções
anexadas) de um Projeto Pedagógico de Curso (PPC) a partir de uma matriz
curricular e de um **perfil** — sem regras específicas de nenhum curso
fixadas no código.

O sistema suporta **múltiplos perfis simultâneos e independentes** no
mesmo repositório: cursos diferentes, versões curriculares diferentes do
mesmo curso, ou propostas alternativas em avaliação. Cada perfil é
autocontido em `dados/perfis/<id>/` e todo comando exige um perfil
explícito (`--perfil <id>`) — não existe um curso "padrão" embutido no
código. Ver `docs/PERFIS.md`.

Este repositório traz três perfis de exemplo:

- `engenharia_computacao_2026_1` — curso real, migrado do gerador anterior,
  com dados/currículo/fichas reais.
- `controle_automacao_2027_1` — proposta de um Curso Superior de
  Tecnologia em Controle e Automação, construído para este novo sistema.
- `perfil_minimo` (em `testes/perfis_exemplo/`) — perfil mínimo sintético
  usado pelos testes automatizados.

O gerador anterior (`gen_docs.py` + `Main.tex` + `include/`), que
produzia o PPC de Engenharia de Computação antes desta reestruturação,
foi mantido funcional e intocado durante toda a migração — só removido
do repositório depois de confirmada a equivalência de resultado com o
perfil novo. Continua recuperável pelo histórico do git. Ver
`docs/MIGRACAO.md`/`docs/MIGRAR_PERFIL.md` para o relato completo e
`CHANGELOG.md` para a referência de commit.

## 2. Arquitetura

```
dados/perfis/<id>/perfil.yaml + matriz_curricular.xlsx + referenciais/*.yaml
  (+ heranca: dados/compartilhados/, + extends: outro perfil)
     → ppcgen.leitores → ppcgen.validadores → ppcgen.geradores
     → ppcgen.compiladores → PDF em saida/<id>/
```

Detalhes e decisões de design em `docs/ARQUITETURA.md`. Mapa completo de
diretórios em `docs/ESTRUTURA_DE_DIRETORIOS.md`.

```
ppcgen/             pacote Python genérico (leitores, validadores,
                     geradores, compiladores, CLI) — nada específico de
                     curso
templates/          LaTeX genérico (Main.tex + configuracoes/) — sem
                     texto de curso nenhum
dados/
  perfis/<id>/       um curso/versão/proposta por pasta, autocontido
  compartilhados/    dados institucionais comuns a vários perfis
                      (referenciados explicitamente via heranca:)
saida/<id>/          PDFs e relatórios gerados (gitignorado)
testes/              testes unitários e de integração (pytest)
docs/                esta documentação
scripts/             setup de ambiente LaTeX
```

## 3. Requisitos

- Python ≥ 3.11
- Uma distribuição LaTeX com `latexmk`/`biber` (MiKTeX ou TeX Live) e os
  pacotes usados por `templates/latex/` (`tabularray`, `biblatex`,
  `geometry`, `fancyhdr`... — lista completa e scripts de setup/
  verificação em `scripts/install-latex-minimal.ps1` e
  `scripts/verify-latex-environment.ps1`), apenas para compilar o PDF
  (`compilar`/`completo`) — `validar`/`gerar`/`comparar` não precisam de
  LaTeX instalado.

## 4. Instalação

```
python -m pip install -e .[dev]
```

## 5. Perfis: listar, inspecionar, criar

```
python -m ppcgen perfis                                # lista todos os perfis
python -m ppcgen perfil-info --perfil <id>              # dados carregados de um perfil
python -m ppcgen perfil-criar --id <id> --nome "..."     # estrutura inicial de um perfil novo
python -m ppcgen perfil-clonar --origem <id> --destino <novo-id>
```

Passo a passo completo para criar um perfil novo: `docs/CRIAR_PERFIL.md`.
Para migrar um curso que já existe em outro formato: `docs/MIGRAR_PERFIL.md`.

## 6. Estrutura da planilha / significado de cada campo

Ver `docs/DICIONARIO_DADOS.md` — todas as abas/arquivos, campos, tipos,
valores possíveis e a regra de validação associada a cada um.

## 7. Validação

```
python -m ppcgen perfil-validar --perfil <id>            # só estrutura do perfil
python -m ppcgen validar        --perfil <id>            # currículo (+ fichas, se presentes)
python -m ppcgen validar-fichas --perfil <id>             # só fichas
```

Lista completa das regras em `docs/VALIDACOES.md`. Saída: terminal +
`saida/<id>/relatorios/validacao.html` + `.json`.

## 8. Geração, compilação, PPC completo

```
python -m ppcgen gerar    --perfil <id>   # tabelas/fluxo/indicadores em saida/<id>/latex/gerado/
python -m ppcgen compilar --perfil <id>   # compila saida/<id>/latex/Main.tex
python -m ppcgen completo --perfil <id>   # valida + gera + compila + anexa fichas/resoluções
```

`completo` produz `saida/<id>/PPC_..._corpo.pdf` (o texto) e
`saida/<id>/PPC_..._completo.pdf` (corpo + fichas em PDF na ordem
curricular + anexos de `anexos/resolucoes/`). Fichas que não estejam em
PDF (ex.: DOCX ainda não exportado) são listadas no final, não anexadas
silenciosamente. Arquivos em `saida/<id>/latex/gerado/` nunca devem ser
editados manualmente — são recriados a cada execução e carregam o aviso
"ARQUIVO GERADO AUTOMATICAMENTE" no topo.

## 9. Operações em lote (todos os perfis ativos)

```
python -m ppcgen validar-todos [--status <s>]
python -m ppcgen gerar-todos [--status <s>]
python -m ppcgen completo-todos [--status <s>]
```

Por padrão pulam perfis com `status: descontinuado`; `--status` filtra
por um valor específico (ex.: `--status vigente`).

## 10. Comparação entre versões curriculares

```
python -m ppcgen comparar --anterior <matriz-anterior.xlsx> --atual <matriz-atual.xlsx>
```

Produz um relatório HTML/JSON (incluídos, removidos, alterados campo a
campo, impacto sobre carga total/extensão/EaD/competências) — ferramenta
de auditoria entre duas matrizes quaisquer, independente de perfil.

## 11. Limpeza

```
python -m ppcgen limpar --perfil <id>   # remove saida/<id>/ (nunca dados/)
python -m ppcgen limpar --todos
```

## 12. Isolamento entre perfis

Cada perfil só lê/grava dentro da própria pasta (`dados/perfis/<id>/`),
exceto o que declarar explicitamente em `heranca:`
(`docs/DADOS_COMPARTILHADOS.md`) ou `extends:` (`docs/HERANCA_DE_PERFIS.md`).
Saída de um perfil nunca é escrita dentro de outro, nem dentro da própria
pasta de dados do perfil — sempre em `saida/<id>/`. Um caminho que tente
escapar da pasta do perfil (`../outro_perfil/...`) é rejeitado com erro.

## 13. Solução de erros frequentes

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Informe --perfil <id> ou --perfil-dir <caminho>` | nenhum perfil selecionado | todo comando exige seleção explícita — ver `docs/PERFIS.md` (inclusive a conveniência opcional `.ppcgen.local.yaml` para desenvolvimento local) |
| `ConfiguracaoInvalida: Campo(s) desconhecido(s)` | campo digitado errado em `perfil.yaml` | conferir grafia contra `ppcgen/config.py` / `docs/PERFIS.md` |
| `ConfiguracaoInvalida: Caminho ... escapa da sua própria pasta` | um `arquivos.*`/caminho tentando sair da pasta do perfil | use `heranca`/`extends` para compartilhar dados entre perfis, nunca um caminho relativo `../` |
| `FormatoInvalido: Aba obrigatória ausente` | aba `Curso` ou `Componentes` faltando/renomeada no `.xlsx` | conferir nomes exatos das abas (`docs/DICIONARIO_DADOS.md`) |
| `[ERRO] CARGA_TOTAL_INCONSISTENTE` | `tot` não bate com `cht+chp+chd+che` | corrigir a planilha (o validador não infere qual campo está errado) |
| `[ERRO] CICLO_PREREQUISITOS` | dependência circular | a mensagem mostra o caminho completo do ciclo — remover uma das arestas |
| `Herança circular de perfis detectada` | `extends` formando um ciclo entre perfis | corrigir a cadeia de `extends` em `perfil.yaml` |
| Compilação LaTeX falha com "fresh installation"/"no repository" (MiKTeX) | MiKTeX novo, sem repositório de pacotes configurado | rode `scripts/install-latex-minimal.ps1`, depois `scripts/verify-latex-environment.ps1` |
| Acentos ilegíveis no terminal (Windows) | codepage do console, não um bug de dados | a CLI já força UTF-8 em stdout/stderr; os arquivos gerados sempre estão corretos em UTF-8 |

## 14. Fluxo de trabalho recomendado

1. Editar `dados/perfis/<id>/matriz_curricular.xlsx` (ou
   `referenciais/*.yaml`, `perfil.yaml`, `textos/*.tex`).
2. `python -m ppcgen validar --perfil <id>` até revisar todos os erros.
3. `python -m ppcgen completo --perfil <id>` (ou `make complete
   PROFILE=<id>`).
4. Revisar `saida/<id>/PPC_..._corpo.pdf` / `_completo.pdf` e os
   relatórios em `saida/<id>/relatorios/`.
5. Commitar `dados/` — nunca `saida/`.

## Comandos (Makefile)

Os alvos de um único perfil exigem `PROFILE=<id>`:

```
make install
make perfis
make perfil-info    PROFILE=<id>
make perfil-validar PROFILE=<id>
make validate       PROFILE=<id>
make generate       PROFILE=<id>
make pdf            PROFILE=<id>
make complete       PROFILE=<id>
make clean          PROFILE=<id>

make validate-all [STATUS=<s>]
make generate-all [STATUS=<s>]
make complete-all [STATUS=<s>]
make clean-all

make perfil-criar  ID=<id> NOME="Nome do Curso"
make perfil-clonar ORIGEM=<id> DESTINO=<novo-id>
make compare ANTERIOR=... ATUAL=...

make test       # pytest
make lint       # ruff check
make format     # ruff format
```

Em Windows sem `make` instalado (ex.: via `choco install make` ou WSL),
rode os comandos `python -m ppcgen ...` equivalentes diretamente — é
exatamente o que cada alvo do Makefile faz.

## Documentação adicional

- `docs/PERFIS.md` — o que é um perfil, schema de `perfil.yaml`, comandos.
- `docs/CRIAR_PERFIL.md` — passo a passo para criar um perfil novo.
- `docs/MIGRAR_PERFIL.md` — passo a passo para migrar um curso existente.
- `docs/DADOS_COMPARTILHADOS.md` — dados institucionais comuns a vários perfis.
- `docs/HERANCA_DE_PERFIS.md` — `extends` (perfil base) e `heranca`
  (dados compartilhados): mecanismos, prioridade, detecção de ciclo.
- `docs/ESTRUTURA_DE_DIRETORIOS.md` — mapa completo do repositório.
- `docs/ARQUITETURA.md` — decisões de design e limitações conhecidas.
- `docs/DICIONARIO_DADOS.md` — todos os campos de todas as fontes de dados.
- `docs/VALIDACOES.md` — toda regra de validação, severidade e condição.
- `docs/MIGRACAO.md` — o que foi migrado do sistema anterior para o perfil
  `engenharia_computacao_2026_1` e o que exige decisão acadêmica.
- `CHANGELOG.md` — histórico desta reestruturação.
