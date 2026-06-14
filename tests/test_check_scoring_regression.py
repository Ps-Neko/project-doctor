"""check_scoring_regression (BL-15 채점 회귀 가드) 테스트.

채점기(compare_report)가 깨지지 않았는지를 보는 가드 — 각 픽스처 정답지의 '## 심은 문제'
ID를 본뜬 합성 보고서가 100%·오탐0(통과)을 내야 한다. '## 심은 문제'가 없는 정답지
(intro/pivot 스타일)는 채점 대상에서 빠진다.
"""
import check_scoring_regression as csr


def test_regression_guard_passes() -> None:
    # 채점 가능한 모든 픽스처 정답지가 compare_report로 100%·오탐0이면 종료 0.
    assert csr.main() == 0
