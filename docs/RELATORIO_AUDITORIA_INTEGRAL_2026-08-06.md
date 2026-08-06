# Relatório de auditoria integral dos PPCs

Data de corte: 6 de agosto de 2026  
Perfis: `tecnologo_automacao_2027_1` e `engenharia_automacao_2027_1`  
Escopo: matrizes `.xlsm`, textos LaTeX, arquivos gerados, fichas localizadas, referências, links, validações, gerador, compilação e inspeção visual dos PDFs.

## 1. Sumário executivo

Os dois PPCs **compilam**, mas **não estão aptos para submissão ou oferta**. A auditoria confirmou problemas que exigem deliberação acadêmica ou ato institucional e que não podem ser corrigidos editorialmente:

1. A matriz da Engenharia está incompleta. O total de 3.630h usa uma linha agregadora `FEELT!OPT — MÓDULO OPTATIVO — 1.040h`; excluída essa linha, as 16 optativas cursáveis somam 960h, abaixo das 1.040h exigidas. Nenhuma está vinculada às ênfases MIAPI, RASC ou SEICI, e os períodos finais não possuem corpo suficiente de componentes específicos de Engenharia.
2. A proposta de ABI não apresenta ato institucional de criação, ingresso, código acadêmico, vagas, escolha ou continuidade entre os dois cursos. A permanência de vínculo da Resolução CONGRAD nº 46/2022 refere-se a habilitação, modalidade ou certificado de estudos de um mesmo curso; não basta, isoladamente, para assegurar segunda graduação entre cursos com PPCs, códigos e diplomas distintos.
3. A extensão está abaixo do piso de 10% nos totais atualmente calculados: 240/2.430h no Tecnólogo e 360/3.630h na Engenharia, ambos 9,9%. No Tecnólogo, a decisão sobre as 30h optativas altera o denominador: se o total definitivo for 2.400h, as 240h atingem exatamente 10%; se for 2.430h, será necessário ampliar a extensão.
4. Libras não está operacionalizada como componente optativo ativo em nenhuma das matrizes, embora exista uma ficha isolada no acervo do Tecnólogo.
5. Permanecem ausentes ou pendentes atos de criação/reformulação, justificativa formal de vagas, normas complementares de estágio, fichas completas de ACE, regulamento de TCC da Engenharia e validação institucional da carga mediada por tecnologia.

Foram corrigidos diretamente os erros objetivos: base normativa do ABI, citação indevida do Parecer CNE/CES nº 136/2012 para AAC, aplicação da Resolução CONFEA nº 1.073/2016, generalização indevida do SIEX, regra sem fonte de 20% de EaD por disciplina, notas de carga horária desatualizadas, links institucionais em HTTP, documentação do repositório, detecção de agregador optativo, compilação MiKTeX sem Perl e tabelas que ultrapassavam as margens.

## 2. Resultado por perfil

| Perfil | Componentes ativos | Total configurado/calculado | Extensão | Resultado do validador | Situação |
|---|---:|---:|---:|---:|---|
| Tecnólogo em Automação Industrial | 40 | 2.400h / 2.430h | 240h (9,9% sobre 2.430h) | 3 erros, 32 alertas | Bloqueado |
| Engenharia de Automação, Robótica e IA | 61 | 3.630h / 3.630h, com agregador optativo inválido | 360h (9,9%) | 7 erros, 57 alertas | Bloqueado |

O subsistema de fichas reportou, adicionalmente, 7 alertas estruturais em cada perfil: nenhuma ficha optativa categorizada e ausência das pastas esperadas `obrigatorias`, `optativas`, `extensao`, `tcc`, `estagio` e `complementares`. O acervo existente foi mantido; sua reorganização deve respeitar as alterações ainda não consolidadas no diretório de trabalho.

## 3. Conformidade normativa

