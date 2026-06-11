// 고객 알림 발송 도구 — 웹 대시보드용 설정 (실험 단계)
const GH_TOKEN = "ghp_EXAMPLEFAKE0TOKEN0EXAMPLEFAKE0TOKEN0";

const config = {
  apiBaseUrl: "https://api.example.com/v1",
  maxRetry: 3,
  batchSize: 50,
  locale: "ko-KR",
};

module.exports = { config, GH_TOKEN };
