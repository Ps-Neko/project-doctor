"""check_location_sampling (BL-22 위치 샘플링 게이트) 단위 테스트."""
import check_location_sampling as cls


def _lines(text: str) -> list[str]:
    return text.splitlines()


EXPECTED_3 = _lines(
    "## 심은 문제 (3건)\n"
    "| ID | 위치 | 심각도 |\n"
    "|----|------|--------|\n"
    "| DUP-01 | calc()가 main.py / utils.py 두 곳에 복사됨 | 🔴 |\n"
    "| DEAD-01 | utils.py의 legacy() 함수 — 호출 0건 | 🟡 |\n"
    "| DOC-01 | README 파일 없음 | 🔴 |\n"
)


def test_filename_extraction_with_adjacent_hangul():
    # 'utils.py의'처럼 확장자에 한글이 바로 붙어도 파일명을 뽑는다 (\b 대신 lookahead).
    rows = cls.parse_expected_locations(EXPECTED_3)
    assert rows[0] == ("DUP-01", {"main.py", "utils.py"})
    assert rows[1] == ("DEAD-01", {"utils.py"})
    assert rows[2] == ("DOC-01", set())  # 'README 파일 없음' — 파일명 없음 → 위치 검사 N/A


def test_pass_when_locations_match():
    report = _lines(
        "### [DUP-01] 중복\n- 어디? main.py:10, utils.py:12\n"
        "### [DEAD-01] 죽은 코드\n- 어디? utils.py:33\n"
    )
    checked, hits, misses = cls.evaluate(report, EXPECTED_3)
    # DUP-01·DEAD-01 은 파일명 보유라 검사 대상, DOC-01 은 N/A
    assert {i for i, _ in checked} == {"DUP-01", "DEAD-01"}
    assert not misses
    assert {i for i, _ in hits} == {"DUP-01", "DEAD-01"}


def test_misplaced_id_is_caught():
    # DUP-01 을 보고했지만 엉뚱한 파일(config.json)을 가리킴 → 위치 오진
    report = _lines(
        "### [DUP-01] 중복\n- 어디? config.json:3\n"
        "### [DEAD-01] 죽은 코드\n- 어디? utils.py:33\n"
    )
    _, hits, misses = cls.evaluate(report, EXPECTED_3)
    assert ("DUP-01", {"main.py", "utils.py"}) in misses
    assert ("DEAD-01", {"utils.py"}) in hits


def test_skips_when_no_filename_ids():
    expected = _lines(
        "## 심은 문제\n| ID | 위치 | 심각도 |\n|--|--|--|\n"
        "| DOC-01 | README 없음 | 🔴 |\n| TEST-01 | 테스트 0건 | 🟡 |\n"
    )
    checked, _, misses = cls.evaluate(["### [DOC-01] x"], expected)
    assert checked == []  # 위치 검사 대상 없음
    assert not misses


def test_only_top_n_sampled():
    rows = "\n".join(f"| BIG-{i:02d} | f{i}.py 어딘가 | 🟡 |" for i in range(1, 9))
    expected = _lines(
        "## 심은 문제\n| ID | 위치 | 심각도 |\n|--|--|--|\n" + rows
    )
    checked, _, _ = cls.evaluate([], expected)
    assert len(checked) == cls.SAMPLE_SIZE  # 상위 N 개만 표본


def test_fenced_id_examples_ignored():
    # 코드펜스 안의 [DUP-01] 예시(wrong.py)는 구간 판독에서 제외되고,
    # 펜스 밖 진짜 보고(main.py/utils.py)만 본다.
    expected = _lines(
        "## 심은 문제\n| ID | 위치 | 심각도 |\n|--|--|--|\n"
        "| DUP-01 | calc()가 main.py / utils.py 에 복사됨 | 🔴 |\n"
    )
    report = _lines(
        "```\n### [DUP-01] 예시\n- 어디? wrong.py\n```\n"
        "### [DUP-01] 진짜\n- 어디? main.py, utils.py\n"
    )
    _, hits, misses = cls.evaluate(report, expected)
    assert ("DUP-01", {"main.py", "utils.py"}) in hits
    assert not misses


def test_usage_error_returns_1():
    assert cls.main(["prog"]) == 1


def test_long_location_cell_is_length_capped():
    """비정상적으로 긴 위치 셀은 MAX_LOC_LEN으로 잘라 FILENAME_RE 백트래킹 폭주(ReDoS)를 막는다.

    상한 너머의 파일명은 추출되지 않는다(현실 위치 셀은 <100자라 정상 추출엔 무영향).
    이전엔 상한 없이 finditer가 셀 전체를 훑어 10만 자 셀에서 catastrophic backtracking(O(n²))이 났다."""
    far = "a" * cls.MAX_LOC_LEN + " realfile.py"  # realfile.py는 상한 너머에 위치
    rows = cls.parse_expected_locations(_lines(
        "## 심은 문제 (2건)\n"
        "| ID | 위치 | 심각도 |\n"
        "|----|------|--------|\n"
        f"| DUP-01 | {far} | 🔴 |\n"
        "| DUP-02 | near.py 한 곳 | 🟡 |\n"
    ))
    d = dict(rows)
    assert "realfile.py" not in d["DUP-01"]  # 상한으로 잘려 미추출 (ReDoS 차단의 부산물)
    assert d["DUP-02"] == {"near.py"}        # 정상 길이 셀은 그대로 추출(무영향)
