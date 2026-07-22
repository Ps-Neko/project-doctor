"""Local performance guard contract tests."""

import check_performance as performance


def test_median_uses_middle_value() -> None:
    assert performance.median_seconds([0.9, 0.1, 0.5]) == 0.5
    assert performance.median_seconds([0.1, 0.9]) == 0.5


def test_evaluate_marks_a_slow_check_as_failed() -> None:
    results = [
        performance.Result("fast", 0, 0.2),
        performance.Result("slow", 0, performance.MAX_SECONDS + 0.01),
    ]

    failures = performance.failures(results)

    assert failures == ["slow exceeded 10.0s (10.01s)"]


def test_evaluate_marks_a_command_failure_as_failed() -> None:
    results = [performance.Result("broken", 1, 0.1)]

    assert performance.failures(results) == ["broken exited with code 1"]
