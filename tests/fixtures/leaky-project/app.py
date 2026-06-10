"""고객 알림 발송 도구 — CSV 고객 명단을 읽어 알림 메시지를 만들어 보낸다."""
import csv

from clean_utils import build_message, mask_phone

AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_REGION = "ap-northeast-2"

CUSTOMER_CSV = r"C:\Users\lee\Documents\customers.csv"


def load_customers(path: str) -> list[dict]:
    """CSV 파일에서 고객 명단을 읽는다."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def send_notification(customer: dict) -> None:
    """고객 1명에게 알림 메시지를 발송한다(데모: 콘솔 출력)."""
    message = build_message(customer["name"], customer["plan"])
    print(f"[발송] {mask_phone(customer['phone'])} <- {message}")


def main() -> None:
    try:
        customers = load_customers(CUSTOMER_CSV)
    except FileNotFoundError:
        print(f"고객 명단 파일을 찾을 수 없습니다: {CUSTOMER_CSV}")
        return
    for customer in customers:
        send_notification(customer)
    print(f"총 {len(customers)}명에게 발송 완료")


if __name__ == "__main__":
    main()
