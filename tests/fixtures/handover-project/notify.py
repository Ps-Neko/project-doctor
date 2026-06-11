"""알림 전송 모듈 — 미완성 스텁.

TODO: 임계값 미만 품목 목록을 이메일/메신저로 보내는 기능을 붙일 예정.
아직 어떤 함수도 inventory.py에서 호출되지 않는다 (import만 걸려 있음).
"""


def send_email_alert(low_items):
    """부족 품목 목록을 이메일로 전송한다 (미구현).

    TODO: SMTP 서버 주소·발신 계정을 settings.json에 추가한 뒤 구현
    """
    raise NotImplementedError("이메일 알림은 아직 구현되지 않았습니다")


def send_messenger_alert(low_items):
    """부족 품목 목록을 메신저 webhook으로 전송한다 (미구현).

    TODO: webhook URL을 어디에 둘지 결정한 뒤 구현
    """
    raise NotImplementedError("메신저 알림은 아직 구현되지 않았습니다")