| Tema/norma verificada | Tecnólogo | Engenharia | Conclusão e providência |
|---|---|---|---|
| Lei nº 15.388/2026 — PNE vigente | Parcial | Parcial | Atualizar a aba `Legislacao`; a Lei nº 13.005/2014 pode permanecer apenas como referência histórica. |
| Resolução CNE/CP nº 1/2021 e CNCST 4ª ed. | Parcial | Não aplicável como DCN | Denominação e mínimo de 2.400h do CST são compatíveis; falta fechar total, optativas e Libras. Remover da Engenharia resíduos usados como se fossem base do bacharelado. |
| Resoluções CNE/CES nº 2/2019 e nº 1/2021 — Engenharia | Não aplicável | Não demonstrada | A matriz e as competências técnicas específicas ainda não demonstram integralmente o perfil de Engenharia, sobretudo do 7º ao 10º período. |
| Resolução CONGRAD nº 177/2026 — ACE | Não conforme no total atual | Não conforme | Resolver o total definitivo; assegurar ≥10%, ao menos 3 componentes em períodos distintos, fichas completas quando houver disciplina de extensão, governança e vedação de dupla contagem. |
| Decreto nº 12.456/2025 e Portaria MEC nº 378/2025 | Parcial | Parcial | O teto global de 30% para o formato presencial foi preservado. Removida regra sem fonte de 20% por disciplina. Falta validação institucional da UFU e coerência entre matriz, ficha e plano de ensino. |
| Decreto nº 5.626/2005 — Libras | Não conforme | Não conforme | Cadastrar componente optativo ativo e ficha correspondente; a ficha isolada não integra a matriz. |
| Lei nº 11.788/2008 e Resolução CONGRAD nº 93/2023 — estágio | Parcial | Parcial | Incluir a lei federal na base; elaborar norma do CST; ratificar/revisar a norma do curso predecessor e resolver pré-requisitos dos Estágios I e II da Engenharia. |
| Resolução CONGRAD nº 46/2022 — permanência de vínculo | Não sustenta a redação original | Não sustenta a redação original | Redação corrigida para hipótese condicionada. Exigir ato específico para dois cursos distintos. |
| Lei nº 13.146/2015, Res. CNE/CP nº 1/2004 e nº 2/2012 | Parcial | Parcial | Temas aparecem no texto/mapeamento, mas a cobertura efetiva deve ser confirmada nas fichas. Incluir também a Lei nº 14.926/2024 na educação ambiental. |
| Resoluções CONFEA nº 313/1986, 1.073/2016 e 1.156/2025 | Parcial | Parcial | Corrigida a afirmação de que a Res. 1.073 se aplicaria apenas a Tecnólogos. Atribuições concretas dependem da formação comprovada e da análise do CREA. |
| Ato de criação/reformulação, vagas e ABI | Ausente | Ausente | Bloqueio institucional: anexar resoluções/atos, instrumento do programa citado, capacidade de oferta, códigos, vagas e procedimento ABI. |

Fontes oficiais centrais consultadas:

