# Perfis de PPC

## O que é um perfil

Um **perfil** é o conjunto completo e autocontido de dados necessários para
gerar uma versão específica de um PPC: um curso, uma versão curricular
diferente do mesmo curso, ou uma proposta alternativa em avaliação. Cada
perfil vive em `dados/perfis/<id>/` e não depende de nada fora da sua
própria pasta, exceto o que ele referenciar explicitamente em `heranca:`
(dados institucionais compartilhados em `dados/compartilhados/`) ou em
`extends:` (herda de outro perfil inteiro) — ver a seção `perfil.yaml`
abaixo para os dois campos.

O sistema **nunca** assume um perfil padrão. Todo comando que opera sobre
um perfil exige `--perfil <id>` ou `--perfil-dir <caminho>` explicitamente
— a única exceção é um arquivo de conveniência de desenvolvimento local,
`.ppcgen.local.yaml` (ver seção própria abaixo), que nunca é usado em CI,
testes ou geração oficial.

## Identificador do perfil

O `id` é o nome da pasta em `dados/perfis/` e também o campo `perfil.id`
dentro do `perfil.yaml` — os dois precisam ser iguais. Formato exigido
(validado como `PERFIL-000` se violado): letras minúsculas, dígitos e `_`
apenas (`^[a-z0-9_]+$`), e não pode começar com `00` — esse prefixo é
reservado para material de referência mantido manualmente dentro de
`saida/` (ex.: `saida/00old/`, uma cópia antiga guardada à mão para
comparação), que `ppcgen limpar --todos` ignora de propósito por não
começar com o nome de um perfil real. Convenção usada pelos perfis de
exemplo deste repositório: `<curso>_<versao>`, ex.
`engenharia_computacao_2026_1`, `controle_automacao_2027_1`.

## `perfil.yaml`: as seções

```yaml
perfil:
  id: engenharia_computacao_2026_1
  nome: "Engenharia de Computação com Ênfase em Inteligência Artificial Aplicada"
  status: vigente          # rascunho | proposta | vigente | descontinuado
  versao: "2026-1"
  descricao: "..."
  extends: null             # id de um perfil base do qual herdar tudo (opcional)

curso:
  nome: ...
  nome_curto: ...
  sigla: ...
  grau: Bacharelado
  modalidade: Presencial
  turno: Vespertino
  regime_academico: Semestral
  numero_periodos: 8
  campus: ...
  municipio: ...
  estado: ...

curriculo:
  carga_horaria_total: 3450
  carga_optativa_minima: 90
  carga_extensao: 345
  carga_aac: 90
  percentual_minimo_extensao: 10      # pontos percentuais (0-100), não fração
  percentual_maximo_ead: 20

oferta:                      # formato de oferta do curso — todos os campos
                              # abaixo são opcionais, valores abaixo são o padrão
  formato: presencial         # presencial | semipresencial | distancia —
                               # decisão explícita, nunca inferida do percentual
                               # de EaD; ver percentual_maximo_ead acima
  possui_carga_ead: false
  norma_federal: ""           # ex.: "Decreto nº 12.456/2025; Portaria MEC nº 378/2025"
  norma_institucional: null   # ato da UFU (CONGRAD) que respalda a oferta parcial
                               # de EaD deste curso especificamente — null enquanto
                               # não houver ato publicado
  status_validacao_institucional: pendente   # pendente | confirmado

arquivos:                    # todos opcionais — valores abaixo são o padrão
  matriz: matriz_curricular.xlsx
  bibliografia: referencias/bibliografia.bib
  textos: textos
  fichas: fichas
  figuras: figuras
  anexos: anexos
  frontmatter: frontmatter
  overrides: overrides

geracao:
  anexar_fichas: true
  anexar_resolucoes: true
  compilar_pdf: true
  interromper_em_erro: true  # false só com justificativa documentada em
                              # comentário no próprio perfil.yaml

saida:
  nome_base: PPC

heranca:                     # referencia dados/compartilhados/ (opcional)
  instituicao: compartilhados/instituicao/ufu.yaml
  unidade: compartilhados/instituicao/feelt.yaml
  identidade_visual: compartilhados/identidade_visual/cores.yaml
  autoridades: compartilhados/instituicao/autoridades.yaml
  referencias: [compartilhados/referencias/referencias_institucionais.bib]

# Catálogo de referenciais legais deste perfil (substitui o antigo
# referenciais/legislacao.yaml e o antigo heranca.legislacao — cada
# perfil declara sua própria lista completa, sem arquivo externo).
legislacao:
  - id: MEC_CNE_CES_7_2018
    nome: Diretrizes para a extensão na Educação Superior
    tipo: resolucao
    documento: Resolução CNE/CES nº 7, de 18 de dezembro de 2018
    ano: 2018
    observacoes: ...
```

