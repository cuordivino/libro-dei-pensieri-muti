# Pubblica il sito su GitHub (PowerShell, da eseguire nella cartella del progetto)
# Uso:  .\pubblica.ps1
param(
  [string]$User = "cuordivino",
  [string]$Repo = "libro-dei-pensieri-muti"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Git non è installato: scaricalo da https://git-scm.com/download/win e rilancia lo script." -ForegroundColor Red
  exit 1
}

if (-not (Test-Path ".git")) { git init -b main }

git add .
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m "Il Libro dei Pensieri Muti" }

$remote = git remote
if ($remote -notcontains "origin") {
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    # GitHub CLI disponibile: crea il repository pubblico e fa il push
    gh repo create "$User/$Repo" --public --source . --remote origin --push
    Write-Host "Fatto. Ora attiva Pages: Settings > Pages > Source: GitHub Actions" -ForegroundColor Green
    exit 0
  }
  git remote add origin "https://github.com/$User/$Repo.git"
}

git push -u origin main
Write-Host ""
Write-Host "Fatto. Ora attiva Pages: Settings > Pages > Source: GitHub Actions" -ForegroundColor Green
Write-Host "Il sito sarà su: https://$User.github.io/$Repo/" -ForegroundColor Green
