"""Measure the deterministic, local quality gates used by Project Doctor.

This deliberately does not measure Claude's diagnosis time: model/network latency is
outside the repository's control.  It guards the local scripts that validate a
report before it is shared.
"""
from __future__ import annotations

import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_SECONDS = 10.0
RUNS = 3


@dataclass(frozen=True)
class Result:
    name: str
    returncode: int
    seconds: float


def median_seconds(samples: list[float]) -> float:
    """Return a stable middle value so one noisy machine sample does not mislead."""
    return float(statistics.median(samples))


def run_check(name: str, command: list[str]) -> Result:
    started = time.perf_counter()
    # Child scripts may emit UTF-8 Korean text while Windows uses a different
    # console encoding. Their output is not part of the measurement.
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return Result(name, completed.returncode, time.perf_counter() - started)


def failures(results: list[Result]) -> list[str]:
    problems: list[str] = []
    for result in results:
        if result.returncode != 0:
            problems.append(f"{result.name} exited with code {result.returncode}")
        elif result.seconds > MAX_SECONDS:
            problems.append(
                f"{result.name} exceeded {MAX_SECONDS:.1f}s ({result.seconds:.2f}s)"
            )
    return problems


def main() -> int:
    checks = (
        ("scoring regression", [sys.executable, "tests/check_scoring_regression.py"]),
        ("link validation", [sys.executable, "tests/check_links.py"]),
        (
            "golden report validation",
            [
                sys.executable,
                "tests/run_checks.py",
                "tests/golden/checkup-report.md",
                "tests/fixtures/messy-project/EXPECTED.md",
            ],
        ),
    )
    results: list[Result] = []
    for name, command in checks:
        samples = [run_check(name, command) for _ in range(RUNS)]
        result = Result(
            name,
            next((sample.returncode for sample in samples if sample.returncode), 0),
            median_seconds([sample.seconds for sample in samples]),
        )
        results.append(result)
        print(f"{name}: median {result.seconds:.2f}s ({RUNS} runs)")

    problems = failures(results)
    if problems:
        print("Local performance guard failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"Local performance guard passed: each check completed within {MAX_SECONDS:.1f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
