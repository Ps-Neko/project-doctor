"""재고 알림 미니 도구 — 엔트리포인트.

data/stock.csv 를 읽어 임계값 미만인 품목을 콘솔에 출력한다.
실행: python inventory.py  (표준 라이브러리만 사용, 별도 설치 불필요)
"""

import csv
import json
from pathlib import Path

import notify  # noqa: F401  # TODO: 부족 품목 알림 전송 연결 예정 (notify.py는 아직 스텁)
import stock_rules

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
REQUIRED_SETTING_KEYS = ("default_threshold", "csv_path", "csv_encoding")


def load_settings(path):
    """settings.json을 읽어 dict로 돌려준다. 형식이 깨지면 즉시 중단한다."""
    try:
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"[오류] 설정 파일이 없습니다: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[오류] settings.json 형식이 깨졌습니다: {exc}")

    missing = [key for key in REQUIRED_SETTING_KEYS if key not in settings]
    if missing:
        raise SystemExit(f"[오류] settings.json에 필수 키가 없습니다: {', '.join(missing)}")
    if not isinstance(settings["default_threshold"], int) or settings["default_threshold"] < 0:
        raise SystemExit("[오류] settings.json의 default_threshold는 0 이상의 정수여야 합니다")
    return settings


def parse_row(row, line_no):
    """CSV 한 행을 검증해 (품목, 수량, 단위) 튜플로 돌려준다."""
    item = (row.get("item") or "").strip()
    quantity_text = (row.get("quantity") or "").strip()
    unit = (row.get("unit") or "").strip()

    if not item:
        raise SystemExit(f"[오류] stock.csv {line_no}행: item이 비어 있습니다")
    try:
        quantity = int(quantity_text)
    except ValueError:
        raise SystemExit(f"[오류] stock.csv {line_no}행: quantity가 숫자가 아닙니다: {quantity_text!r}")
    if quantity < 0:
        raise SystemExit(f"[오류] stock.csv {line_no}행: quantity는 0 이상이어야 합니다")
    return (item, quantity, unit)


def load_stock(csv_path, encoding):
    """재고 CSV 전체를 (품목, 수량, 단위) 튜플 목록으로 돌려준다."""
    try:
        with open(csv_path, encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            return [parse_row(row, line_no) for line_no, row in enumerate(reader, start=2)]
    except FileNotFoundError:
        raise SystemExit(f"[오류] 재고 파일이 없습니다: {csv_path}")


def find_low_stock(stock_rows, default_threshold):
    """임계값 미만 품목만 골라 새 목록으로 돌려준다 (원본은 바꾸지 않는다)."""
    return [
        (item, quantity, unit, stock_rules.get_threshold(item, default_threshold))
        for item, quantity, unit in stock_rows
        if quantity < stock_rules.get_threshold(item, default_threshold)
    ]


def print_report(low_items, total_count):
    """점검 결과를 콘솔에 출력한다."""
    print(f"재고 점검 결과: 전체 {total_count}개 품목 중 {len(low_items)}개가 임계값 미만입니다.")
    if not low_items:
        print("부족한 품목이 없습니다.")
        return
    for item, quantity, unit, threshold in low_items:
        print(f"  - [부족] {item}: 현재 {quantity}{unit} (기준 {threshold}{unit} 미만)")
    # TODO: notify.send_email_alert(low_items) 연결 — notify.py 구현이 끝나면 주석 해제


def main():
    settings = load_settings(SETTINGS_PATH)
    csv_path = BASE_DIR / settings["csv_path"]
    stock_rows = load_stock(csv_path, settings["csv_encoding"])
    low_items = find_low_stock(stock_rows, settings["default_threshold"])
    print_report(low_items, len(stock_rows))


if __name__ == "__main__":
    main()
