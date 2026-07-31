# Criar um Novo Perfil

Este guia cria um perfil do zero (curso novo, sem dados legados para
migrar). Para trazer um curso que já existe em outro sistema/formato, veja
`docs/MIGRAR_PERFIL.md`.

## 1. Escolher o id

Minúsculas, dígitos e `_` apenas (`^[a-z0-9_]+$`). Convenção sugerida:
`<curso>_<versao>`, ex. `engenharia_software_2027_1`.

## 2. Gerar o esqueleto

```
python -m ppcgen perfil-criar --id engenharia_software_2027_1 --nome "Engenharia de Software"
```

Isso cria `dados/perfis/engenharia_software_2027_1/` com toda a árvore
padrão de um perfil já no lugar: `perfil.yaml` mínimo (já com `legislacao:
[]`), `matriz_curricular.xlsx` só com cabeçalhos (incluindo as abas de
registro `Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`, todas
vazias), os 12 `textos/*.tex` com um `\chapter{}` placeholder cada,
`frontmatter/*.yaml` vazios, `referencias/bibliografia.bib` vazio, e as
subpastas de `fichas/`/`anexos/`/`overrides/`. O perfil já é
estruturalmente válido neste ponto (`perfil-validar` passa), só sem
conteúdo real.

## 3. Preencher `perfil.yaml`

Ver `docs/PERFIS.md` para o significado de cada campo. No mínimo, decida:

- `curso.numero_periodos` e as cargas horárias esperadas em `curriculo:`
  (você vai conferir depois que a matriz bate com esses números — é assim
  que `CARGA_TOTAL_DIVERGENTE` funciona).
- Se este curso pertence à mesma instituição de um perfil existente,
  preencha `heranca:` apontando para `dados/compartilhados/` em vez de
  copiar os dados institucionais. Se a instituição ainda não existe em
  `compartilhados/`, crie-a lá primeiro — não duplique dentro do perfil.
- Preencha `legislacao:` (lista de referenciais legais deste curso) — não
  há mais arquivo externo para isso, é tudo aqui (ver
  `docs/DICIONARIO_DADOS.md` para os campos de cada entrada). Competências
  não ficam em `perfil.yaml` — são a aba `Competencias` da matriz (próximo
  passo), pode ficar vazia se o curso não rastreia competências
  individualmente.

## 4. Preencher a matriz curricular

Edite `matriz_curricular.xlsx`. Aba obrigatória: `Componentes`. Opcionais:
`Equivalencias`, `Nucleos`, `Areas`, `Temas`, `Conteudos`, `Competencias`,
`Certificacoes` — schema completo em `docs/DICIONARIO_DADOS.md`. Pontos
que costumam pegar quem preenche pela primeira vez:

- **Núcleo, áreas, temas, conteúdos e competências de um componente NÃO
  são colunas de `Componentes`** — são a coluna `componentes` (códigos
  separados por `|`) de cada linha das abas `Nucleos`/`Areas`/`Temas`/
  `Conteudos`/`Competencias`. A direção é catálogo → componente: você
  edita o item de catálogo e lista nele os componentes que o cobrem, não
  o contrário.
- **Pré-requisitos e correquisitos de um componente são colunas da
  própria aba `Componentes`** (listas separadas por vírgula — ex.:
  `CTR401, CTR203 (opcional), >=1200h` na coluna `pre_requisitos`).
- **Optativa não é uma aba** — é um componente com `tipo=carga_optativa`
  na aba `Componentes`.
- **`tipo`, não `obrigatorio`, decide o que conta no total oficial do
  curso.** Um componente de extensão com `obrigatorio=FALSE` ainda soma
  no total se `tipo=extensao` (ver `ppcgen/calculo.py`) — `obrigatorio`
  serve só para a tabela "Componentes Curriculares Obrigatórios".
- Deixe `ativo` **explícito** (`TRUE`/`FALSE`) em vez de em branco — célula
  vazia gera um aviso (`LEITURA_DADO_OMITIDO`) mesmo assumindo `TRUE`.
