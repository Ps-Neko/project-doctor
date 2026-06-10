"""주문 관리 미니 도구 — 메인 실행 파일.

주문 CSV를 읽어 고객별 주문 합계를 집계하고 요약을 출력한다.
"""

import csv

from helpers import flag_risky_orders, group_by_customer, validate_order
from utils import format_currency, send_summary

# TODO: 데이터 파일 경로를 config.json으로 옮기기
DATA_FILE = r"C:\Users\kim\Desktop\orders\data.csv"


def calc_order_total(items):
    """주문 항목 목록의 결제 합계를 계산한다 (할인·배송비 포함)."""
    subtotal = 0
    for item in items:
        price = item.get("price", 0)
        qty = item.get("qty", 0)
        subtotal += price * qty
    if subtotal >= 50000:
        discount = subtotal * 0.05
    else:
        discount = 0
    shipping = 0 if subtotal >= 30000 else 3000
    total = subtotal - discount + shipping
    return int(total)


def load_orders():
    """주문 CSV 파일을 읽어 행 목록을 돌려준다."""
    # FIXME: 파일이 없을 때 더 친절한 안내 메시지 출력하기
    orders = []
    with open(DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(row)
    return orders


def process_orders():
    """주문 데이터를 읽어 변환·검증·집계·출력까지 한 번에 처리한다."""
    rows = load_orders()
    if not rows:
        print("주문 데이터가 없습니다.")
        return

    # 1단계: CSV 행을 주문 구조로 변환
    orders = []
    for row in rows:
        items = []
        names = row.get("item_names", "").split("|")
        prices = row.get("item_prices", "").split("|")
        qtys = row.get("item_qtys", "").split("|")
        for name, price, qty in zip(names, prices, qtys):
            if not name:
                continue
            try:
                items.append({
                    "name": name,
                    "price": int(price),
                    "qty": int(qty),
                })
            except ValueError:
                print(f"가격/수량 형식 오류로 건너뜀: {name}")
        orders.append({
            "order_id": row.get("order_id", ""),
            "customer": row.get("customer", "이름없음"),
            "status": row.get("status", "pending"),
            "items": items,
        })

    # 2단계: 유효성 검사
    valid_orders = []
    skipped = 0
    for order in orders:
        if validate_order(order):
            valid_orders.append(order)
        else:
            skipped += 1

    # 3단계: 고객별 그룹화 및 합계 계산
    grouped = group_by_customer(valid_orders)
    report_lines = []
    grand_total = 0
    for customer, customer_orders in grouped.items():
        customer_total = 0
        for order in customer_orders:
            total = calc_order_total(order["items"])
            customer_total += total
        grand_total += customer_total
        report_lines.append(
            f"{customer}: {format_currency(customer_total)}"
        )

    # 4단계: 요약 출력 및 전송
    print("=" * 40)
    print("고객별 주문 합계")
    print("=" * 40)
    for line in report_lines:
        print(line)
    print("-" * 40)
    print(f"전체 합계: {format_currency(grand_total)}")
    print(f"처리 {len(valid_orders)}건 / 제외 {skipped}건")
    risky = flag_risky_orders(valid_orders)
    if risky:
        print(f"재확인 필요 주문 항목: {len(risky)}건")
    send_summary(grand_total, len(valid_orders))


# TODO: 주문 상태별(대기/결제/배송) 건수 요약 출력 추가
if __name__ == "__main__":
    process_orders()
