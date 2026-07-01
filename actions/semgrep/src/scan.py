#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys


def main() -> None:
    config = os.environ["INPUT_CONFIG"]
    target = os.environ["INPUT_TARGET"]
    output_file = os.environ["INPUT_OUTPUT_FILE"]
    fail_on_findings = os.environ["INPUT_FAIL_ON_FINDINGS"].strip().lower() == "true"
    extra_args = os.environ.get("INPUT_EXTRA_ARGS", "").strip()

    cmd = [
        "semgrep",
        "scan",
        "--config", config,
        "--sarif",
        "--output", output_file,
        "--quiet",
    ]

    if extra_args:
        cmd.extend(shlex.split(extra_args))

    cmd.append(target)

    result = subprocess.run(cmd)

    # semgrep exit codes: 0 = clean, 1 = findings, 2 = error, 3 = invalid config
    if result.returncode == 0:
        print("No findings.")
        return

    if result.returncode == 1:
        finding_count = _count_findings(output_file)
        print(f"::warning::Semgrep reported {finding_count} finding(s). Review {output_file}.")
        if fail_on_findings:
            sys.exit(1)
        return

    # returncode 2 or 3: configuration or runtime error — always fatal
    print(f"::error::Semgrep exited with error code {result.returncode}.", file=sys.stderr)
    sys.exit(result.returncode)


def _count_findings(sarif_path: str) -> int:
    try:
        with open(sarif_path) as f:
            data = json.load(f)
        return sum(
            len(run.get("results", []))
            for run in data.get("runs", [])
        )
    except Exception:
        return -1


if __name__ == "__main__":
    main()
