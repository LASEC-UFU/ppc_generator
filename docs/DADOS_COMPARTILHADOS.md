# Dados Compartilhados

`dados/compartilhados/` guarda informação institucional que é a mesma para
vários perfis — endereço da universidade, nome das autoridades, paleta de
cores, normas legais citadas em mais de um curso. Nada aqui é lido
automaticamente por nenhum perfil: cada perfil precisa referenciar
explicitamente o que quer usar, em `heranca:` no seu `perfil.yaml` (ver
`docs/HERANCA_DE_PERFIS.md`). Isso existe para que um perfil sozinho
continue sendo auditável sem precisar adivinhar o que veio de fora.

## Estrutura

```
dados/compartilhados/
├── instituicao/
│   ├── ufu.yaml            nome, sigla, endereço, site... da universidade
│   ├── feelt.yaml          idem, para uma unidade acadêmica específica
│   └── autoridades.yaml    reitor(a), vice, pró-reitores, diretor(a)...
├── legislacao/
│   ├── extensao.yaml
│   ├── educacao_ambiental.yaml
│   ├── direitos_humanos.yaml
│   ├── libras.yaml
│   ├── relacoes_etnico_raciais.yaml
│   └── prevencao_desastres.yaml
├── identidade_visual/
│   ├── cores.yaml           paleta RGB nomeada + mapa de logos
│   ├── logo_ufu.png         variante larga (faixa) — capa/cabeçalho
│   ├── logo_ufu_quadrado.png variante compacta — blocos de endereço
│   ├── logo_feelt.png
│   ├── header_pattern.jpg
│   └── selo_ccbynd.png
└── referencias/
    └── referencias_institucionais.bib
```

Um arquivo por norma em `legislacao/` (em vez de um único arquivo com
todas) porque cada perfil referencia só as normas que lhe dizem respeito —
um curso sem nenhuma disciplina de Libras não deveria precisar "importar"
a legislação de Libras para não referenciar as outras.

## Schema de cada arquivo

### `instituicao/*.yaml`

```yaml
instituicao:
  nome: "Universidade Federal de Uberlândia"
  sigla: "UFU"
  # qualquer outro campo (endereco, cep, municipio, estado, site,
  # telefone, unidade_academica, unidade_sigla...) é aceito e fica
  # disponível em Perfil.instituicao.extra — o código genérico não precisa
  # conhecer cada campo individualmente, os textos/*.tex acessam por nome.
```

`heranca.instituicao` e `heranca.unidade` são mesclados no mesmo bloco
`instituicao:` do perfil (o segundo por cima do primeiro) — por isso
`ufu.yaml` guarda os dados da universidade e `feelt.yaml` só os da
unidade acadêmica, sem repetir nome/sigla da UFU.

### `instituicao/autoridades.yaml`

Lista de nomes e cargos usada na folha de rosto gerada
(`ppcgen.geradores.latex.gerar_frontmatter`). Nomes reais, migrados da
fonte oficial de cada curso — nunca preenchidos com placeholder.

### `legislacao/<tema>.yaml`

```yaml
referenciais:
  - id: MEC_CNE_CP_1_2004
    descricao: "Resolução CNE/CP nº 1/2004 — Relações Étnico-Raciais..."
    fonte: "..."
```

Mesmo schema de `dados/perfis/<id>/referenciais/legislacao.yaml` — um
perfil que declara `heranca.legislacao: [compartilhados/legislacao/libras.yaml]`
recebe esses itens **complementando** (nunca sobrescrevendo) o que ele
próprio define localmente (`ppcgen.cli._acrescentar_legislacao_compartilhada`).

### `identidade_visual/cores.yaml`

```yaml
cores:
  azul_escuro: "14,64,151"
  azul_claro: "41,102,189"
  # ...
logos:
  ufu: "identidade_visual/logo_ufu.png"                    # larga, capa
  ufu_quadrado: "identidade_visual/logo_ufu_quadrado.png"   # compacta, endereços
  feelt: "identidade_visual/logo_feelt.png"
  header_pattern: "identidade_visual/header_pattern.jpg"
  selo_ccbynd: "identidade_visual/selo_ccbynd.png"
```

Quando um perfil declara `heranca.identidade_visual`,
`ppcgen.compiladores.latex.montar_arvore_latex` copia as imagens da mesma
pasta (`dados/compartilhados/identidade_visual/`) para
`saida/<perfil>/latex/figuras/compartilhadas/` — é de lá que os textos do
perfil devem referenciá-las, ex.:
`\includegraphics{figuras/compartilhadas/logo_ufu.png}`. A paleta de cores
em si (`Azul­Claro`, `AzulEscuro`, `CinzaClaro`...) já está definida em
`templates/latex/configuracoes/Estilos.tex` — `cores.yaml` documenta essa
paleta para quem for auditar/alterar os valores, mas não é lido
dinamicamente pelo compilador ainda.

### `referencias/*.bib`

Entradas BibTeX/biblatex comuns a vários cursos (leis, resoluções,
normas). `montar_arvore_latex` concatena os arquivos listados em
`heranca.referencias` com a bibliografia própria do perfil
(`arquivos.bibliografia`) em `saida/<perfil>/latex/referencias/bibliografia.bib`
— sempre cria o arquivo, mesmo vazio, para que `\addbibresource` nunca
aponte para um caminho inexistente.

## Adicionando algo novo em compartilhados

1. Confirme que o dado é **realmente** compartilhado por mais de um perfil
   (ou tem potencial concreto de ser) — legislação/dado específico de um
   único curso vai em `dados/perfis/<id>/referenciais/`, não aqui.
2. Adicione o arquivo na subpasta correspondente, seguindo o schema acima.
3. Nos perfis que devem usá-lo, adicione a referência em `heranca:` —
   nunca é automático.
4. Rode `python -m ppcgen perfil-validar --perfil <id>` — `PERFIL-007`
   aponta se um caminho declarado em `heranca` não existir.
