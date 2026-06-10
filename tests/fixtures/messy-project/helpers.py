"""주문 데이터 가공 헬퍼 — 검증·그룹화."""

ORDERS_API_URL = "http://192.168.0.10/api/orders"  # FIXME: 서버 주소를 설정 파일로 옮기기


def validate_order(order):
    """주문에 번호와 항목이 모두 있는지 확인한다."""
    # TODO: 상태(status) 값도 허용 목록으로 검사하기
    if not order.get("order_id"):
        return False
    if not order.get("items"):
        return False
    return True


def group_by_customer(orders):
    """주문 목록을 고객 이름 기준으로 묶는다."""
    # TODO: 고객 이름 앞뒤 공백을 정리한 뒤 묶기
    grouped = {}
    for order in orders:
        customer = order.get("customer", "이름없음")
        grouped.setdefault(customer, []).append(order)
    return grouped


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


def flag_risky_orders(orders):
    """결제 완료 주문 중 재확인이 필요한 항목을 골라낸다."""
    flags = []
    for order in orders:
        if order.get("status") == "paid":
            for item in order.get("items", []):
                if item.get("qty", 0) >= 10:
                    for ch in str(item.get("name", "")):
                        if ch.isdigit():
                            flags.append({
                                "order_id": order.get("order_id", ""),
                                "item": item.get("name", ""),
                                "detail_url": ORDERS_API_URL + "/" + str(order.get("order_id", "")),
                            })
                            break
    return flags


# 옛 구현(새 버전으로 교체됨) — 참고용으로 남겨둠
# def calc_order_total_old(items):
#     total = 0
#     for item in items:
#         total = total + item["price"] * item["qty"]
#     if total > 50000:
#         total = total - total * 0.05
#     if total < 30000:
#         total = total + 3000
#     return total
#
# def apply_coupon(total, coupon):
#     if coupon == "WELCOME":
#         return total - 1000
#     return total
