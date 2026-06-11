// 주문 표시용 보조 함수 모음 (웹 화면에서 사용 예정)

function formatOrderId(orderId) {
  return `ORD-${String(orderId).padStart(6, "0")}`;
}

function statusLabel(status) {
  const labels = {
    pending: "대기",
    paid: "결제완료",
    shipped: "배송중",
    done: "완료",
  };
  return labels[status] || "알수없음";
}

function summarizeItems(items) {
  if (!items || items.length === 0) {
    return "항목 없음";
  }
  const first = items[0].name;
  return items.length === 1 ? first : `${first} 외 ${items.length - 1}건`;
}

module.exports = { formatOrderId, statusLabel, summarizeItems };
