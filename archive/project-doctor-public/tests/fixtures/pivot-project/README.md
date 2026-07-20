# 개인 블로그 생성기 (myblog)

마크다운으로 글을 쓰면 정적 블로그 HTML을 만들어 주는 작은 도구입니다.

## 무엇을 하나요

- `posts/`에 마크다운으로 글을 쓰면
- `python cli.py build` 한 번으로 블로그 페이지(HTML)가 생성되고
- `python cli.py rss`로 구독용 RSS 피드까지 만들어 줍니다

## 사용법

```bash
python cli.py new-post "오늘의 일기"   # 새 글 뼈대 생성
python cli.py build --theme dark       # 다크 테마로 블로그 빌드
python cli.py rss                      # feed.xml 생성
```

## 구성

| 파일/폴더 | 역할 |
|----------|------|
| markdown_engine.py | 마크다운 → HTML 변환 엔진 |
| exporter.py | 블로그 페이지 틀 입히기 + 파일 출력 |
| cli.py | 명령행 진입점 |
| posts/ | 내 블로그 글 + 글 관리 모듈 |
| themes/ | 블로그 테마 CSS (default / dark) |
| rss_builder.py | RSS 피드 생성 |