- Todo código listado em `componentes` de `Nucleos`/`Areas`/`Temas`/
  `Conteudos`/`Competencias` precisa existir na aba `Componentes`, ou o
  validador acusa `*_COMPONENTE_INEXISTENTE`; um mesmo componente em mais
  de uma linha de `Nucleos` acusa `NUCLEO_MULTIPLO_PARA_COMPONENTE`.

## 6. Escrever os 12 capítulos em `textos/`

Prosa institucional/pedagógica em LaTeX. Nenhum deles é gerado
automaticamente — são texto humano. `estrutura_curricular.tex` é o único
capítulo que **combina** prosa própria com `\input{gerado/*}` (as tabelas
que `ppcgen gerar` produz a partir da matriz — ver a lista completa de
nomes de arquivo gerados em `docs/DICIONARIO_DADOS.md` ou inspecionando
`ppcgen/geradores/latex.py`). Use o perfil `controle_automacao_2027_1`
como referência de quais `\input{gerado/tab_*}`/`\IfFileExists{...}` usar.

Capítulos obrigatórios (validados por `PERFIL-003`): `identificacao`,
`apresentacao`, `justificativa`, `principios`, `perfil_egresso`,
`objetivos`, `estrutura_curricular`, `diretrizes_pedagogicas`,
`avaliacao`, `atendimento_estudante`, `acompanhamento_egresso`,
`consideracoes_finais`.

Macros disponíveis sem precisar `\input` nada: `\ppccurso`,
`\ppccursocurto`, `\ppcinstituicao`, `\ppcunidadeacademica` — definidas a
partir de `perfil.yaml`/`heranca.instituicao` em
`ppcgen.geradores.latex` (arquivo `curso_macros.tex`, gerado
automaticamente).

## 7. Frontmatter

`frontmatter/capa.yaml` (título, `logo_curso: figuras/<seu-logo>.png`),
`frontmatter/autoridades.yaml` e `frontmatter/comissao.yaml` (nomes reais
de quem coordena o curso e integra a comissão de elaboração — nunca
placeholder). `frontmatter/folha_rosto.tex` é opcional: só crie se o
layout padrão gerado por `ppcgen.geradores.latex.gerar_frontmatter` não
for suficiente.

## 8. Fichas curriculares

Coloque os PDFs/DOCX das fichas de cada componente na subpasta
correspondente ao `tipo` do componente:
`fichas/{obrigatorias,optativas,extensao,tcc,estagio,complementares}/`.
`ppcgen.leitores.fichas` extrai código/nome do conteúdo do arquivo e casa
com `matriz_curricular.xlsx` por código (fallback por nome) — fichas que
não forem reconhecidas ficam sinalizadas, nunca silenciosamente ignoradas.

## 9. Validar, gerar, compilar

```
python -m ppcgen perfil-validar --perfil engenharia_software_2027_1   # só estrutura
python -m ppcgen validar        --perfil engenharia_software_2027_1   # currículo + fichas
python -m ppcgen gerar          --perfil engenharia_software_2027_1
python -m ppcgen compilar       --perfil engenharia_software_2027_1
python -m ppcgen completo       --perfil engenharia_software_2027_1   # os quatro passos acima
```

Ou, com `make` (exige `PROFILE=`):

```
make perfil-validar PROFILE=engenharia_software_2027_1
make validate       PROFILE=engenharia_software_2027_1
make complete        PROFILE=engenharia_software_2027_1
```

Erros (`ERRO`) interrompem a geração por padrão
(`geracao.interromper_em_erro: true`); alertas (`ALERTA`) não impedem a
geração, mas ficam registrados em
`saida/<id>/relatorios/validacao.{html,json}` — nunca corrija um alerta
"escondendo" o dado, sempre corrigindo a fonte (matriz/`perfil.yaml`) ou
documentando por que ele é esperado.

## 10. Customizações de layout (raramente necessário)

Se o layout genérico realmente não atender (ex.: uma tabela extra
específica deste curso), use `overrides/latex/` e `overrides/estilos/` —
arquivos ali sobrescrevem os equivalentes em `templates/latex/` só para
este perfil, aplicados por último na montagem da árvore. Evite: a
maioria das necessidades reais é resolvida com conteúdo em `textos/`,
não com um override de template.
