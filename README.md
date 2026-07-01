# sec-actions

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Reusable GitHub Actions for FOSS security gates. Each action runs a standalone FOSS tool, emits a SARIF file or SBOM artifact, and works on any GitHub Actions runner (and reasonably on Forgejo).

Licensed under [AGPL-3.0](LICENSE). Free to use and modify; if you run this as a network service you must make your modifications available under the same terms.

## Actions

| Action | Tool | Gate |
|---|---|---|
| [gitleaks](actions/gitleaks/) | [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning |
| [semgrep](actions/semgrep/) | [Semgrep OSS](https://semgrep.dev) | SAST / code analysis |
| [syft](actions/syft/) | [Syft](https://github.com/anchore/syft) | SBOM generation + license compliance |

## Design

- **No platform lock-in.** No calls to proprietary security APIs. Results land as workflow artifacts (SARIF, SPDX JSON, CycloneDX JSON) that any SARIF-aware consumer can read.
- **Composite actions.** No Docker images — tools are installed at runtime from their upstream release channels. Fast, auditable, version-pinnable.
- **Observe before you gate.** Every action has `fail_on_findings: false` for a non-blocking audit pass while onboarding.
- **SARIF output.** gitleaks and semgrep produce SARIF. syft produces SBOM. Upload as artifacts or push to a dashboard like DefectDojo.

## Quick start

Scan a repo on every push:

```yaml
name: Security

on: [push, pull_request]

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cschooley/sec-actions/actions/gitleaks@main
        with:
          fail_on_findings: 'true'
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: gitleaks-sarif
          path: gitleaks.sarif

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cschooley/sec-actions/actions/semgrep@main
        with:
          config: 'auto'
          fail_on_findings: 'false'
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: semgrep-sarif
          path: semgrep.sarif

  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cschooley/sec-actions/actions/syft@main
        with:
          check_licenses: 'true'
          deny_licenses: 'GPL-2.0-only,GPL-3.0-only,AGPL-3.0-only'
          fail_on_findings: 'false'
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sbom
          path: sbom.spdx.json
```

See [examples/](examples/) for a complete workflow template, VS Code integration, a SARIF download script, and a post-merge git hook.

## VS Code integration (non-GHAS repos)

GitHub Code Scanning requires GHAS (paid feature for private repos). For private repos without GHAS, you can still get inline findings in VS Code:

1. Copy [examples/scripts/fetch-sarif.sh](examples/scripts/fetch-sarif.sh) into your repo's `scripts/` directory
2. Copy [examples/githooks/post-merge](examples/githooks/post-merge) into `.githooks/`
3. Copy [examples/vscode/](examples/vscode/) into `.vscode/`
4. Add `.sarif/` to your `.gitignore`
5. **One-time per working copy:** enable the local hook:
   ```bash
   git config core.hooksPath .githooks
   ```
6. Install the [SARIF Viewer](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer) extension (recommended in `.vscode/extensions.json`)

After setup, `git pull` automatically fetches the latest scan artifacts into `.sarif/` and the SARIF Viewer shows findings inline in the Problems panel (`Ctrl+Shift+M`). Run manually anytime with `bash scripts/fetch-sarif.sh`.

> **Note:** `git config core.hooksPath` is a local setting — it must be run once in each working copy (clone or worktree). It does not travel with the repo.

## Roadmap

- OSV-Scanner action (dependency/SCA scanning)
- TruffleHog action (alternative secret scanner with historical commit scanning)
- DefectDojo upload helper
