<#
.SYNOPSIS
    Instala/configura o mínimo necessário do MiKTeX no Windows para compilar
    um PPC gerado pelo ppcgen (latexmk, biber e os pacotes usados pelos
    templates genéricos em templates/latex/).

.DESCRIPTION
    Pressupõe que o MiKTeX já esteja instalado (https://miktex.org/download).
    Este script apenas ativa a instalação automática de pacotes sob demanda
    e garante que o repositório de pacotes esteja configurado — os mesmos
    passos manuais necessários durante o desenvolvimento deste projeto numa
    instalação "fresh" do MiKTeX. Depois de rodar, use
    verify-latex-environment.ps1 para confirmar.
#>

$ErrorActionPreference = "Stop"

function Requer-Comando($nome) {
    if (-not (Get-Command $nome -ErrorAction SilentlyContinue)) {
        Write-Host "[ERRO] '$nome' não encontrado no PATH. Instale o MiKTeX primeiro: https://miktex.org/download" -ForegroundColor Red
        exit 1
    }
}

Requer-Comando "initexmf"
Requer-Comando "mpm"

Write-Host "== Ativando instalação automática de pacotes (AutoInstall) ==" -ForegroundColor Cyan
& initexmf --set-config-value="[MPM]AutoInstall=1"

Write-Host ""
Write-Host "== Configurando repositório de pacotes ==" -ForegroundColor Cyan
$repositorios = & mpm --list-repositories 2>&1
$primeiroRepositorio = ($repositorios | Select-String -Pattern "^\S+://" | Select-Object -First 1)
if (-not $primeiroRepositorio) {
    Write-Host "[ERRO] não foi possível listar repositórios via 'mpm --list-repositories'. Verifique a conexão de rede." -ForegroundColor Red
    exit 1
}
$urlRepositorio = ($primeiroRepositorio -split '\s+')[0]
Write-Host "Usando repositório: $urlRepositorio"
& mpm --set-repository="$urlRepositorio"

Write-Host ""
Write-Host "== Atualizando banco de dados de pacotes ==" -ForegroundColor Cyan
& mpm --update-db

Write-Host ""
Write-Host "== Instalando pacotes usados pelos templates genéricos ==" -ForegroundColor Cyan
# Mesma lista verificada por verify-latex-environment.ps1 — mantenha as duas
# sincronizadas se um novo \usepackage for adicionado em templates/latex/.
$pacotes = @(
    "latexmk", "biber", "biblatex", "geometry", "fancyhdr", "xcolor",
    "tabularray", "csquotes", "hyperref", "enumitem", "footnotehyper",
    "pdflscape", "xspace", "soul", "caption", "makecell"
)
foreach ($pacote in $pacotes) {
    Write-Host "Instalando '$pacote'..."
    & mpm --install="$pacote" 2>&1 | Out-Null
}

Write-Host ""
Write-Host "Concluído. Rode scripts\verify-latex-environment.ps1 para confirmar o ambiente." -ForegroundColor Green