- [Lei nº 15.388/2026 — Plano Nacional de Educação](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15388.htm)
- [Decreto nº 12.456/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/decreto/d12456.htm)
- [Resoluções CNE/CES de 2019](https://www.gov.br/mec/pt-br/cne/resolucoes/resolucoes-cne-ces-2019)
- [Histórico e atos da CINE Brasil](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/cine-brasil/historico)
- [Resolução CONFEA nº 1.073/2016](https://normativos.confea.org.br/Ementas/Visualizar?id=59111)
- [Resolução CONFEA nº 1.156/2025](https://normativos.confea.org.br/Ementas/Visualizar?id=82360)
- [Decreto nº 5.626/2005 — Libras](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2005/decreto/d5626.htm)
- [Lei nº 13.146/2015 — Lei Brasileira de Inclusão](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm)
- [Normas de estágio da UFU — Resolução CONGRAD nº 93/2023](https://www.prograd.ufu.br/legislacoes/resolucao-congrad-no-93-de-06022023-normas-gerais-de-estagio-do-ensino-de-graduacao-da)

## 4. Achados detalhados

| ID | Severidade | Perfil | Evidência | Ação | Estado |
|---|---|---|---|---|---|
| CUR-01 | Crítica | Engenharia | `FEELT!OPT`, 1.040h, nome `MÓDULO OPTATIVO`; elenco real = 960h | Excluir a linha agregadora e cadastrar/deliberar componentes cursáveis suficientes | Pendente do NDE |
| CUR-02 | Crítica | Engenharia | MIAPI, RASC e SEICI = 0h vinculadas; mínimo de 2 ênfases × 400h | Definir componentes, nomes/vínculos, ementas, oferta e regras de integralização | Pendente do NDE |
| CUR-03 | Crítica | Engenharia | 7º: ACE IV; 8º: ACE V; 9º: TCC; 10º: Estágio II | Completar o corpo específico de Engenharia e demonstrar aderência às DCN | Pendente do NDE |
| ABI-01 | Crítica | Ambos | Não há ato de ABI, ingresso, vagas, código ou escolha | Aprovação institucional antes da oferta | Pendente institucional |
| ABI-02 | Crítica | Ambos | Dois cursos distintos foram tratados como hipótese comum de permanência da Res. 46/2022 | Criar base normativa específica ou retirar a continuidade/segundo diploma | Texto corrigido; ato pendente |
| EXT-01 | Alta | Ambos | 9,9% de extensão nos totais atuais | Ajustar total/carga ACE e revalidar; decisão acadêmica | Pendente do NDE |
| EXT-02 | Alta | Ambos | Fichas completas de ACE e procedimento de comprovação não localizados | Elaborar fichas/norma; registrar UFU no sistema institucional e aceitar comprovação institucional externa conforme regra aprovada | Pendente; texto corrigido |
| LIB-01 | Alta | Ambos | `HUM_LIBRAS` sem componente ativo | Cadastrar Libras como optativa e vincular ficha | Pendente do NDE |
| TEC-01 | Alta | Tecnólogo | Total calculado 2.430h versus 2.400h; 30h optativas sem elenco | Deliberar total e elenco, depois recalcular extensão | Pendente do NDE |
| TCC-01 | Alta | Engenharia | Perfil exige 30h; `FEELT!TCC` está como `disciplina`, logo soma do tipo TCC = 0h | Alterar para `tipo=tcc` se essa for a decisão e aprovar regulamento | Pendente do NDE |
| EST-01 | Alta | Engenharia | Estágio I: 900h na matriz versus 1.800h na norma do predecessor; Estágio II sem pré-requisito | Ratificar/revisar norma complementar e matriz | Pendente do Colegiado |
| DEN-01 | Alta | Engenharia | Nova denominação e programa citado sem ato específico anexado | Anexar aprovações e justificativa regulatória | Pendente institucional |
| COD-01 | Alta | Ambos | 30 códigos provisórios no CST; 52 na Engenharia | Substituir por códigos oficiais antes da aprovação | Pendente do registro acadêmico |
| FIC-01 | Alta | Ambos | Pastas categorizadas e fichas optativas/ACE/TCC/estágio ausentes do fluxo do gerador | Consolidar acervo e completar fichas após fechar a matriz | Pendente |
| EAD-01 | Média | Ambos | `status_validacao_institucional=pendente`; texto fixava 20% por disciplina sem base localizada | Removido o limite inventado; confirmar regra UFU e fichas | Parcialmente corrigido |
| REF-01 | Média | Ambos | 47 URLs únicas; 11 HTTP; fontes Semesp/ABMES/UFRGS e links antigos do MEC | Trocar por Planalto, MEC/CNE, INEP, UFU e CONFEA oficiais na planilha | Pendente na matriz |
| REF-02 | Média | Ambos | Parecer CNE/CES nº 136/2012 é da área de Computação, mas fundamentava AAC | Fundamento removido dos dois textos | Corrigido |
| TXT-01 | Média | Engenharia | Competências técnicas herdadas do CST; alta identidade textual em seções pedagógicas | Reescrever perfil/competências e diferenciar metodologia/avaliação de Engenharia | Pendente do NDE |
| TXT-02 | Média | Ambos | `Materias Elétricos...`, `Maquinas`, `IoT E IIoT`, variações de `IIOT` | Corrigir nomes na fonte `.xlsm` e conferir contra fichas e SIGAA | Pendente na matriz |
| TXT-03 | Média | Ambos | Marcadores editoriais vermelhos e comentários `REVISAR` permanecem em decisões não tomadas | Substituir por conteúdo aprovado antes da versão de submissão | Pendente; não inventado |
| GEN-01 | Média | Gerador | `latexmk` do MiKTeX falhava sem Perl | Implementado fallback `pdflatex → biber → pdflatex × 2` | Corrigido e testado |
| GEN-02 | Média | Gerador | Agregador optativo mascarava pool insuficiente | Nova regra `COMPONENTE_AGREGADOR_OPTATIVO`; agregador excluído do pool | Corrigido e testado |
| GEN-03 | Alta | Gerador/Tecnólogo | Arquivos gerados antigos permaneciam em `saida/`; uma tabela de equivalências de 01/08 era incluída embora ausente da matriz atual | Limpeza restrita a `.tex`/`.bib` com cabeçalho do gerador; arquivos manuais preservados | Corrigido e testado |
| GEN-04 | Média | Gerador | Compilação interrompida deixou `Main.aux` truncado e bloqueou a execução seguinte | Limpeza preventiva dos auxiliares temporários antes de cada compilação | Corrigido e testado |
| LAT-01 | Média | Ambos | Fluxo excedia a largura em 225pt; pré-requisitos em 85pt; cabeçalho quebrava com títulos longos | Colunas, espaçamento, cabeçalho e título ajustados | Corrigido visualmente |
| LAT-02 | Média | Ambos | Quadro ACE, comparação ABI, representação gráfica e identificadores técnicos longos geravam estouros; a Engenharia registrava `Float too large` | Colunas flexíveis, quebras seguras e limite da representação gráfica; recompilação e inspeção visual | Corrigido |
| DOC-01 | Baixa | Repositório | README listava perfis e caminhos antigos | Atualizado para os perfis atuais e fallback de compilação | Corrigido |

## 5. Auditoria textual e de coerência

- Os cinco primeiros períodos das matrizes são idênticos por código, nome, carga e tipo, o que sustenta a afirmação de etapa curricular comum; isso não resolve o mecanismo jurídico/administrativo de ABI.
- A Engenharia reutiliza extensamente textos do CST: `atendimento_estudante` (aprox. 99,5%), `diretrizes_pedagogicas` (98,7%), `avaliacao` (97,3%), `principios` (95,9%) e `acompanhamento_egresso` (94,5%). Partes institucionais podem ser comuns, mas perfil, competências, metodologia e avaliação devem evidenciar a complexidade de Engenharia.
- A afirmação de que a Resolução CONFEA nº 1.073/2016 seria exclusiva de Tecnólogos foi corrigida. A Resolução nº 313/1986 é a norma específica dos Tecnólogos; a sistemática da nº 1.073/2016 é geral.
- A exigência universal de certificado SIEX foi corrigida: ações UFU seguem o sistema institucional; ações externas precisam de comprovação institucional conforme procedimento aprovado.
- Notas antigas de 2.700h/3.825h, 80h de AAC, 9,4% de extensão e 44 componentes foram substituídas pelos dados atuais.
- O arquivo incompleto `resolucaoCONGRAD-2026-177.pdf.crdownload`, presente no acervo, não é fonte normativa válida e deve ser removido manualmente após conferência; não foi apagado nesta auditoria para preservar dados preexistentes.

## 6. Links e referências

A planilha deve substituir espelhos e portais de entidades privadas por fontes primárias. Prioridades:

- Portaria MEC nº 378/2025: DOU/MEC em lugar de Semesp.
- CNCST e Portaria MEC nº 514/2024: dados abertos/MEC em lugar de ABMES.
- Portaria INEP nº 622/2025 e CINE Brasil: INEP em lugar de ABMES.
- Resoluções CONFEA: portal oficial `normativos.confea.org.br` em lugar de espelhos universitários.
- Sites UFU/FEELT: HTTPS.
- A referência interna inexistente `referenciais/cncst_automacao_industrial.yaml` foi removida do texto.

Também devem ser saneados: a identificação inconsistente de `UFU_CONSUN_31_2022`, normas revogadas ou parcialmente revogadas (Resolução CONGRAD nº 13/2019 e Resolução CONFEA nº 380/1993), e resíduos não aplicáveis do PPC anterior (Parecer CNE/CES nº 5/2016, Portaria SERES nº 647/2018 e Parecer CNE/CES nº 136/2012, salvo justificativa histórica expressa).

## 7. Verificação técnica

| Verificação | Resultado |
|---|---|
| `pytest -q` | **163 testes aprovados** em 10,43s |
| `ruff check .` | **All checks passed** |
| Validação do Tecnólogo | 3 erros e 32 alertas; bloqueio acadêmico reproduzido |
| Validação da Engenharia | 7 erros e 57 alertas; bloqueio acadêmico reproduzido |
| Compilação real | Ambos os corpos PDF gerados por fallback direto; `latexmk` continua indisponível por falta de Perl |
| Citações/referências LaTeX | Nenhuma referência indefinida ou label duplicada nos dois logs finais |
| Log de layout | Nenhum `Float too large`; permanecem avisos tipográficos pequenos e o excesso intencional da faixa gráfica da capa, sem corte visual |
| Inspeção visual | Capas, tabelas multipágina, fluxos, quadros ACE, comparação ABI, ênfases e optativas inspecionados; sem tabela ou URL cortada nas regiões auditadas |
| PDFs de corpo | Tecnólogo: 128 páginas; Engenharia: 145 páginas |
| PDFs completos com anexos | Não gerados pela CLI, pois a validação crítica bloqueia corretamente `completo` |

Os PDFs de corpo são **artefatos de auditoria**, não versões aprovadas. Foram gerados pela API interna somente para testar o LaTeX, sem desativar `geracao.interromper_em_erro` nos perfis.

## 8. Arquivos alterados nesta auditoria

- `ppcgen/compiladores/latex.py`
- `ppcgen/geradores/bibliografia.py`
- `ppcgen/validadores/cargas.py`
- `ppcgen/geradores/fluxo.py`
- `ppcgen/geradores/latex.py`
- `ppcgen/geradores/representacao_grafica.py`
- `ppcgen/geradores/tabelas.py`
- `templates/latex/configuracoes/Estilos.tex`
- `testes/integracao/test_pipeline_completo.py`
- `testes/unitarios/test_geradores_bibliografia.py`
- `testes/unitarios/test_geradores_tabelas.py`
- `testes/unitarios/test_isolamento_perfis.py`
- `testes/unitarios/test_validador_cargas.py`
- `docs/VALIDACOES.md`
- `README.md`
- textos dos dois perfis: `apresentacao.tex`, `identificacao.tex`, `justificativa.tex`, `estrutura_curricular.tex`, `perfil_egresso.tex`, `abi_trajetorias_formativas.tex`, `atendimento_estudante.tex`, `acompanhamento_egresso.tex`, `avaliacao.tex`, `consideracoes_finais.tex`, `diretrizes_pedagogicas.tex`; e `modulos_optativos_areas_formacao.tex` na Engenharia.

Nesta retomada, as planilhas `.xlsm`, fichas e anexos binários não foram editados. Alterações binárias e renomeações já existentes no diretório de trabalho foram preservadas; os ajustes acadêmicos neles continuam dependentes de decisão competente.

## 9. Checklist para liberação

- [ ] Aprovar atos de criação/reformulação, denominação, turno e vagas.
- [ ] Aprovar ato completo da ABI ou remover dos PPCs tudo o que não for institucionalmente autorizado.
- [ ] Fechar a matriz específica da Engenharia e suas competências.
- [ ] Remover o agregador de 1.040h e cadastrar elenco optativo integralizável.
- [ ] Vincular e tornar viáveis ao menos duas ênfases de 400h, se essa arquitetura for mantida.
- [ ] Resolver total/optativas do Tecnólogo.
- [ ] Atingir 10% de extensão sobre o total definitivo em cada curso.
- [ ] Cadastrar Libras como optativa em ambos.
- [ ] Tipificar TCC e aprovar regulamento da Engenharia.
- [ ] Aprovar/atualizar normas de estágio e pré-requisitos.
- [ ] Elaborar fichas completas de ACE e procedimento de validação.
- [ ] Substituir todos os códigos `FEELT!` por códigos oficiais.
- [ ] Consolidar fichas por categoria e conferir código, nome, carga, ementa, bibliografia e unidade ofertante.
- [ ] Corrigir grafia e padronização dos nomes na planilha.
- [ ] Atualizar a aba `Legislacao` com fontes oficiais vigentes e remover resíduos.
- [ ] Substituir marcadores editoriais por decisões aprovadas e dados institucionais definitivos.
- [ ] Executar `python -m ppcgen validar` até obter zero erro.
- [ ] Executar `python -m ppcgen completo` e revisar o PDF com todas as fichas e resoluções anexadas.
