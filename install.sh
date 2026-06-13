#!/usr/bin/env bash
# 프로젝트 주치의(project-doctor) 스킬 설치 (macOS/Linux)
#
#   skills/project-doctor 를 ~/.claude/skills/project-doctor 로 복사하고,
#   설치가 인식 가능한 상태인지(SKILL.md·버전)까지 확인합니다. 여러 번 실행해도 안전합니다.
#
# 사용:
#   bash install.sh            # 설치
#   bash install.sh --check    # 복사 없이 현재 설치 상태만 점검
set -euo pipefail

SKILL_NAME="project-doctor"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/skills/$SKILL_NAME"
DST_ROOT="$HOME/.claude/skills"
DST="$DST_ROOT/$SKILL_NAME"
SKILL_MD="$DST/SKILL.md"

skill_version() {
  # SKILL.md 앞부분에서 첫 vX.Y(.Z) 를 뽑는다 (로케일 무관).
  [ -f "$1" ] && sed -n '1,12p' "$1" | grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1
}

check_install() {
  if [ ! -f "$SKILL_MD" ]; then
    echo "[X] 미설치 — $SKILL_MD 없음"
    return 1
  fi
  echo "[OK] 설치됨: $DST ($(skill_version "$SKILL_MD"))"
  echo "     Claude Code 를 새로 시작하면 /project-doctor 가 인식됩니다."
}

if [ "${1:-}" = "--check" ]; then
  check_install
  exit $?
fi

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "[X] 원본을 찾을 수 없습니다: $SRC"
  echo "    이 스크립트는 저장소 루트에서 실행하세요 (skills/ 폴더가 보이는 위치)."
  exit 1
fi

mkdir -p "$DST_ROOT"
rm -rf "$DST"
cp -R "$SRC" "$DST_ROOT/"
echo "[OK] 복사 완료: skills/$SKILL_NAME  ->  $DST ($(skill_version "$SRC/SKILL.md"))"
echo ""
check_install
