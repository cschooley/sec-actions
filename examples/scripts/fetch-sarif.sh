#!/usr/bin/env bash
# Downloads the latest completed security scan artifacts from GitHub Actions
# into .sarif/ so VS Code SARIF Viewer shows findings inline.
#
# Runs automatically via .githooks/post-merge after git pull.
# If already up to date (no new commits), run manually:
#   bash scripts/fetch-sarif.sh
#
# Requires: gh CLI authenticated (gh auth login)
set -euo pipefail

REPO="${SARIF_REPO:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
WORKFLOW="${SARIF_WORKFLOW:-security.yml}"
OUT_DIR="${SARIF_OUT_DIR:-.sarif}"

rm -rf "$OUT_DIR" && mkdir -p "$OUT_DIR"

RUN_ID=$(gh run list \
  --repo "$REPO" \
  --workflow "$WORKFLOW" \
  --limit 5 \
  --json databaseId,status \
  --jq '[.[] | select(.status == "completed")] | .[0].databaseId' 2>/dev/null || true)

if [ -z "$RUN_ID" ] || [ "$RUN_ID" = "null" ]; then
  echo "fetch-sarif: no completed security runs found, skipping." >&2
  exit 0
fi

echo "fetch-sarif: downloading artifacts from run $RUN_ID..."

gh run download "$RUN_ID" --repo "$REPO" --name gitleaks-sarif --dir "$OUT_DIR" 2>/dev/null && \
  echo "  ✓ gitleaks" || echo "  – gitleaks artifact not available"

gh run download "$RUN_ID" --repo "$REPO" --name semgrep-sarif  --dir "$OUT_DIR" 2>/dev/null && \
  echo "  ✓ semgrep"  || echo "  – semgrep artifact not available"

gh run download "$RUN_ID" --repo "$REPO" --name grype-sarif    --dir "$OUT_DIR" 2>/dev/null && \
  echo "  ✓ grype"    || echo "  – grype artifact not available"

echo "fetch-sarif: done. Open VS Code Problems panel to see findings."
