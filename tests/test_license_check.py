import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../actions/syft/src"))
from license_check import (
    Violation,
    check_licenses,
    extract_packages_spdx,
    extract_packages_syft,
    parse_list,
    _split_spdx_expression,
)


# --- parse_list ---

def test_parse_list_basic():
    assert parse_list("MIT,Apache-2.0") == {"MIT", "APACHE-2.0"}

def test_parse_list_whitespace():
    assert parse_list("MIT, Apache-2.0 , BSD-3-Clause") == {"MIT", "APACHE-2.0", "BSD-3-CLAUSE"}

def test_parse_list_empty():
    assert parse_list("") == set()


# --- _split_spdx_expression ---

def test_split_simple():
    assert _split_spdx_expression("MIT") == ["MIT"]

def test_split_and_expression():
    result = _split_spdx_expression("MIT AND Apache-2.0")
    assert "MIT" in result
    assert "Apache-2.0" in result
    assert "AND" not in result

def test_split_complex():
    result = _split_spdx_expression("(GPL-2.0-only OR MIT) AND Apache-2.0")
    assert "GPL-2.0-only" in result
    assert "MIT" in result
    assert "Apache-2.0" in result

def test_split_noassertion():
    assert _split_spdx_expression("NOASSERTION") == ["UNKNOWN"]

def test_split_empty():
    assert _split_spdx_expression("") == ["UNKNOWN"]


# --- extract_packages_spdx ---

SPDX_FIXTURE = {
    "packages": [
        {
            "name": "requests",
            "versionInfo": "2.31.0",
            "licenseDeclared": "Apache-2.0",
            "licenseConcluded": "Apache-2.0",
        },
        {
            "name": "some-gpl-lib",
            "versionInfo": "1.0.0",
            "licenseDeclared": "GPL-2.0-only",
            "licenseConcluded": "NOASSERTION",
        },
    ]
}

def test_extract_spdx_uses_concluded():
    pkgs = extract_packages_spdx(SPDX_FIXTURE)
    requests_pkg = next(p for p in pkgs if p[0] == "requests")
    assert "Apache-2.0" in requests_pkg[2]

def test_extract_spdx_falls_back_to_declared():
    pkgs = extract_packages_spdx(SPDX_FIXTURE)
    gpl_pkg = next(p for p in pkgs if p[0] == "some-gpl-lib")
    assert "GPL-2.0-only" in gpl_pkg[2]


# --- extract_packages_syft ---

SYFT_FIXTURE = {
    "artifacts": [
        {
            "name": "flask",
            "version": "3.0.0",
            "licenses": [{"value": "BSD-3-Clause"}],
        },
        {
            "name": "no-license-pkg",
            "version": "0.1.0",
            "licenses": [],
        },
    ]
}

def test_extract_syft_basic():
    pkgs = extract_packages_syft(SYFT_FIXTURE)
    flask = next(p for p in pkgs if p[0] == "flask")
    assert flask[2] == ["BSD-3-Clause"]

def test_extract_syft_no_licenses():
    pkgs = extract_packages_syft(SYFT_FIXTURE)
    no_lic = next(p for p in pkgs if p[0] == "no-license-pkg")
    assert no_lic[2] == []


# --- check_licenses ---

PACKAGES = [
    ("requests", "2.31.0", ["Apache-2.0"]),
    ("gpl-lib", "1.0.0", ["GPL-2.0-only"]),
    ("mit-lib", "2.0.0", ["MIT"]),
    ("unknown-lib", "0.1.0", ["UNKNOWN"]),
]

def test_deny_catches_blocked_license():
    violations = check_licenses(PACKAGES, allow=set(), deny={"GPL-2.0-ONLY"})
    assert len(violations) == 1
    assert violations[0].package == "gpl-lib"
    assert violations[0].reason == "denied license"

def test_allowlist_blocks_unlisted():
    violations = check_licenses(PACKAGES, allow={"MIT", "APACHE-2.0"}, deny=set())
    names = [v.package for v in violations]
    assert "gpl-lib" in names
    assert "requests" not in names
    assert "mit-lib" not in names

def test_allowlist_skips_unknown_license():
    violations = check_licenses(PACKAGES, allow={"MIT", "APACHE-2.0"}, deny=set())
    names = [v.package for v in violations]
    assert "unknown-lib" not in names

def test_no_policy_no_violations():
    violations = check_licenses(PACKAGES, allow=set(), deny=set())
    assert violations == []

def test_deny_and_allow_independent():
    # deny takes precedence; allow doesn't protect a denied license
    violations = check_licenses(
        [("pkg", "1.0", ["GPL-2.0-only"])],
        allow={"GPL-2.0-ONLY"},
        deny={"GPL-2.0-ONLY"},
    )
    assert len(violations) == 1
    assert violations[0].reason == "denied license"
