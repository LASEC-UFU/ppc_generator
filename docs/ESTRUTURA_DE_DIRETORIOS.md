# Estrutura de Diretórios

Este documento é o mapa do repositório após a reestruturação para múltiplos
perfis de PPC (ver `docs/PERFIS.md`). A regra geral, detalhada seção a
seção abaixo, é:

```
ppcgen/      -> código genérico, sem nada específico de curso
templates/   -> LaTeX genérico, sem texto de curso nenhum
dados/       -> dados: um perfil por curso/versão/proposta + compartilhados
saida/       -> tudo gerado, um subdiretório por perfil, nunca versionado
testes/      -> testes automatizados (unitários + integração)
docs/        -> esta documentação
scripts/     -> utilitários de linha de comando (setup de ambiente LaTeX)
```

O gerador anterior (script monolítico + LaTeX manual, usado antes desta
reestruturação para o curso de Engenharia de Computação) não está mais no
working tree — foi mantido e depois arquivado em `legado/sistema_antigo/`
durante a migração, e removido depois de confirmada a equivalência de
resultado com o perfil novo (ver `docs/MIGRACAO.md`, Seção 7.5). Continua
recuperável pelo histórico do git (`CHANGELOG.md` tem a referência de
commit).

## `ppcgen/` — código genérico

Nenhum arquivo aqui menciona um curso, uma sigla de disciplina ou um valor
de carga horária específico. Tudo o que varia entre cursos vem de fora, via
`Perfil` (`ppcgen/config.py`).

```
ppcgen/
├── __main__.py          python -m ppcgen
├── cli.py                todos os subcomandos (validar, gerar, compilar,
│                          completo, perfis, perfil-*, *-todos, limpar...)
├── config.py              Perfil, carregamento de perfil.yaml, herança
├── modelos.py             dataclasses de domínio (ComponenteCurricular,
│                          Curriculo, ReferencialCurricular, FichaCurricular...)
├── calculo.py             carga_horaria_oficial() e afins — regras
│                          compartilhadas por validadores e geradores
├── excecoes.py
├── perfis.py              descoberta/listagem de perfis em dados/perfis/
├── scaffolding.py         criar_perfil(), clonar_perfil()
├── leitores/               matriz_curricular.xlsx, referenciais/*.yaml,
│                          fichas (PDF/DOCX), CSV legado (compatibilidade)
├── validadores/            códigos, cargas, extensão, EaD, pré-requisitos,
│                          referenciais, fichas, estrutura do perfil
├── geradores/               tabelas/fluxo/representação gráfica em LaTeX,
│                          relatórios de validação, comparação entre versões
├── compiladores/            monta a árvore LaTeX final e invoca latexmk
└── utilitarios/             caminhos, texto, logging
```

## `templates/` — LaTeX genérico

```
templates/
├── latex/
│   ├── Main.tex                  esqueleto do documento — \input de
│   │                              textos/*.tex do perfil, nunca editado
│   │                              por perfil (ver docs/CRIAR_PERFIL.md)
│   └── configuracoes/
│       └── Estilos.tex           cores, tema de tabela `ppc`, cabeçalhos —
│                                  paleta institucional genérica, sem nome
│                                  de curso
└── relatorios/                   templates HTML dos relatórios de validação
```

## `dados/` — dados curriculares (o que realmente muda entre cursos)

```
dados/
├── perfis/
│   ├── engenharia_computacao_2026_1/
│   ├── controle_automacao_2027_1/
│   └── <outros perfis...>
├── compartilhados/
│   ├── instituicao/       ufu.yaml, feelt.yaml, autoridades.yaml
│   ├── legislacao/        um YAML por norma citável (extensao.yaml, ...)
│   ├── identidade_visual/ cores.yaml + logos/selo (png/jpg)
│   └── referencias/       .bib institucional (referências comuns a vários
│                          perfis)
└── perfis.yaml             opcional — registro explícito de perfis
                             (só necessário para status/ordem customizados;
                             sem ele, todo diretório em dados/perfis/ com um
                             perfil.yaml válido é descoberto automaticamente)
```

Ver `docs/DADOS_COMPARTILHADOS.md` para o que cada arquivo compartilhado
contém e `docs/HERANCA_DE_PERFIS.md` para como um perfil os referencia.

### Um perfil por dentro

Ver `docs/PERFIS.md` (visão geral) e `docs/CRIAR_PERFIL.md` (passo a passo)
para o significado de cada arquivo. Resumo da árvore:

