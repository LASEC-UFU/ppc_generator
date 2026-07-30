# Perfis de PPC

## O que é um perfil

Um **perfil** é o conjunto completo e autocontido de dados necessários para
gerar uma versão específica de um PPC: um curso, uma versão curricular
diferente do mesmo curso, ou uma proposta alternativa em avaliação. Cada
perfil vive em `dados/perfis/<id>/` e não depende de nada fora da sua
própria pasta, exceto o que ele referenciar explicitamente em `heranca:`
(ver `docs/DADOS_COMPARTILHADOS.md`) ou em `extends:` (ver
`docs/HERANCA_DE_PERFIS.md`).

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
  extends: null             # id de um perfil base (opcional — ver HERANCA_DE_PERFIS.md)

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

arquivos:                    # todos opcionais — valores abaixo são o padrão
  matriz: matriz_curricular.xlsx
  equivalencias: equivalencias.xlsx
  bibliografia: referencias/bibliografia.bib
  textos: textos
  referenciais: referenciais
  fichas: fichas
  figuras: figuras
  anexos: anexos
  frontmatter: frontmatter
  overrides: overrides

geracao:
  anexar_fichas: true
  anexar_resolucoes: true
  compilar_pdf: true
  interromper_em_erro: true  # false só com justificativa documentada — ver
                              # docs/MIGRACAO.md para o caso de uso real

saida:
  nome_base: PPC

heranca:                     # ver docs/DADOS_COMPARTILHADOS.md
  instituicao: compartilhados/instituicao/ufu.yaml
  unidade: compartilhados/instituicao/feelt.yaml
  identidade_visual: compartilhados/identidade_visual/cores.yaml
  autoridades: compartilhados/instituicao/autoridades.yaml
  referencias: [compartilhados/referencias/referencias_institucionais.bib]
  legislacao: [compartilhados/legislacao/extensao.yaml, ...]
```

Campos desconhecidos em qualquer seção fazem o carregamento falhar com
`ConfiguracaoInvalida` (erro de digitação nunca é ignorado silenciosamente).

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
