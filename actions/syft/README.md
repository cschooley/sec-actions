# Syft SBOM Generator

Generates a Software Bill of Materials using [Syft](https://github.com/anchore/syft) and optionally enforces a license policy against the output.

## Usage

**Generate SBOM only:**
```yaml
- uses: ./actions/syft
  with:
    target: 'dir:.'
    output_format: spdx-json
    output_file: sbom.spdx.json
```

**Generate SBOM + license gate:**
```yaml
- uses: ./actions/syft
  with:
    target: 'dir:.'
    output_file: sbom.spdx.json
    check_licenses: 'true'
    deny_licenses: 'GPL-2.0-only,GPL-3.0-only,AGPL-3.0-only'
    fail_on_findings: 'true'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `target` | No | `dir:.` | What to scan: `dir:.`, `name:image:tag`, or OCI archive path |
| `output_format` | No | `spdx-json` | `spdx-json`, `cyclonedx-json`, or `syft-json` |
| `output_file` | No | `sbom.spdx.json` | SBOM output path |
| `check_licenses` | No | `false` | Run license compliance check |
| `allow_licenses` | No | | SPDX IDs to allow (allowlist — anything else fails) |
| `deny_licenses` | No | | SPDX IDs that are always blocked |
| `fail_on_findings` | No | `true` | Fail the job on license violations |
| `version` | No | latest | Syft version to install |

`allow_licenses` and `deny_licenses` are mutually exclusive in intent: use one or the other. Both empty skips the license check even if `check_licenses: true`.

## License policy

Use SPDX identifiers: `MIT`, `Apache-2.0`, `GPL-2.0-only`, `LGPL-2.1-or-later`, etc. See the [SPDX license list](https://spdx.org/licenses/).

**Allowlist approach** (strict — anything not listed fails):
```yaml
allow_licenses: 'MIT,Apache-2.0,BSD-2-Clause,BSD-3-Clause,ISC'
```

**Denylist approach** (permissive — only block specific licenses):
```yaml
deny_licenses: 'GPL-2.0-only,GPL-3.0-only,AGPL-3.0-only,SSPL-1.0'
```

## Scanning container images

```yaml
- uses: ./actions/syft
  with:
    target: 'name:myapp:latest'
    output_format: cyclonedx-json
    output_file: sbom.cyclonedx.json
```

The image must be available to the runner (pulled or built earlier in the job).
