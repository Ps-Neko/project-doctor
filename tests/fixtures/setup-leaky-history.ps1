<#
setup-leaky-history.ps1 — SEC-02 시나리오 도구 (공개 전 검진: git 과거 기록 속 비밀키 이력 생성)

사용법:
  powershell -ExecutionPolicy Bypass -File setup-leaky-history.ps1 -CopyPath <검사용 사본 경로>

동작:
  1) 인자로 받은 "사본 경로"(원본 픽스처 leaky-project 를 복사해 둔 폴더)에 git 저장소를 만들고
  2) 전체 파일로 첫 커밋을 만든 뒤
  3) secrets_old.txt 에 가짜 키(AWS 공식 예시 키 AKIAIOSFODNN7EXAMPLE)를 넣어 커밋하고
  4) 그 파일을 삭제하는 커밋을 추가한다.
  => 작업 폴더에는 키가 없지만 git 기록에는 남는 SEC-02 케이스 완성.

주의 (절대 규칙):
  - 이 스크립트는 검사 직전에 만든 "사본"에서만 사용한다.
  - 원본 픽스처(tests/fixtures/leaky-project)에는 절대 .git 을 만들지 않는다.
    원본에 git 이력이 생기면 픽스처가 오염되어 다른 테스트 결과가 달라진다.
    아래 가드가 원본 경로를 감지하면 즉시 중단한다.
  - 심는 키는 AWS 공식 문서의 공개 예시 키로, 실존 자격증명이 아니다.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$CopyPath
)

$ErrorActionPreference = "Stop"

# --- 가드 1: 사본 폴더 존재 확인 ---
if (-not (Test-Path -LiteralPath $CopyPath -PathType Container)) {
    Write-Error "사본 폴더가 없습니다: $CopyPath"
    exit 1
}
$resolvedCopy = (Resolve-Path -LiteralPath $CopyPath).Path.TrimEnd("\")

# --- 가드 2: 원본 픽스처 보호 — 원본에는 절대 .git 을 만들지 않는다 ---
$originalFixture = Join-Path $PSScriptRoot "leaky-project"
if (Test-Path -LiteralPath $originalFixture) {
    $resolvedOriginal = (Resolve-Path -LiteralPath $originalFixture).Path.TrimEnd("\")
    if ($resolvedCopy -ieq $resolvedOriginal) {
        Write-Error "원본 픽스처에는 git 저장소를 만들 수 없습니다. 사본 경로를 지정하세요."
        exit 1
    }
}

# --- 가드 3: 이미 git 저장소면 중단 (중복 실행 방지) ---
if (Test-Path -LiteralPath (Join-Path $resolvedCopy ".git")) {
    Write-Error "이미 git 저장소입니다: $resolvedCopy"
    exit 1
}

# --- 가드 4: leaky-project 사본이 맞는지 확인 (app.py 존재) ---
$appPy = Join-Path $resolvedCopy "app.py"
if (-not (Test-Path -LiteralPath $appPy -PathType Leaf)) {
    Write-Error "사본에 app.py 가 없습니다: $appPy"
    exit 1
}

Push-Location -LiteralPath $resolvedCopy
try {
    git init --quiet
    if ($LASTEXITCODE -ne 0) { Write-Error "git init 실패"; exit 1 }
    git config user.name "fixture-bot"
    git config user.email "fixture-bot@example.com"

    # 1) 전체 첫 커밋
    git add -A
    git commit --quiet -m "initial commit: leaky-project fixture copy"
    if ($LASTEXITCODE -ne 0) { Write-Error "첫 커밋 실패"; exit 1 }

    # 2) secrets_old.txt 에 가짜 키 추가 커밋 — UTF-8(BOM 없음) 유지
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $secretsFile = Join-Path $resolvedCopy "secrets_old.txt"
    [System.IO.File]::WriteAllText($secretsFile, "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE`n", $utf8NoBom)
    git add secrets_old.txt
    git commit --quiet -m "chore: add legacy secrets file (fixture fake key)"
    if ($LASTEXITCODE -ne 0) { Write-Error "키 추가 커밋 실패"; exit 1 }

    # 3) 그 파일을 삭제하는 커밋 — 작업 폴더에는 없지만 기록에는 남는다 (SEC-02)
    git rm --quiet secrets_old.txt
    git commit --quiet -m "chore: remove legacy secrets file"
    if ($LASTEXITCODE -ne 0) { Write-Error "삭제 커밋 실패"; exit 1 }

    Write-Output "완료: $resolvedCopy 에 SEC-02 이력 생성 (가짜 키 추가 -> 삭제, git 기록에만 잔존)"
    git log --oneline
}
finally {
    Pop-Location
}
