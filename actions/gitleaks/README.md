# Gitleaks Secret Scanner

Scans a repository for hardcoded secrets using [Gitleaks](https://github.com/gitleaks/gitleaks) and produces a SARIF report.

## Usage

```yaml
- uses: ./actions/gitleaks
  with:
    source: '.'
    output_file: gitleaks.sarif
    fail_on_findings: 'true'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `source` | No | `.` | Directory to scan |
| `config` | No | | Path to a `.gitleaks.toml` config file |
| `baseline_path` | No | | Baseline file to suppress known findings |
| `output_file` | No | `gitleaks.sarif` | SARIF output path |
| `fail_on_findings` | No | `true` | Fail the job on findings; set `false` for audit mode |
| `version` | No | latest | Gitleaks version to install |

## Outputs

SARIF file at `output_file`. Upload as a workflow artifact or feed to a SARIF-aware platform.

## Suppressing false positives

Create a baseline on an existing repo:

```bash
gitleaks detect --report-format json --report-path baseline.json
```

Commit `baseline.json` and pass it as `baseline_path`. Future runs only report new findings not in the baseline.

## Tuning rules

Drop a `.gitleaks.toml` at the repo root or pass a custom path via `config`. See the [Gitleaks config reference](https://github.com/gitleaks/gitleaks#configuration).
