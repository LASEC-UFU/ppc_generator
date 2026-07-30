# legado/

Este diretório preserva material do sistema anterior de geração do PPC (curso de
Engenharia de Computação) durante a transição para o novo gerador modular (`ppcgen/`).
Nada aqui foi apagado — apenas movido ou copiado para referência e comparação.

## csv_historico/

Variantes do CSV de disciplinas que coexistiam com `py/PPC_disciplinas_final.csv`
sem que o código indicasse qual delas era a fonte oficial:

- `PPC_disciplinas_3450.csv`
- `PPC_disciplinas_3850.csv`
- `PPC_disciplinas_NAO_APAGAR.csv`
- `PPC_disciplinas_XXX.csv`

Comparação feita durante a auditoria (`diff`) mostrou que essas quatro variantes são
idênticas entre si, exceto pelas horas placeholder de ACE/AAC/ACC/OPT (ver
`docs/MIGRACAO.md` para os valores). Nenhuma delas possui as colunas `QEXTR`,
`DCN_base` ou `DCN_ecp`, presentes apenas em `py/PPC_disciplinas_final.csv` — o
arquivo hardcoded na linha 74 de `py/gen_docs.py` e, portanto, a fonte
efetivamente usada para gerar o PPC atual. `py/PPC_disciplinas_final.csv` e
`py/PPC_disciplinas.csv` (usado como saída por `fichas/get_info_fichas.py`)
permanecem em `py/` — não foram tocados, para que `py/gen_docs.py` continue
funcionando exatamente como antes.

## main_pdf_baseline/

Cópia do `Main.pdf` compilado a partir do estado original do repositório
(commit `first commit`), antes de qualquer alteração — usada como baseline para
comparar a saída do PPC de Engenharia de Computação antes/depois da
reestruturação.

## Por que preservar em vez de apagar

Este projeto gera um documento institucional (PPC) com valor legal/acadêmico.
A Seção 21 do pedido de reestruturação exige que nenhuma saída antiga seja
descartada sem documentação, e que seja mantida uma forma de comparar o
resultado anterior com o novo. Este diretório cumpre esse papel enquanto a
migração para `ppcgen/` está em andamento.
