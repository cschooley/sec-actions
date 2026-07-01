# grype

Scans for CVEs using [Grype](https://github.com/anchore/grype) and emits a SARIF report.

Accepts a directory, container image, or a Syft-generated SBOM as input. Pair with the [syft](../syft/) action to scan your exact dependency graph rather than a filesystem heuristic.

## Inputs

| Input | Default | Description |
|---|---|---|
| `target` | `dir:.` | What to scan: directory (`dir:.`), container image (`name:tag`), or path to a Syft SBOM file |
| `output_file` | `grype.sarif` | Path to write the SARIF output |
| `severity_cutoff` | `medium` | Minimum severity to report: `negligible`, `low`, `medium`, `high`, `critical` |
| `fail_on_findings` | `true` | Exit 1 if vulnerabilities at or above `severity_cutoff` are found. Set `false` for audit mode. |
| `version` | latest | Grype version to pin (e.g. `0.88.0`) |

## Usage

### Scan a directory (standalone)

```yaml
- uses: cschooley/sec-actions/actions/grype@main
  with:
    fail_on_findings: 'false'
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: grype-sarif
    path: grype.sarif
```

### Scan a Syft SBOM (recommended for accuracy)

```yaml
- uses: cschooley/sec-actions/actions/syft@main
  with:
    output_file: sbom.spdx.json

- uses: cschooley/sec-actions/actions/grype@main
  with:
    target: sbom.spdx.json
    fail_on_findings: 'false'
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: grype-sarif
    path: grype.sarif
```
