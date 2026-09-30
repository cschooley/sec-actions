# trivy

Scans a container image for vulnerabilities using [Trivy](https://github.com/aquasecurity/trivy) and emits a SARIF report.

Focused on the image scan use case (CVEs in OS packages and language dependencies baked into a built image). For lockfile-based SCA on source, see [osv-scanner](../osv-scanner/). For a filesystem/SBOM-based CVE scan, see [grype](../grype/). Pairs well with [syft](../syft/): run Trivy for image CVEs, syft for SBOM and license compliance.

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `image` | Yes | | Container image to scan (e.g. `myapp:latest`). Must already be available to the runner (pulled or built earlier in the job). |
| `severity` | No | `HIGH,CRITICAL` | Comma-separated minimum severities to report: `UNKNOWN`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `output_file` | No | `trivy.sarif` | Path to write the SARIF output |
| `ignore_unfixed` | No | `false` | Exclude vulnerabilities with no available fix |
| `trivy_config` | No | | Path to a `trivy.yaml` config file |
| `fail_on_findings` | No | `true` | Exit 1 if vulnerabilities are found. Set `false` for audit mode. |
| `version` | No | latest | Trivy version to pin (e.g. `0.56.2`) |

## Usage

```yaml
- name: Build image
  run: docker build -t myapp:ci .

- uses: cschooley/sec-actions/actions/trivy@2e7265858d4328b9eac6001532e7011e8be518bf # main, 2026-07-06
  with:
    image: myapp:ci
    severity: 'HIGH,CRITICAL'
    fail_on_findings: 'false'
- uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
  if: always()
  with:
    name: trivy-sarif
    path: trivy.sarif
```

## Exit codes

Trivy is invoked with `--exit-code 1`, so it exits `0` clean, `1` on findings at or above `severity`, anything else is treated as an error and always fails the job regardless of `fail_on_findings`.

## Suppressing findings

Drop a `.trivyignore` at the repo root to ignore specific vulnerability IDs, or use a `trivy.yaml` config file (pass its path via `trivy_config`) for broader policy. See the [Trivy configuration reference](https://aquasecurity.github.io/trivy/latest/docs/configuration/).
