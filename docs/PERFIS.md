# Perfis de PPC

## O que é um perfil

Um **perfil** é o conjunto completo e autocontido de dados necessários para
gerar uma versão específica de um PPC: um curso, uma versão curricular
diferente do mesmo curso, ou uma proposta alternativa em avaliação. Cada
perfil vive na sua própria pasta (normalmente `dados/perfis/<id>/`, mas o
caminho pode ser qualquer um — ver "Descoberta de perfis" abaixo) e não
depende de nada fora dela, exceto o que ele referenciar explicitamente em
`extends:` (herda de outro perfil inteiro) — ver a seção "Aba `Perfil`"
abaixo. Não existe `perfil.yaml`: toda a configuração do perfil vive na
aba `Perfil` da própria `matriz_curricular.xlsx`/`.xlsm`, junto com os
dados curriculares. Não existe mecanismo de dados compartilhados entre
perfis: cada um carrega seus próprios dados institucionais, autoridades,
imagens e bibliografia.

O sistema **nunca** assume um perfil padrão. Todo comando que opera sobre
um perfil exige `--perfil <id>` ou `--perfil-dir <caminho>` explicitamente
— a única exceção é um arquivo de conveniência de desenvolvimento local,
`.ppcgen.local.yaml` (ver seção própria abaixo), que nunca é usado em CI,
testes ou geração oficial.

## Identificador do perfil

Por padrão, o `id` é o nome da pasta em `dados/perfis/` e também o campo
`perfil.id` dentro da aba `Perfil` da matriz — os dois precisam ser iguais
(a menos que o perfil esteja registrado explicitamente em
`dados/perfis.yaml`, ver
"Descoberta de perfis" abaixo, caso em que o `id` só precisa bater com o
que está no registro). Formato exigido
(validado como `PERFIL-000` se violado): letras minúsculas, dígitos e `_`
apenas (`^[a-z0-9_]+$`), e não pode começar com `00` — esse prefixo é
reservado para material de referência mantido manualmente dentro de
`saida/` (ex.: `saida/00old/`, uma cópia antiga guardada à mão para
comparação), que `ppcgen limpar --todos` ignora de propósito por não
começar com o nome de um perfil real. Convenção usada pelo perfil deste
repositório: `<curso>_<versao>`, ex. `tecnologo_automacao_2027_1`.

## Aba `Perfil`: as chaves

Chave/valor, uma linha por campo (`chave` no formato `secao.campo`,
`valor` o conteúdo) — schema completo em `docs/DICIONARIO_DADOS.md`.
Equivalente ao antigo `perfil.yaml`, mesma organização em seções:

