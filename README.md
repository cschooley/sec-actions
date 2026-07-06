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
| [grype](actions/grype/) | [Grype](https://github.com/anchore/grype) | CVE / vulnerability scanning |

## Design

- **No platform lock-in.** No calls to proprietary security APIs. Results land as workflow artifacts (SARIF, SPDX JSON, CycloneDX JSON) that any SARIF-aware consumer can read.
- **Composite actions.** No Docker images — tools are installed at runtime from their upstream release channels. Fast, auditable, version-pinnable.
- **Observe before you gate.** Every action has `fail_on_findings: false` for a non-blocking audit pass while onboarding.
- **SARIF output.** gitleaks, semgrep, and grype produce SARIF. syft produces SBOM (feed it to grype for accurate CVE results).

## Quick start

Scan a repo on every push. Actions below are pinned to commit SHAs (with the tag/branch noted in a comment) rather than `@v4` or `@main` — mutable refs can be repointed, so pinning is the safer default for anything running in CI. Update the pins with [Dependabot](https://docs.github.com/code-security/dependabot/dependabot-version-updates) or by hand once a tagged release of this repo exists.

```yaml
name: Security

on: [push, pull_request]

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: cschooley/sec-actions/actions/gitleaks@2e7265858d4328b9eac6001532e7011e8be518bf # main, 2026-07-06
        with:
          fail_on_findings: 'true'
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        if: always()
        with:
          name: gitleaks-sarif
          path: gitleaks.sarif

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: cschooley/sec-actions/actions/semgrep@2e7265858d4328b9eac6001532e7011e8be518bf # main, 2026-07-06
        with:
          config: 'auto'
          fail_on_findings: 'false'
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        if: always()
        with:
          name: semgrep-sarif
          path: semgrep.sarif

  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: cschooley/sec-actions/actions/syft@2e7265858d4328b9eac6001532e7011e8be518bf # main, 2026-07-06
        with:
          check_licenses: 'true'
          deny_licenses: 'GPL-2.0-only,GPL-3.0-only,AGPL-3.0-only'
          fail_on_findings: 'false'
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        if: always()
        with:
          name: sbom
          path: sbom.spdx.json

  vuln:
    runs-on: ubuntu-latest
    needs: sbom
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4
        with:
          name: sbom
      - uses: cschooley/sec-actions/actions/grype@2e7265858d4328b9eac6001532e7011e8be518bf # main, 2026-07-06
        with:
          target: sbom.spdx.json
          severity_cutoff: 'medium'
          fail_on_findings: 'false'
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        if: always()
        with:
          name: grype-sarif
          path: grype.sarif
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
7. Add this to your `.vscode/settings.json` so the extension auto-loads findings on startup:
   ```json
   {
     "sarif-viewer.rootpaths": [".sarif"]
   }
   ```
   > `.vscode/settings.json` should be gitignored so this stays local to each developer's machine.

After setup, `git pull` automatically fetches the latest scan artifacts into `.sarif/` and the SARIF Viewer shows findings inline. Run manually anytime with `bash scripts/fetch-sarif.sh` — also use this if `git pull` reports "Already up to date" (the hook only fires when commits are merged).

> **Note:** `git config core.hooksPath` is a local setting — it must be run once in each working copy (clone or worktree). It does not travel with the repo.

## Triaging findings in VS Code

Once the SARIF Viewer extension is installed and `.sarif/` files are present, open the SARIF panel from the Activity Bar. It has three tabs:

- **Locations** — every individual finding, with file path and line number. Click any row to jump directly to the affected code.
- **Rules** — findings grouped by rule ID. Useful for understanding how many instances of the same issue exist and deciding whether to fix or suppress the whole rule.
- **Logs** — the raw SARIF files (gitleaks.sarif, semgrep.sarif, grype.sarif). Toggle individual scanners on/off from here.

### Triage workflow

1. **Fetch latest results**: `bash scripts/fetch-sarif.sh` (or wait for the post-merge hook after `git pull`)
2. **Open the Locations tab** — start with `error` severity (red), then `warning` (yellow)
3. **Click a finding** — VS Code jumps to the exact file and line
4. **Fix, suppress, or document:**
   - *Fix it* — update the code or dependency and push; the next scan will clear it
   - *Suppress a known false positive or dev-only issue* — add an ignore rule to `.grype.yaml` (for CVEs) or a `# nosemgrep: rule-id` comment inline (for semgrep)
   - *Defer it* — leave it in audit mode and track it in your issue tracker
5. **Re-fetch** after the next CI run to confirm the finding is gone

### Ignoring a CVE in Grype

Create `.grype.yaml` in your repo root:

```yaml
ignore:
  - vulnerability: GHSA-6w46-j5rx-g56g
    package:
      name: pytest
    reason: "dev-only test dependency, never installed in production"
```

Grype picks this up automatically — no workflow changes needed.

### Ignoring a Semgrep rule inline

```python
result = db.execute(query)  # nosemgrep: python.lang.security.audit.formatted-sql-query
```

Or suppress an entire rule for the repo by adding it to your `semgrep.yml` config.

## Roadmap

- OSV-Scanner action (dependency/SCA scanning)
- TruffleHog action (alternative secret scanner with historical commit scanning)
- DefectDojo upload helper
