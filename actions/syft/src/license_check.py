#!/usr/bin/env python3
"""
License compliance check against a syft-generated SBOM.
Supports spdx-json and syft-json formats.
"""
import json
import os
import sys
from dataclasses import dataclass


@dataclass
class Violation:
    package: str
    version: str
    license: str
    reason: str


def parse_list(value: str) -> set[str]:
    return {v.strip().upper() for v in value.split(",") if v.strip()}


def extract_packages_spdx(data: dict) -> list[tuple[str, str, list[str]]]:
    """Return (name, version, [license_ids]) tuples from an SPDX 2.x JSON SBOM."""
    packages = []
    for pkg in data.get("packages", []):
        name = pkg.get("name", "unknown")
        version = pkg.get("versionInfo", "")
        declared = pkg.get("licenseDeclared", "NOASSERTION")
        concluded = pkg.get("licenseConcluded", "NOASSERTION")

        raw = concluded if concluded not in ("NOASSERTION", "NONE", "") else declared
        licenses = _split_spdx_expression(raw)
        packages.append((name, version, licenses))
    return packages


def extract_packages_syft(data: dict) -> list[tuple[str, str, list[str]]]:
    """Return (name, version, [license_ids]) tuples from a syft-json SBOM."""
    packages = []
    for pkg in data.get("artifacts", []):
        name = pkg.get("name", "unknown")
        version = pkg.get("version", "")
        licenses = [lic.get("value", "") for lic in pkg.get("licenses", [])]
        packages.append((name, version, licenses))
    return packages


def _split_spdx_expression(expr: str) -> list[str]:
    """Split a simple SPDX license expression into individual IDs, ignoring operators."""
    if not expr or expr in ("NOASSERTION", "NONE"):
        return ["UNKNOWN"]
    tokens = expr.replace("(", " ").replace(")", " ").split()
    return [t for t in tokens if t.upper() not in ("AND", "OR", "WITH")]


def check_licenses(
    packages: list[tuple[str, str, list[str]]],
    allow: set[str],
    deny: set[str],
) -> list[Violation]:
    violations = []
    for name, version, licenses in packages:
        for lic in licenses:
            lid = lic.upper()
            if deny and lid in deny:
                violations.append(Violation(name, version, lic, "denied license"))
            elif allow and lid not in allow and lid != "UNKNOWN":
                violations.append(Violation(name, version, lic, "not in allow list"))
    return violations


def main() -> None:
    sbom_file = os.environ["INPUT_SBOM_FILE"]
    sbom_format = os.environ["INPUT_SBOM_FORMAT"]
    allow_licenses = parse_list(os.environ.get("INPUT_ALLOW_LICENSES", ""))
    deny_licenses = parse_list(os.environ.get("INPUT_DENY_LICENSES", ""))
    fail_on_findings = os.environ.get("INPUT_FAIL_ON_FINDINGS", "true").strip().lower() == "true"

    if not allow_licenses and not deny_licenses:
        print("No license policy configured (allow_licenses and deny_licenses are both empty). Skipping.")
        return

    try:
        with open(sbom_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"::error::SBOM file not found: {sbom_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse SBOM: {e}", file=sys.stderr)
        sys.exit(1)

    if sbom_format == "spdx-json":
        packages = extract_packages_spdx(data)
    elif sbom_format == "syft-json":
        packages = extract_packages_syft(data)
    else:
        print(f"::error::License check only supports spdx-json and syft-json formats, got: {sbom_format}", file=sys.stderr)
        sys.exit(1)

    violations = check_licenses(packages, allow_licenses, deny_licenses)

    if not violations:
        print(f"License check passed. {len(packages)} package(s) reviewed.")
        return

    print(f"::warning::License violations found ({len(violations)}):")
    for v in violations:
        print(f"  {v.package}@{v.version}: {v.license} ({v.reason})")

    if fail_on_findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
