# Semgrep SAST Scanner

Runs [Semgrep](https://semgrep.dev) static analysis and produces a SARIF report. Supports any Semgrep ruleset — the default `auto` config selects rules based on detected languages.

## Usage

```yaml
- uses: ./actions/semgrep
  with:
    config: 'auto'
    output_file: semgrep.sarif
    fail_on_findings: 'true'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `config` | No | `auto` | Ruleset: `auto`, `p/security-audit`, `p/owasp-top-ten`, or path to local rules |
| `target` | No | `.` | Directory or file to scan |
| `output_file` | No | `semgrep.sarif` | SARIF output path |
| `fail_on_findings` | No | `true` | Fail the job on findings; set `false` for audit mode |
| `extra_args` | No | | Additional CLI args (e.g. `--exclude tests/ --severity ERROR`) |

## Outputs

SARIF file at `output_file`.

## Exit codes

Semgrep distinguishes findings (exit 1) from errors (exit 2/3). This action fails on errors regardless of `fail_on_findings`, so misconfigured rulesets don't silently pass.

## Choosing a config

- `auto` — language-aware, no setup required, good default
- `p/security-audit` — broader coverage, more noise
- `p/owasp-top-ten` — focused on OWASP Top 10 categories
- A path like `./rules/` — use your own rule files

See the [Semgrep Registry](https://semgrep.dev/r) for available packs.
