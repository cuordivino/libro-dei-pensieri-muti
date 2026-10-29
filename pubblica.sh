#!/usr/bin/env bash
# Pubblica il sito su GitHub (Mac/Linux). Uso:  ./pubblica.sh
set -e
USER_GH="${1:-cuordivino}"; REPO="${2:-libro-dei-pensieri-muti}"
command -v git  >/dev/null || { echo "Installa Git (https://git-scm.com)"; exit 1; }
command -v node >/dev/null || { echo "Installa Node.js LTS (https://nodejs.org)"; exit 1; }
[ -d node_modules ] || npm install
echo "Controllo il sito..."; npm run check || { echo "Il controllo ha trovato errori: non pubblico."; exit 1; }
URL="${PUBBLICA_REMOTE:-https://github.com/$USER_GH/$REPO.git}"
if [ ! -d .git ]; then
  git init -b main >/dev/null; git remote add origin "$URL"
  if git fetch origin main 2>/dev/null; then git tag -f v1 origin/main >/dev/null; git reset --soft origin/main; fi
fi
git add -A
if git diff --cached --quiet; then echo "Nessuna modifica da pubblicare."; else git commit -m "Il Libro dei Pensieri Muti, versione 2"; fi
git push -u origin main; git push origin --tags 2>/dev/null || true
echo; echo "Fatto. La pubblicazione parte da sola (circa 2 minuti)."
echo "Prima volta? Su GitHub: Settings > Pages > Source: GitHub Actions."
echo "Il sito sarà su: https://$USER_GH.github.io/$REPO/"
