# Pubblica il sito su GitHub (Windows, PowerShell). Uso:  .\pubblica.ps1
# Prima controlla il sito; se il controllo non passa, non pubblica. La versione 1 resta salvata (etichetta v1).
param([string]$User = "cuordivino", [string]$Repo = "libro-dei-pensieri-muti")
$ErrorActionPreference = "Stop"
function Fail($m) { Write-Host $m -ForegroundColor Red; exit 1 }
if (-not (Get-Command git  -ErrorAction SilentlyContinue)) { Fail "Git non è installato: scaricalo da https://git-scm.com/download/win e rilancia." }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Fail "Node.js non è installato: scaricalo da https://nodejs.org (versione LTS) e rilancia." }

if (-not (Test-Path "node_modules")) { Write-Host "Installo le dipendenze..." -ForegroundColor Cyan; npm install; if ($LASTEXITCODE) { Fail "npm install non è riuscito." } }
Write-Host "Controllo il sito..." -ForegroundColor Cyan
npm run check
if ($LASTEXITCODE) { Fail "Il controllo ha trovato errori (vedi sopra). Non pubblico." }

$url = "https://github.com/$User/$Repo.git"
if (-not (Test-Path ".git")) {
  git init -b main | Out-Null
  git remote add origin $url
  git fetch origin main 2>$null
  if ($LASTEXITCODE -eq 0) {
    # il repository esiste già (versione 1): conservo la sua storia e ci costruisco sopra
    git tag -f v1 origin/main | Out-Null
    git reset --soft origin/main
  }
}
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m "Il Libro dei Pensieri Muti, versione 2" } else { Write-Host "Nessuna modifica da pubblicare." -ForegroundColor Yellow }
git push -u origin main
if ($LASTEXITCODE) { Fail "Il push non è riuscito. Se ti chiede l'accesso, accedi a GitHub nella finestra che si apre e rilancia." }
git push origin --tags 2>$null | Out-Null
Write-Host ""
Write-Host "Fatto. La pubblicazione parte da sola (circa 2 minuti)." -ForegroundColor Green
Write-Host "Prima volta? Su GitHub: Settings > Pages > Source: GitHub Actions." -ForegroundColor Green
Write-Host "Il sito sarà su: https://$User.github.io/$Repo/" -ForegroundColor Green
