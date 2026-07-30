# Relatório de Auditoria Normativa

Auditoria do embasamento legal, institucional e bibliográfico do perfil
`tecnologo_automacao_2027_1` (Curso Superior de Tecnologia em Automação
Industrial, UFU) e da infraestrutura genérica do `ppcgen` que o gera.

**Escopo**: `dados/perfis/tecnologo_automacao_2027_1/`, `dados/compartilhados/`
(usado por qualquer perfil via `heranca`) e o código genérico em `ppcgen/`
que valida essas informações. Não inclui os perfis arquivados em
`dados/perfis/00Old/` (material de referência histórico, fora de uso).

**Data da auditoria**: 2026-07-30.

**Limitação de acesso**: o servidor `reitoria.ufu.br` (fonte primária das
resoluções dos conselhos superiores da UFU) recusou conexão a partir deste
ambiente em todas as tentativas. Os documentos da UFU citados abaixo como
"confirmados" foram obtidos por mirrors institucionais (`facom.ufu.br`,
`prograd.ufu.br`, `proae.ufu.br` etc.) ou por resultados de busca; quando não
foi possível localizar o texto integral, isso está declarado explicitamente
no campo "Nível de confiança".

## Como ler este relatório

Cada norma recebe uma classificação:

- **MANTER** — vigente, corretamente aplicada, nenhuma ação necessária.
- **ATUALIZAR** — vigente mas com dado incorreto no projeto (número, data,
  ementa, URL) — corrigido nesta rodada.
- **SUBSTITUIR** — havia norma mais nova cobrindo a mesma matéria — trocada
  nesta rodada.
- **RETIRAR** — não deveria estar no projeto (nunca foi citada, ou é
  claramente inaplicável ao CST) — já ausente, ou removida nesta rodada.
- **MANTER APENAS COMO HISTÓRICA** — revogada/substituída, mas mantida no
  `.bib` com nota, porque ainda é citada em contexto histórico.
- **EXIGE ANÁLISE ACADÊMICA** — depende de decisão do NDE/Colegiado/Unidade
  Acadêmica (conteúdo pedagógico, não normativo).
- **EXIGE CONFIRMAÇÃO DA UFU** — depende de ato que a UFU ainda não publicou,
  ou que não foi possível localizar/verificar nesta auditoria.

"Ação nesta rodada" indica o que **já foi implementado** ao longo desta
conversa (nesta e na anterior). Itens sem essa marca são diagnóstico apenas —
ainda não implementados.

---

## 0. Padronização de chaves `.bib` — implementada

As ~35 chaves de citação dos dois arquivos `.bib` (compartilhado e do
perfil) foram renomeadas para `snake_case` semântico (ex.:
`MEC:CNE:CES:7:2018` → `cne_ces_7_2018`; `UFU:CONGRAD:177:2026` →
`ufu_congrad_177_2026`), com todos os `\cite{}` correspondentes atualizados
em todos os capítulos de `textos/`. De quebra, a duplicata de conteúdo
`Lei:13005:2014` (perfil) / `mec2014pne` (compartilhado) — o mesmo PNE
2014, com duas chaves e dois textos ligeiramente diferentes — foi
unificada em `mec_pne_2014`, único. Confirmado sem citação órfã e sem
chave duplicada entre os dois arquivos (`40` chaves ao todo).

## 1. Extensão (auditoria completa — implementada)