```
chave                                       valor
perfil.id                                   engenharia_computacao_2026_1
perfil.nome                                 Engenharia de Computação com Ênfase em IA Aplicada
perfil.status                               vigente            # rascunho | proposta | vigente | descontinuado
perfil.versao                               2026-1
perfil.descricao                            ...
perfil.extends                              (vazio)            # id de um perfil base do qual herdar tudo (opcional)

curso.nome                                  ...                 # denominação regulatória (CNCST/MEC)
curso.nome_curto                            ...
curso.nome_mercadologico                    ...                 # nome de divulgação institucional (opcional)
curso.enfase_curricular                     ...                 # linha formativa/ênfase (opcional)
curso.titulacao_conferida                   ...                 # diploma/título conferido
curso.tempo_minimo_integralizacao           ...                 # texto institucional, ex.: "6 semestres (3 anos)"
curso.tempo_maximo_integralizacao           ...                 # texto institucional; deixe vazio se pendente
curso.vagas_ofertadas                       ...                 # texto institucional; deixe vazio se pendente
curso.eixo_tecnologico                      ...                 # classificação regulatória, se aplicável
curso.area_tecnologica                      ...                 # classificação regulatória, se aplicável
curso.codigo_cine                           ...                 # código CINE Brasil, se aplicável
curso.sigla                                 ...
curso.grau                                  Bacharelado
curso.modalidade                            Presencial
curso.turno                                 Vespertino
curso.regime_academico                      Semestral
curso.numero_periodos                       8
curso.campus                                ...
curso.municipio                             ...
curso.estado                                ...

curriculo.carga_horaria_total               3450
curriculo.carga_optativa_minima             90
curriculo.carga_extensao                    345
curriculo.carga_aac                         90
curriculo.percentual_minimo_extensao        10                 # pontos percentuais (0-100), não fração
curriculo.percentual_maximo_ead             20

oferta.formato                              presencial         # presencial | semipresencial | distancia —
                                                                # decisão explícita, nunca inferida do percentual
                                                                # de EaD; ver percentual_maximo_ead acima
oferta.possui_carga_ead                     FALSE
oferta.norma_federal                        (ex.: "Decreto nº 12.456/2025; Portaria MEC nº 378/2025")
oferta.norma_institucional                  (vazio)            # ato da UFU (CONGRAD) que respalda a oferta parcial
                                                                # de EaD deste curso especificamente — vazio enquanto
                                                                # não houver ato publicado
oferta.status_validacao_institucional       pendente           # pendente | confirmado

arquivos.textos                             textos             # todas opcionais — valores acima são o padrão
arquivos.fichas                             fichas
arquivos.figuras                            figuras
arquivos.anexos                             anexos
arquivos.frontmatter                        frontmatter
arquivos.overrides                          overrides
arquivos.capitulos                          identificacao|apresentacao|...  # lista/ordem dos capítulos do PDF,
                                                                # itens separados por `|`, sem `.tex` — vazio cai
                                                                # nos 12 padrão (CAPITULOS_PADRAO)

geracao.anexar_fichas                       TRUE
geracao.anexar_resolucoes                   TRUE
geracao.compilar_pdf                        TRUE
geracao.interromper_em_erro                 TRUE               # FALSE só com justificativa documentada em
                                                                # observação na própria planilha

saida.nome_base                             PPC
```

(Não existe linha `arquivos.matriz` — o nome do arquivo é sempre o que
acabou de ser aberto pra ler esta própria aba, nunca configurável de
dentro dela; ver "Descoberta de perfis" abaixo sobre `matriz:` no
registro.) Campos desconhecidos em qualquer seção fazem o carregamento
falhar com `ConfiguracaoInvalida` (erro de digitação nunca é ignorado
silenciosamente). Não existe mais pasta `referenciais/` em nenhum perfil —
núcleos, áreas, temas transversais, conteúdos curriculares, competências e
legislação são abas de registro da própria `matriz_curricular.xlsx`
(`Nucleos`/`Areas`/`Temas`/`Conteudos`/`Competencias`/`Legislacao`, ver
`docs/DICIONARIO_DADOS.md`) — nenhuma dessas listas vive na aba `Perfil`.

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
`matriz_curricular.xlsm` ou `.xlsx` (nessa ordem) com uma aba `Perfil`
declarando `perfil.id` é descoberto automaticamente (`ppcgen/perfis.py`)
— não é preciso registrar um perfil em nenhum lugar central para que ele
apareça em `python -m ppcgen perfis` ou seja incluído nos comandos em
lote.

Um `dados/perfis.yaml` opcional pode sobrepor a descoberta automática, para
listar perfis fora de `dados/perfis/`, fixar uma ordem de exibição, ou
declarar explicitamente o nome do arquivo de matriz quando ele não é
`matriz_curricular.xlsx`/`.xlsm` — não é necessário no uso comum. Exemplo
real deste repositório: cada perfil vive direto em `dados/<id>/` (sem a
pasta intermediária `dados/perfis/`), então `dados/perfis.yaml` registra
cada um explicitamente:

```yaml
perfis:
  - id: tecnologo_automacao_2027_1
    caminho: "tecnologo_automacao_2027_1"
    matriz: "matriz_curricular.xlsm"
    ativo: true
```

(`caminho` é relativo a `dados/`; `matriz` é opcional, padrão
`matriz_curricular.xlsx`.) Isso preserva `--perfil
tecnologo_automacao_2027_1` funcionando normalmente em todos os comandos —
um segundo projeto independente entraria como
`dados/engenharia_automacao_2027_1/` mais uma entrada nova aqui.

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