Campos desconhecidos em qualquer seção fazem o carregamento falhar com
`ConfiguracaoInvalida` (erro de digitação nunca é ignorado silenciosamente).
Não existe mais pasta `referenciais/` em nenhum perfil — núcleos, áreas,
temas transversais, conteúdos curriculares e competências são abas de
registro da própria `matriz_curricular.xlsx`
(`Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`, ver
`docs/DICIONARIO_DADOS.md`); só legislação é a lista acima, direto em
`perfil.yaml`.

## Status

`status` é só metadado descritivo — o código não impõe regras diferentes
por status, exceto nos comandos em lote (`*-todos`), que por padrão
**pulam perfis com `status: descontinuado`** e podem ser filtrados com
`--status <valor>`.

## Comandos da CLI

```
python -m ppcgen perfis                              # lista todos os perfis descobertos
python -m ppcgen perfil-info --perfil <id>            # mostra os dados carregados de um perfil
python -m ppcgen perfil-validar --perfil <id>         # valida só a estrutura (PERFIL-0xx)
python -m ppcgen perfil-criar --id <id> --nome "..."  # cria a estrutura mínima de um perfil novo
python -m ppcgen perfil-clonar --origem <id> --destino <novo-id> [--versao <v>]

python -m ppcgen validar --perfil <id>                # valida currículo + fichas
python -m ppcgen gerar --perfil <id>                  # gera os .tex em saida/<id>/latex/gerado/
python -m ppcgen compilar --perfil <id>                # compila saida/<id>/latex/Main.tex em PDF
python -m ppcgen completo --perfil <id>                # valida + gera + compila + anexa fichas/resoluções

python -m ppcgen validar-todos [--status <s>]
python -m ppcgen gerar-todos [--status <s>]
python -m ppcgen completo-todos [--status <s>]

python -m ppcgen limpar --perfil <id>                  # remove saida/<id>/ (nunca dados/)
python -m ppcgen limpar --todos
```

Equivalentes via `make` (exige `PROFILE=<id>` nos alvos de um único
perfil — ver `docs/CRIAR_PERFIL.md` e o próprio `Makefile`).

## Descoberta de perfis

Por padrão, todo diretório em `dados/perfis/` que contenha um
`perfil.yaml` válido é descoberto automaticamente (`ppcgen/perfis.py`) —
não é preciso registrar um perfil em nenhum lugar central para que ele
apareça em `python -m ppcgen perfis` ou seja incluído nos comandos em
lote.

Um `dados/perfis.yaml` opcional pode sobrepor a descoberta automática
(por exemplo, para listar perfis fora de `dados/perfis/` ou fixar uma
ordem de exibição), mas não é necessário no uso comum.

## `.ppcgen.local.yaml` (conveniência de desenvolvimento — não oficial)

Se você trabalha o tempo todo no mesmo perfil, pode criar na raiz do
repositório (fora do controle de versão — adicione ao seu `.gitignore`
local se necessário) um arquivo:

```yaml
perfil_padrao: engenharia_computacao_2026_1
```

Quando presente, a CLI o usa como último recurso **apenas se nem
`--perfil` nem `--perfil-dir` forem passados**, emitindo um aviso claro de
que a seleção implícita está sendo usada. Este arquivo:

- nunca é lido em testes automatizados (`testes/`);
- nunca deve ser usado em CI ou em geração oficial de um PPC;
- não tem nenhum efeito sobre os comandos em lote (`*-todos`).

Existe só para poupar digitação durante o desenvolvimento local — a regra
geral do sistema continua sendo seleção sempre explícita de perfil.