| Referência | Situação | Ação nesta rodada | Fonte |
|---|---|---|---|
| Resolução CONGRAD nº 177, de 20/02/2026 | **Vigente.** Regulamenta ACEs na UFU: mínimo 10% da carga total (piso absoluto de 160h para Tecnologia quando não fixado em lei superior); ACEs em ≥3 componentes, em períodos distintos; **execução obrigatoriamente presencial** — a exceção de mediação digital (art. 5º §7º II) vale só para bacharelados; estágio obrigatório/monitoria/tutoria não contam como ACE. | **SUBSTITUIR.** Texto integral obtido (PDF lido diretamente). `.bib`, `legislacao.yaml` (compartilhado) e a seção "Atividades Curriculares de Extensão / ACE" de `estrutura_curricular.tex` foram reescritos com os artigos reais, não mais placeholders "a confirmar". | facom.ufu.br (mirror do documento SEI 7072406, Processo 23117.058216/2025-19) — **alta confiança**, texto lido na íntegra |
| Resolução CONGRAD nº 13/2019 (arts. 1º-11º) | **Revogada** pela Res. 177/2026, art. 15, I. | **MANTER APENAS COMO HISTÓRICA.** Removida do `\cite` operativo da seção de extensão; entrada `.bib` marcada como histórica com a nota de revogação. | mesmo documento, art. 15, I — alta confiança |
| Resolução CONGRAD nº 15/2016 | Vigente, alterada pela Res. 177/2026 (art. 14: novo art. 21-A tornando as ACEs obrigatórias em todos os cursos). | **MANTER**, sem alteração necessária no projeto. | mesmo documento, art. 14 |
| Resolução CNE/CES nº 7/2018 (Diretrizes para a Extensão) | Vigente, federal. | **MANTER.** Já citada corretamente. | já verificada na rodada anterior |
| Lei nº 13.005/2014 (PNE 2014-2024), Meta 12.7 | **Substituída** pela Lei nº 15.388/2026. | **SUBSTITUIR** (parcial). Adicionada `mec2026pne` ao `.bib` compartilhado; a citação na seção de extensão agora referencia o PNE atual, mantendo 13.005/2014 como nota histórica da origem da meta de 10%. | planalto.gov.br, gov.br/mec — confirmado sancionado 14/04/2026 |
| Percentual de extensão do perfil (`curriculo.percentual_minimo_extensao: 10`, `carga_extensao: 240h`) | 240h = exatamente 10% de 2.400h, e acima do piso de 160h para Tecnologia da Res. 177/2026 art. 4º §3º III. | **MANTER** — os valores já configurados no perfil (definidos na atualização anterior) atendem à norma agora verificada. Nenhuma mudança de número necessária. | Res. CONGRAD 177/2026, art. 4º |

**Nota**: a discrepância de 120h entre a soma das parcelas informadas
originalmente pelo usuário (1.800+120+60+60+240=2.280h) e o total declarado
(2.400h), já sinalizada na atualização anterior, **continua não resolvida**
— nenhuma norma encontrada nesta auditoria explica essa diferença. Ver nota em
`perfil.yaml` e em `identificacao.tex`. **EXIGE ANÁLISE ACADÊMICA.**

---

## 2. Educação a distância em curso presencial

