"""품목별 임계값 규칙.

settings.json의 default_threshold보다 이 파일의 품목별 규칙이 우선한다.
숫자를 잘 모르고 바꾸면 알림이 과다하게 울리거나, 반대로 부족을 놓친다.
(에러는 나지 않고 조용히 잘못 동작하므로 특히 주의)
"""

# 품목별 최소 재고 기준 — 현재 수량이 이 숫자 "미만"이면 부족으로 판정
ITEM_THRESHOLDS = {
    "A4용지": 20,  # 소모가 빨라 기본값(10)보다 높게 잡음
    "토너": 5,     # 고가 품목이라 적게 쌓아둠
    "볼펜": 30,
}


def get_threshold(item_name, default_threshold):
    """품목별 규칙이 있으면 그 값을, 없으면 기본값을 그대로 돌려준다."""
    return ITEM_THRESHOLDS.get(item_name, default_threshold)
