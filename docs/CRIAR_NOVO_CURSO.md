# Como criar um novo curso (ou uma nova versão curricular)

> **Este documento descreve a arquitetura anterior à reestruturação para
> múltiplos perfis** (um único `config/curso.yaml` na raiz do repositório,
> uma única `dados/matriz_curricular.xlsx`, um único `latex/capitulos/`).
> Esses caminhos não existem mais.
>
> Para criar um novo curso ou uma nova versão curricular hoje, veja:
>
> - **`docs/CRIAR_PERFIL.md`** — passo a passo atualizado, usando
>   `dados/perfis/<id>/`.
> - **`docs/PERFIS.md`** — o que é um perfil e o schema de `perfil.yaml`.
> - **`docs/ESTRUTURA_DE_DIRETORIOS.md`** — onde cada arquivo vive agora.
> - **`docs/MIGRAR_PERFIL.md`** — se o curso já existe em outro formato
>   (planilha solta, outro gerador) em vez de começar do zero.
>
> Este arquivo é mantido só como referência histórica de como o sistema
> funcionava antes de suportar múltiplos cursos simultaneamente no mesmo
> repositório.