| Referência | Situação | Ação proposta | Fonte |
|---|---|---|---|
| Decreto nº 12.456, de 19/05/2025 | **Vigente.** Fixa parâmetros por formato: presencial = mín. 70% presencial (≤30% EaD); semipresencial = mín. 30% presencial + mín. 20% presencial/síncrona mediada; a distância = mín. 10% presencial. IES têm até 19/05/2027 para adequação. | Já no `.bib` do projeto (herdado de quando a Engenharia de Computação foi migrada). **`curriculo.percentual_maximo_ead: 30` do perfil está exatamente no teto legal para formato presencial — confirmado correto**, não é uma folga arbitrária. | conjur.com.br, semesp.org.br, planalto — alta confiança |
| Portaria MEC nº 378, de 19/05/2025 | **Vigente.** Detalha formatos de oferta por área do CINE Brasil; áreas não mencionadas seguem só o Decreto 12.456/2025. | **ADICIONADO** ao `.bib` compartilhado (`mec_portaria_378_2025`) e citado em `identificacao.tex`, substituindo a menção à Portaria 2.117/2019. **Ainda não verifiquei** se ela cita regra específica para a área "Eletrônica e Automação"/eixo "Controle e Processos Industriais" — nota de pendência deixada no próprio `.bib`. **EXIGE ANÁLISE ACADÊMICA/CONFIRMAÇÃO** antes de descartar regra específica. | gov.br/mec, semesp — média confiança (resumo, não texto integral) |
| Portarias MEC nº 381/2025, 795/2025, 506/2025, 794/2025 (citadas no pedido do usuário) | **Não verificadas nesta auditoria** — não pesquisei o conteúdo de nenhuma das quatro. | **EXIGE CONFIRMAÇÃO DA UFU/pesquisa adicional** antes de citá-las no PPC. Não presumir que existem com o conteúdo implícito no pedido. | não consultada |
| Portaria MEC nº 2.117/2019 (limite antigo de 40% EaD) | **Superada** pelo arcabouço Decreto 12.456/2025 + Portaria 378/2025 (ela mesma já havia revogado a Portaria 1.428/2018). | **RETIRAR** — não está e não deve ser citada no projeto como regra vigente. Já não constava do projeto. | conjur.com.br, gov.br/mec — alta confiança |
| **Resolução CONGRAD (UFU) sobre oferta de componentes EaD em cursos presenciais** (altera a Resolução CONGRAD nº 35/2011; Processo SEI 23117.070903/2023-41) | **Ainda em tramitação.** Pautada na 2ª reunião/2026 (13/03, retirada por diligência a pedido de conselheiro), reincluída na 6ª reunião/2026 (10/07) e na 7ª reunião/2026 (24/07). **Não localizei uma resolução final publicada** com esse conteúdo até a data desta auditoria. | **EXIGE CONFIRMAÇÃO DA UFU — registrado como pendência, não inventado.** Enquanto não houver resolução publicada, o formato de oferta deste curso só pode se apoiar na norma federal (Decreto 12.456/2025 + Portaria 378/2025), não em regra institucional própria da UFU para esse tema específico. | ufu.br/acontece (pautas das reuniões do CONGRAD) — média confiança (pautas encontradas, resolução final não) |

### Bloco `oferta:` pedido pelo usuário (Seção 6 do pedido) — implementado

Implementado como mudança de arquitetura genérica do `ppcgen` (afeta
qualquer perfil, não só este):

- `OfertaConfig` (novo dataclass em `ppcgen/config.py`), campo `oferta:`
  em `Perfil`, documentado em `docs/PERFIS.md`.
- `ppcgen.validadores.ead.validar_formato_oferta`: valida `oferta.formato`
  contra os tetos legais do Decreto nº 12.456/2025 (`TETO_EAD_POR_FORMATO`
  = presencial 30% / semipresencial 70% / distância 90%) e alerta quando
  há carga EaD declarada sem norma institucional confirmada — códigos
  `OFERTA_FORMATO_DESCONHECIDO`, `EAD_ACIMA_DO_TETO_LEGAL_FORMATO`,
  `OFERTA_SEM_NORMA_INSTITUCIONAL_CONFIRMADA`, documentados em
  `docs/VALIDACOES.md`. 7 testes novos em
  `testes/unitarios/test_validador_extensao_ead.py` (93/93 passam).
- `perfil.yaml` deste curso configurado com:

```yaml
oferta:
  formato: presencial
  possui_carga_ead: true
  norma_federal: "Decreto nº 12.456/2025; Portaria MEC nº 378/2025"
  norma_institucional: null   # PENDENTE — Res. CONGRAD ainda não publicada
  status_validacao_institucional: pendente
```

`python -m ppcgen validar --perfil tecnologo_automacao_2027_1` já mostra o
`[ALERTA]` correspondente à pendência institucional.

