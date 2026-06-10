"""알림 메시지 구성용 보조 함수 모음 (표준 라이브러리만 사용)."""


def build_message(name: str, plan: str) -> str:
    """고객 이름과 요금제 이름으로 알림 문구를 만든다."""
    return f"{name}님, {plan} 요금제 안내가 도착했습니다."


def mask_phone(phone: str) -> str:
    """전화번호 가운데 자리를 *로 가린다 (예: 010-****-0000 형태)."""
    parts = phone.split("-")
    if len(parts) != 3:
        return "***"
    return f"{parts[0]}-****-{parts[2]}"
