# Herança de Perfis

Existem **dois mecanismos de herança diferentes**, que resolvem problemas
diferentes e não devem ser confundidos:

| Mecanismo | Campo em `perfil.yaml` | Para quê |
|---|---|---|
| Perfil base | `perfil.extends: <id>` | Reaproveitar/derivar um perfil inteiro de outro (ex.: uma nova versão curricular a partir da anterior) |
| Dados compartilhados | `heranca:` | Referenciar dados institucionais comuns a vários cursos (endereço da universidade, legislação, identidade visual) sem duplicá-los em cada perfil |

Nenhum dos dois é implícito — um perfil sem `extends` e sem `heranca` é
100% autocontido e não lê nada fora da própria pasta.

## 1. Perfil base (`extends`)

```yaml
perfil:
  id: engenharia_computacao_2026_2
  extends: engenharia_computacao_2026_1
```

Ao carregar `engenharia_computacao_2026_2`, `ppcgen.config.carregar_perfil`
carrega recursivamente `engenharia_computacao_2026_1` como
`perfil.perfil_base` e mescla a configuração efetiva
(`perfil.yaml` → seções `curso`/`curriculo`/`arquivos`/`geracao`/`saida`)
com prioridade para o perfil atual.

**Arquivos de dados** (matriz, textos, referenciais, figuras, fichas...)
**não são mesclados campo a campo** — são resolvidos por
`Perfil.resolver_arquivo(caminho_relativo)`: primeiro procura no perfil
atual; se o arquivo não existir ali, procura no perfil base, recursivamente
pela cadeia de `extends`. Ou seja, um perfil derivado só precisa conter os
arquivos que de fato mudaram em relação ao perfil base — tudo o mais é
herdado por ausência.

Isso vale para: `matriz_curricular.xlsx`, `equivalencias.xlsx`,
`referencias/bibliografia.bib`. Para `textos/`, `figuras/` e
`frontmatter/folha_rosto.tex`, o comportamento é ligeiramente diferente na
montagem do LaTeX final (ver seção "Como a herança afeta a compilação"
abaixo): a árvore compilada recebe a união de todos os arquivos ao longo
da cadeia, do mais base ao mais específico, com o perfil atual sempre
vencendo em caso de mesmo nome de arquivo.

### Detecção de herança circular

`carregar_perfil` mantém uma pilha de ids visitados; se `A extends B` e `B
extends A` (direta ou transitivamente), o carregamento falha com
`ConfiguracaoInvalida("Herança circular de perfis detectada: A -> B -> A")`
em vez de recursão infinita.

## 2. Dados compartilhados (`heranca`)

```yaml
heranca:
  instituicao: compartilhados/instituicao/ufu.yaml
  unidade: compartilhados/instituicao/feelt.yaml
  identidade_visual: compartilhados/identidade_visual/cores.yaml
  autoridades: compartilhados/instituicao/autoridades.yaml
  referencias:
    - compartilhados/referencias/referencias_institucionais.bib
  legislacao:
    - compartilhados/legislacao/extensao.yaml
    - compartilhados/legislacao/direitos_humanos.yaml
```

Todos os caminhos são relativos a `dados/` (a "raiz de dados", não à pasta
do perfil) — ver `docs/DADOS_COMPARTILHADOS.md` para o conteúdo esperado de
cada arquivo. Nenhum destes campos existe por padrão; um perfil que não
declarar `heranca.legislacao`, por exemplo, simplesmente não recebe nenhuma
norma compartilhada — só as que ele próprio definir em
`referenciais/legislacao.yaml`.

## Prioridade de valores

Quando o mesmo campo pode vir de mais de uma fonte, a ordem de prioridade
(maior primeiro) é:

```
1. valores definidos no perfil.yaml do perfil atual
2. valores herdados do perfil base (extends), recursivamente
3. valores compartilhados (heranca)
4. valores padrão do sistema (default de cada dataclass em ppcgen/config.py)
```

Implementada em `ppcgen.config.carregar_perfil` como três merges
recursivos (`_merge_dict`), aplicados nesta ordem — compartilhado, depois
base, depois o próprio perfil por cima, garantindo que o mais específico
sempre vence.

## Como a herança afeta a compilação (`ppcgen.compiladores.latex`)

`montar_arvore_latex(perfil, pasta_destino)` monta a árvore LaTeX final em
`saida/<id>/latex/` nesta ordem (cada camada pode sobrescrever a anterior):

1. `templates/latex/` — Main.tex e configuracoes/ genéricos.
2. Para cada perfil na cadeia de `extends`, **do mais base ao mais
   específico**: copia `textos/`, `figuras/` e `frontmatter/folha_rosto.tex`
   para a árvore de saída, por cima do que já estiver lá — um perfil
   derivado que só sobrescreve `textos/estrutura_curricular.tex`, por
   exemplo, herda todos os outros 11 capítulos do perfil base
   automaticamente.
3. Bibliografia: concatena os `.bib` de `heranca.referencias` com a
   bibliografia do próprio perfil (`arquivos.bibliografia`, resolvida via
   `resolver_arquivo`) em `referencias/bibliografia.bib`.
4. `overrides/latex/` e `overrides/estilos/` do perfil atual — prioridade
   máxima, aplicados por último, para casos em que um perfil realmente
   precisa de uma customização de layout que os templates genéricos não
   previram (ver `docs/CRIAR_PERFIL.md`).

## Referenciais (núcleos, áreas, competências, conteúdos, temas, legislação)

`ppcgen.cli._mesclar_referenciais` mescla o catálogo do perfil base com o
do perfil atual **por id** (não substitui a lista inteira) — se o perfil
base define um núcleo `BASICO` e o perfil atual só adiciona `OPTATIVO`, o
catálogo efetivo tem os dois. Em caso de mesmo id nos dois lados, o valor
do perfil atual vence. `heranca.legislacao` é tratado à parte:
`_acrescentar_legislacao_compartilhada` só **complementa** o catálogo do
perfil (nunca sobrescreve uma legislação com mesmo id já declarada
localmente).
