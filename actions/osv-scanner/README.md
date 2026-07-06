# OSV-Scanner Dependency Scanner

Scans dependencies for known vulnerabilities using [OSV-Scanner](https://github.com/google/osv-scanner) against the [OSV database](https://osv.dev) (GitHub Advisories, NVD, PyPI, npm, Go, Maven, RubyGems, and more).

Reads lockfiles directly (`package-lock.json`, `Pipfile.lock`, `go.sum`, `Cargo.lock`, etc.) — no image build or filesystem heuristic required. Can also scan a Syft-generated SBOM, making this composable with the [syft](../syft/) action.

## Usage

```yaml
- uses: ./actions/osv-scanner
  with:
    target: '.'
    output_file: osv-results.json
    fail_on_findings: 'true'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `target` | No | `.` | Directory, lockfile, or SBOM file to scan |
| `output_file` | No | `osv-results.json` | Path to write scan output |
| `format` | No | `json` | Output format: `json`, `sarif`, `table`, `markdown`, `cyclonedx-1-5`, `spdx-2-3`, etc. |
| `config` | No | | Path to an `osv-scanner.toml` config file |
| `fail_on_findings` | No | `true` | Fail the job on findings; set `false` for audit mode |
| `version` | No | latest | OSV-Scanner version to install |

## Outputs

Scan results at `output_file`, in whichever `format` was requested.

## Exit codes

OSV-Scanner exits `0` clean, `1` on findings, anything else is treated as an error and always fails the job regardless of `fail_on_findings`.

## SARIF output (VS Code / Code Scanning integration)

Set `format: sarif` to plug into the same [SARIF Viewer workflow](../../README.md#vs-code-integration-non-ghas-repos) used by the other actions in this repo:

```yaml
- uses: ./actions/osv-scanner
  with:
    format: sarif
    output_file: osv-results.sarif
    fail_on_findings: 'false'
```

## Scanning a Syft SBOM

```yaml
- uses: ./actions/syft
  with:
    output_file: sbom.spdx.json

- uses: ./actions/osv-scanner
  with:
    target: sbom.spdx.json
    fail_on_findings: 'false'
```

## Suppressing findings

Drop an `osv-scanner.toml` at the repo root (or pass a custom path via `config`) to ignore specific vulnerability IDs or packages. See the [OSV-Scanner configuration reference](https://google.github.io/osv-scanner/configuration/).