**Deliberadamente fora desta rodada**: os pisos de atividade *síncrona
mediada* que o Decreto 12.456/2025 também define (distintos do teto
presencial/EaD agregado) não são verificados — exigiriam campos novos de
carga síncrona/assíncrona por componente na matriz (Seção 7 do pedido do
usuário), que é uma mudança maior, ainda não feita (ver Seção "Plano de
implementação").

---

## 3. CNCST / CINE Brasil

| Referência | Situação | Ação | Fonte |
|---|---|---|---|
| Portaria MEC nº 514, de 04/06/2024 (CNCST 4ª edição) | Vigente. | **MANTER** — já incorporada na atualização anterior (`.bib`, `legislacao.yaml`, `identificacao.tex`). | abmes.org.br, sead.ufba.br — alta confiança |
| Resolução CNE/CP nº 2, de 04/04/2024 (eixos/áreas tecnológicas do CNCST/CNCT) | Vigente. | **MANTER** — já incorporada. | semesp.org.br, mec.gov.br — alta confiança |
| CINE Brasil, código 0714A01 = "Automação Industrial", eixo 0714 "Eletrônica e Automação" | Confirmado. | **MANTER** — já registrado em `referenciais/cncst_automacao_industrial.yaml`. | download.inep.gov.br (tabela de correspondência oficial) — alta confiança |
| Portaria Inep nº 622, de 08/09/2025 ("nova adaptação da CINE Brasil") | **Vigente** — é a política atual do CINE Brasil. | **ADICIONADO** ao `.bib` e a `referenciais/legislacao.yaml` do perfil (`inep_cine_brasil_622_2025`) como base normativa do enquadramento CINE Brasil deste curso. | abmes.org.br, npi.pr1.ufrj.br — alta confiança |
| Portaria MEC nº 1.715/2019 e "Portaria Inep nº 299/2023" (citadas no pedido do usuário) | 1.715/2019 não verificada. **299/2023 não localizada** nesta busca — pode ter número/ano incorretos. | **RETIRAR/NÃO USAR** "Portaria Inep nº 299/2023" até confirmação — não presumir que existe com esse número. | busca sem resultado direto para 299/2023 |
| Ficha catalográfica completa fornecida pelo usuário (CBO, infraestrutura mínima, ingresso, estágio) em `referenciais/cncst_automacao_industrial.yaml` | Dado fornecido pelo próprio usuário na conversa anterior, **não auditado independentemente** contra o catálogo oficial (`cncst.mec.gov.br`) nesta rodada. | **EXIGE CONFIRMAÇÃO** — recomendo checar a ficha completa direto em cncst.mec.gov.br antes de submissão oficial. | não verificado nesta auditoria |

---

## 4. Regulamentação profissional (Tecnólogo)

| Referência | Situação | Ação | Fonte |
|---|---|---|---|
| Resolução CONFEA nº 1.073/2016 | Vigente. | **MANTER** — já incorporada. | já verificada na rodada anterior |
| Resolução CONFEA nº 313, de 26/09/1986 | **Vigente e mais específica** que a 1073/2016 para o exercício profissional dos Tecnólogos (regulamenta com base na Lei 5.194/1966). | **ADICIONADO** ao `.bib` e a `referenciais/legislacao.yaml` do perfil (`confea_313_1986`). | tecconcursos.com.br, ufrgs.br, confea.org.br — alta confiança |
| Lei nº 5.194/1966 | Vigente — lei-base do sistema Confea/Crea, já presente em `dados/perfis/.../referencias/bibliografia.bib` mas herdada do perfil de Engenharia (contexto de "Engenheiro, Arquiteto e Engenheiro-Agrônomo"). | **MANTER** como base do sistema profissional, mas **não** como fundamento direto das atribuições do tecnólogo — essa função cabe à CONFEA 313/1986. | — |

---

## 5. Normas institucionais da UFU (organização acadêmica)

| Referência | Situação | Ação | Fonte |
|---|---|---|---|
| Resolução CONGRAD nº 46, de 28/03/2022 (Normas Gerais da Graduação da UFU), alterada pela Res. CONGRAD nº 78/2022 | **Vigente.** Revogou parcialmente a Res. CONGRAD nº 15/2011. | **ADICIONADO** — novo arquivo compartilhado `dados/compartilhados/legislacao/organizacao_academica.yaml`, referenciado no `heranca.legislacao` deste perfil, mais entrada `.bib` (`ufu_congrad_46_2022`). | prograd.ufu.br, proae.ufu.br — alta confiança |
| Resolução CONGRAD nº 15/2011 | **Parcialmente revogada** pela 46/2022. Já não é usada no projeto (correto). | **RETIRAR/NÃO USAR** — confirmado, já ausente. | prograd.ufu.br |
| Resolução CONGRAD nº 24/2012 (estágio, citada no pedido do usuário como desatualizada) | Já ausente do projeto — o projeto usa corretamente a Res. CONGRAD nº 93/2023 para estágio. | **MANTER** o uso atual (93/2023); confirmado que 24/2012 não está e não deve ser reintroduzida. | — |
| Guia de Elaboração de PPC da PROGRAD, 3ª edição (2021) | Usado no `.bib` (`UFU:GuiaPPC:2021`). **Não verifiquei se há edição mais recente.** | **EXIGE CONFIRMAÇÃO** — checar se a PROGRAD publicou edição posterior. | não verificado |
| Estatuto e Regimento Geral da UFU | Não citados diretamente em nenhum lugar do projeto atualmente. | **EXIGE ANÁLISE ACADÊMICA** — avaliar se vale citá-los diretamente (hoje aparecem só indiretamente, via competências mencionadas na Res. 177/2026). | — |

---

## 6. Temas transversais (compartilhados — baixo risco)

Todas as cinco normas em `dados/compartilhados/legislacao/` (direitos
humanos, educação ambiental, Libras, relações étnico-raciais, prevenção de
desastres) são federais, antigas (2004-2017) e estáveis — nenhuma delas
apareceu em nenhum alerta de revogação nas buscas realizadas para outros
itens desta auditoria. **Não foram reverificadas individualmente nesta
rodada** (prioridade mais baixa dado o risco reduzido de terem sido
revogadas). **EXIGE CONFIRMAÇÃO** de baixa prioridade.

---

## 7. Bibliografia pedagógica

**Não auditada nesta rodada.** O `.bib` do perfil `tecnologo_automacao_2027_1`
ainda não contém referências pedagógicas próprias (VEIGA, MOREIRA, ABREU,
MASETTO, TORI, FERREIRA etc., citadas no pedido do usuário) — essas citações
existiam no PPC de Engenharia de Computação mencionado pelo usuário, mas esse
texto-fonte não está neste repositório para eu reavaliar item a item. Isso é
trabalho de **Seção 11 do pedido original**, que depende de acesso ao texto
onde essas referências apareciam — **EXIGE ESCLARECIMENTO** de onde vem esse
material de origem antes de eu poder auditá-lo.

---

## 8. O que NÃO foi auditado nesta rodada (limitações desta entrega)

Dado o tamanho do pedido, esta auditoria priorizou os itens com maior risco
de erro concreto (extensão, EaD, CNCST/CINE, regulamentação profissional) e
verificação externa em fontes oficiais. Ficaram **fora desta rodada**:

- Conteúdo pedagógico completo dos 12 capítulos de `textos/` — ver Seção
  "Achado crítico" abaixo.
- `Lei:9394:1996` (LDB), `Decreto:9235:2017` — não estão no projeto, não
  avaliei se deveriam ser adicionados.
- Instrumentos do Inep para avaliação de cursos, normas do Enade — não
  pesquisados.
- Verificação linha a linha de cada uma das ~50 entradas `.bib` restantes
  (ISBN de livros, URLs quebradas não relacionadas às normas acima).
- Testes automáticos e validadores novos (Seção 14 do pedido) — depende do
  conjunto final de normas "proibidas", que só se consolida depois que as
  pendências acima forem resolvidas.

---

## Achado crítico: o problema não é só a bibliografia

A auditoria dos arquivos `.tex` (Seção 9 do pedido) revelou que **todo o
diretório `textos/` deste perfil ainda é, substancialmente, o texto do PPC de
Engenharia de Computação**, copiado ao criar o esqueleto deste curso. Exemplos
encontrados nesta auditoria, além dos já corrigidos em rodadas anteriores
(identificação, extensão):

- `apresentacao.tex` contém um capítulo inteiro ("Sobre a CC2020 da ACM",
  ~200 linhas) mapeando áreas de conhecimento específicas de Engenharia da
  Computação/Ciência da Computação — sem qualquer relação com Automação
  Industrial — e narra uma "reformulação de 2025" e "última reformulação de
  2018" que são a história real do curso de Engenharia de Computação, não
  deste curso novo.
- `perfil_egresso.tex` afirma que "o título profissional conferido é o de
  Engenheiro de Computação", com atribuições do CONFEA específicas de
  engenheiro (Resoluções 473/2002, 380/1993, 218/1973) — incompatível com um
  curso de Tecnólogo.
- `objetivos.tex`, `diretrizes_pedagogicas.tex`, `justificativa.tex` citam
  as Diretrizes Curriculares Nacionais de Computação (Resolução CNE/CES nº
  5/2016) como fundamento obrigatório do curso — o pedido do usuário é
  explícito que isso não pode ser tratado como DCN do CST.

**Isto não é um problema de referências desatualizadas — é conteúdo
pedagógico de outro curso.** Corrigir isso exige reescrever a prosa
substantiva de praticamente todos os 12 capítulos (perfil do egresso,
competências, metodologia, objetivos) com decisões que descrevem *este*
curso: que competências específicas ele desenvolve, que metodologia usa, como
articula com Robótica/IA — informação que não estava no pedido do usuário e
que, pelas próprias restrições que o usuário definiu ("não altere
silenciosamente decisões acadêmicas... registre como pendência em vez de
inventar"), eu não devo inventar.

## Plano de implementação proposto (próximos passos)

Dado o tamanho do que falta, proponho dividir o restante em fases
independentes, para evitar produzir um PPC com conteúdo pedagógico fabricado:

1. **Fase 1 — normativo/bibliográfico — CONCLUÍDA nesta rodada**: CONFEA
   313/1986, CONGRAD 46/2022, Portaria Inep 622/2025, Portaria MEC 378/2025
   adicionadas; chaves do `.bib` padronizadas (Seção 10 do pedido).
2. **Fase 2 — arquitetura EaD no `ppcgen` — CONCLUÍDA nesta rodada** (bloco
   `oferta:`, validador, testes — ver seção acima). **Não incluída nesta
   fase**: os campos de carga horária síncrona/assíncrona por componente na
   matriz (Seção 7 do pedido) — mudança maior, ainda pendente. O campo
   `oferta.norma_institucional` deste perfil permanece `pendente` até a UFU
   publicar a resolução do CONGRAD.
3. **Fase 3 — capítulo `textos/educacao_digital_e_ead.tex`**: posso redigir
   um primeiro rascunho técnico-normativo (o que a lei exige), mas as
   decisões pedagógicas (qual AVA, que metodologia de mediação, etc.) exigem
   confirmação do NDE.
4. **Fase 4 — reescrita pedagógica dos 12 capítulos**: a mais sensível.
   Recomendo que você (ou o NDE) me passe, ao menos, o perfil de
   competências/egresso pretendido para o Tecnólogo em Automação Industrial
   — caso contrário, o máximo que posso fazer com responsabilidade é remover
   o conteúdo de Engenharia claramente incompatível e marcar `[PENDENTE —
   NDE/Colegiado]` no lugar, sem redigir competências, metodologia ou perfil
   do egresso novos.
5. **Fase 5 — validações, testes, relatório de conformidade, compilação
   final**: só faz sentido depois que as Fases 2-4 estabilizarem, porque os
   testes precisam saber o conjunto final de normas e campos válidos.

Meu recomendo seguir nessa ordem, mas a decisão de prioridade e de quanto
avançar sem input do NDE é sua.
