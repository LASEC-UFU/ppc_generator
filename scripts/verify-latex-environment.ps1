<#
.SYNOPSIS
    Verifica se o ambiente local tem tudo o que o ppcgen precisa para
    compilar um PPC em PDF (latexmk, biber, e os pacotes LaTeX usados pelos
    templates genéricos em templates/latex/).

.DESCRIPTION
    Não instala nada — apenas diagnostica. Para instalar o necessário no
    Windows com MiKTeX, veja install-latex-minimal.ps1.
#>

$ErrorActionPreference = "Continue"
$falhou = $false

function Test-Comando($nome, $args) {
    $cmd = Get-Command $nome -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Host "[FALTA] $nome não encontrado no PATH." -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] $nome -> $($cmd.Source)" -ForegroundColor Green
    return $true
}

Write-Host "== Verificando executáveis ==" -ForegroundColor Cyan
$temPython = Test-Comando "python"
$temLatexmk = Test-Comando "latexmk"
$temBiber = Test-Comando "biber"
$temPdflatex = Test-Comando "pdflatex"

if (-not ($temLatexmk -and $temBiber -and $temPdflatex)) { $falhou = $true }

Write-Host ""
Write-Host "== Verificando pacotes LaTeX exigidos pelos templates genéricos ==" -ForegroundColor Cyan
# Extraídos de templates/latex/configuracoes/Estilos.tex e Main.tex — se um
# novo \usepackage for adicionado lá, adicione o nome do pacote aqui também.
$pacotesNecessarios = @(
    "geometry", "fancyhdr", "xcolor", "tabularray", "biblatex", "biber",
    "csquotes", "hyperref", "enumitem", "footnotehyper", "pdflscape",
    "xspace", "soul", "caption", "makecell"
)

foreach ($pacote in $pacotesNecessarios) {
    $resultado = & mpm --find-package="$pacote" 2>&1
    if ($LASTEXITCODE -eq 0 -and $resultado -match "installed") {
        Write-Host "[OK] pacote '$pacote' instalado" -ForegroundColor Green
    }
    else {
        Write-Host "[FALTA] pacote '$pacote' não encontrado via mpm (MiKTeX) — pode ainda funcionar se o AutoInstall estiver ativo." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "== Testando uma compilação mínima ==" -ForegroundColor Cyan
$pastaTeste = Join-Path $env:TEMP "ppcgen-verify-latex"
New-Item -ItemType Directory -Force -Path $pastaTeste | Out-Null
$texMinimo = @'
\documentclass{article}
\usepackage[backend=biber]{biblatex}
\usepackage{tabularray}
\begin{document}
Teste de compilação mínima do ppcgen.
\end{document}
'@
Set-Content -Path (Join-Path $pastaTeste "teste.tex") -Value $texMinimo -Encoding utf8

Push-Location $pastaTeste
& latexmk -pdf -interaction=nonstopmode -halt-on-error teste.tex 2>&1 | Out-Null
$compilou = Test-Path "teste.pdf"
Pop-Location

if ($compilou) {
    Write-Host "[OK] compilação mínima funcionou." -ForegroundColor Green
}
else {
    Write-Host "[FALTA] compilação mínima falhou — veja $pastaTeste\teste.log" -ForegroundColor Red
    $falhou = $true
}

Write-Host ""
if ($falhou) {
    Write-Host "Ambiente incompleto. No Windows com MiKTeX, rode scripts\install-latex-minimal.ps1." -ForegroundColor Red
    exit 1
}
else {
    Write-Host "Ambiente LaTeX pronto para 'python -m ppcgen compilar' / 'completo'." -ForegroundColor Green
    exit 0
}
