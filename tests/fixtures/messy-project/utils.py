"""주문 도구 공용 유틸리티 — 설정 로드·통화 표기·요약 전송."""

import json
import os

import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    """config.json에서 설정값을 읽어온다."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


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


def legacy_discount(subtotal, member_grade):
    """회원 등급별 추가 할인액을 계산한다 (구버전 정책)."""
    if member_grade == "gold":
        return int(subtotal * 0.1)
    if member_grade == "silver":
        return int(subtotal * 0.07)
    if member_grade == "bronze":
        return int(subtotal * 0.03)
    return 0


def format_currency(amount):
    """금액을 '1,234원' 형태 문자열로 바꾼다."""
    return f"{amount:,}원"


def send_summary(grand_total, order_count):
    """집계 결과를 설정 파일에 적힌 웹훅 주소로 전송한다."""
    config = load_config()
    payload = {"total": grand_total, "count": order_count}
    try:
        response = requests.post(config["webhook_url"], json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"요약 전송 실패: {exc}")