```
dados/perfis/<id>/
├── perfil.yaml                  identidade, curso, currículo, heranca...
├── matriz_curricular.xlsx        fonte oficial dos componentes curriculares
├── equivalencias.xlsx            disciplinas equivalentes pré-aprovadas
├── referenciais/                 nucleos, areas_formacao, competencias,
│                                  conteudos, legislacao, temas_transversais
├── textos/                       12 capítulos em prosa (.tex), obrigatórios
├── frontmatter/                  capa.yaml, autoridades.yaml, comissao.yaml,
│                                  folha_rosto.tex (opcional)
├── referencias/
│   └── bibliografia.bib
├── figuras/                      logo do curso etc. (próprias do perfil)
├── fichas/
│   ├── obrigatorias/ optativas/ extensao/ tcc/ estagio/ complementares/
├── anexos/
│   └── resolucoes/ pareceres/ outros/
└── overrides/
    ├── latex/                    sobrescreve arquivos de templates/latex/
    └── estilos/                  sobrescreve templates/latex/configuracoes/
```

## `saida/` — tudo gerado, nunca editado à mão, nunca versionado

```
saida/
├── engenharia_computacao_2026_1/
│   ├── latex/                    árvore montada por
│   │                              ppcgen.compiladores.latex.montar_arvore_latex
│   │                              (templates + textos do perfil resolvidos
│   │                              pela cadeia de herança + overrides)
│   │   ├── gerado/                tabelas/indicadores gerados a partir da
│   │   │                          matriz — NUNCA editar à mão
│   │   └── build/                 .aux/.log/.bcf do latexmk
│   ├── relatorios/                validacao.html, validacao.json
│   ├── PPC_..._corpo.pdf
│   └── PPC_..._completo.pdf       corpo + fichas + anexos/resolucoes
└── controle_automacao_2027_1/
    └── ...
```

Cada perfil grava exclusivamente dentro do seu próprio `saida/<perfil_id>/`
(Seção 21 — isolamento) — `ppcgen.config.Perfil.caminho()` rejeita qualquer
caminho que tente escapar da pasta do perfil, e a saída nunca é escrita
dentro de `dados/perfis/<id>/`.

**Exceção**: subpastas de `saida/` com prefixo `00` (ex.: `saida/00old/`)
não são saída de nenhum perfil — são material de referência guardado
manualmente por quem estiver comparando gerações (uma cópia antiga do PDF,
por exemplo). `ppcgen limpar --todos` ignora essas pastas de propósito, e
nenhum id de perfil pode começar com `00` (`PERFIL-000`) — assim o prefixo
nunca colide com um perfil real.

## O que NÃO existe mais (arquitetura do Task 1, obsoleta)

Se você encontrar referências a estes caminhos em documentação antiga ou em
anotações locais, elas descrevem a versão anterior a esta reestruturação:

- `config/curso.yaml` (único arquivo de configuração) → substituído por
  `dados/perfis/<id>/perfil.yaml`, um por perfil.
- `dados/matriz_curricular.xlsx` (matriz única na raiz de `dados/`) →
  `dados/perfis/<id>/matriz_curricular.xlsx`.
- `referenciais/*.yaml` na raiz do repositório →
  `dados/perfis/<id>/referenciais/*.yaml` (mais `dados/compartilhados/` para
  o que é comum entre perfis).
- `latex/capitulos/*.tex` → `dados/perfis/<id>/textos/*.tex`.
- `ppcgen.geradores.pdf` → `ppcgen.compiladores.latex`.
- `saida/PPC_corpo.pdf` (saída única na raiz de `saida/`) →
  `saida/<perfil_id>/PPC_..._corpo.pdf`.

## O gerador legado (arquivado no histórico do git)

O script monolítico original (`Main.tex`, `include/`, `figure/`,
`fichas/SEI/`, `fichas/Fichas disciplinas 30h/`, `py/gen_docs.py`,
`py/PPC_disciplinas_final.csv`) foi preservado **funcional e intocado**
durante toda a migração do curso de Engenharia de Computação — primeiro
na raiz do repositório, depois arquivado em `legado/sistema_antigo/` —
para permitir comparar a saída do novo sistema com a antiga (Seção 21 da
especificação original). Confirmada a equivalência de resultado (ver
`docs/MIGRACAO.md`, Seção 7.5), foi removido do working tree; continua
recuperável pelo histórico do git (ver `CHANGELOG.md` para a referência
de commit). Nenhum caminho do gerador antigo deve ser referenciado por
`ppcgen/` ou por `templates/` — se você encontrar uma referência, é
resíduo de documentação desatualizada, não uma dependência real.
