PYTHON ?= python3

.PHONY: install validate generate pdf complete compare test lint format clean \
        perfis perfil-info perfil-validar perfil-criar perfil-clonar \
        validate-all generate-all complete-all clean-all require-profile

# A maioria dos alvos abaixo opera sobre UM perfil e exige `PROFILE=<id>`
# explicitamente — nunca há um perfil padrão (Seção 6/21: seleção sempre
# explícita). Ex.: `make validate PROFILE=engenharia_computacao_2026_1`.
require-profile:
ifndef PROFILE
	$(error PROFILE não informado. Uso: make <alvo> PROFILE=<id-do-perfil> — veja `make perfis` para os disponíveis)
endif

install:
	$(PYTHON) -m pip install -e .[dev]

validate: require-profile
	$(PYTHON) -m ppcgen validar --perfil $(PROFILE)

generate: require-profile
	$(PYTHON) -m ppcgen gerar --perfil $(PROFILE)

pdf: require-profile
	$(PYTHON) -m ppcgen compilar --perfil $(PROFILE)

complete: require-profile
	$(PYTHON) -m ppcgen completo --perfil $(PROFILE)

compare:
	$(PYTHON) -m ppcgen comparar --anterior $(ANTERIOR) --atual $(ATUAL)

# Comandos em lote (Seção 20): operam sobre todos os perfis ativos, com
# filtro opcional por status (`make validate-all STATUS=vigente`).
validate-all:
	$(PYTHON) -m ppcgen validar-todos $(if $(STATUS),--status $(STATUS))

generate-all:
	$(PYTHON) -m ppcgen gerar-todos $(if $(STATUS),--status $(STATUS))

complete-all:
	$(PYTHON) -m ppcgen completo-todos $(if $(STATUS),--status $(STATUS))

# Gestão de perfis (Seção 15).
perfis:
	$(PYTHON) -m ppcgen perfis

perfil-info: require-profile
	$(PYTHON) -m ppcgen perfil-info --perfil $(PROFILE)

perfil-validar: require-profile
	$(PYTHON) -m ppcgen perfil-validar --perfil $(PROFILE)

perfil-criar:
ifndef ID
	$(error ID não informado. Uso: make perfil-criar ID=<novo-id> NOME="Nome do Curso")
endif
	$(PYTHON) -m ppcgen perfil-criar --id $(ID) --nome "$(NOME)"

perfil-clonar:
ifndef ORIGEM
	$(error ORIGEM não informado. Uso: make perfil-clonar ORIGEM=<id> DESTINO=<novo-id>)
endif
ifndef DESTINO
	$(error DESTINO não informado. Uso: make perfil-clonar ORIGEM=<id> DESTINO=<novo-id>)
endif
	$(PYTHON) -m ppcgen perfil-clonar --origem $(ORIGEM) --destino $(DESTINO)

test:
	$(PYTHON) -m pytest

lint:
	ruff check ppcgen testes scripts

format:
	ruff format ppcgen testes scripts

# Remove apenas artefatos temporários/recriáveis do perfil informado
# (saida/<perfil>/ — build do LaTeX, PDFs, relatórios). NÃO remove nada em
# dados/perfis/<perfil>/ — fontes e dados curriculares nunca são apagados
# por este alvo. Use `make clean-all` para limpar a saída de todos os perfis.
clean: require-profile
	$(PYTHON) -m ppcgen limpar --perfil $(PROFILE)

clean-all:
	$(PYTHON) -m ppcgen limpar --todos
