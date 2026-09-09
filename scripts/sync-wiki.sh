#!/usr/bin/env bash
# ==============================================================================
# OSIRIS — Sync wiki/ to GitHub Wiki repository
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WIKI_DIR="${REPO_ROOT}/wiki"
REMOTE_URL="${WIKI_REPO_URL:-https://github.com/richardblaha/osiris-theme.wiki.git}"

if [[ ! -d "${WIKI_DIR}" ]]; then
  echo "Error: Directory ${WIKI_DIR} does not exist." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d -t osiris-wiki-sync-XXXXXX)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "==> Klonování GitHub Wiki: ${REMOTE_URL}"
if ! git clone "${REMOTE_URL}" "${TMP_DIR}"; then
  echo "Upozornění: Klonování selhalo. Pokud jste Wiki na GitHubu ještě neinicializovali," >&2
  echo "otevřete záložku Wiki na GitHubu a vytvořte první stránku pro inicializaci repozitáře." >&2
  exit 1
fi

echo "==> Kopírování obsahu z ${WIKI_DIR} do Wiki repozitáře..."
cp -r "${WIKI_DIR}"/* "${TMP_DIR}/"

cd "${TMP_DIR}"
git add .

if git diff --staged --quiet; then
  echo "==> Žádné změny k odeslání. Wiki je již aktuální."
  exit 0
fi

echo "==> Vytváření commitu a odesílání do GitHub Wiki..."
git commit -m "docs(wiki): synchronizace manuálu grafického designu [skip ci]"

# Detekce hlavní větve (master nebo main)
CURRENT_BRANCH="$(git branch --show-current 2>/dev/null || echo "master")"
git push origin "${CURRENT_BRANCH}"
echo "==> Synchronizace Wiki byla úspěšně dokončena."

