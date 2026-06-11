<#
setup-git-history.ps1 — S6 시나리오 도구 (정밀 검진 HIST-01 핫스팟 이력 생성)

사용법:
  powershell -ExecutionPolicy Bypass -File setup-git-history.ps1 -CopyPath <검사용 사본 경로>

동작:
  1) 인자로 받은 "사본 경로"(원본 픽스처 messy-project 를 복사해 둔 폴더)에 git 저장소를 만들고
  2) 전체 파일로 첫 커밋을 만든 뒤
  3) main.py 한 파일만 건드리는 작은 커밋을 5회 추가해 핫스팟(HIST-01) 이력을 만든다.

주의 (절대 규칙):
  - 이 스크립트는 검사 직전에 만든 "사본"에서만 사용한다.
  - 원본 픽스처(tests/fixtures/messy-project)에는 절대 .git 을 만들지 않는다.
    원본에 git 이력이 생기면 픽스처가 오염되어 다른 테스트 결과가 달라진다.
    아래 가드가 원본 경로를 감지하면 즉시 중단한다.
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
$originalFixture = Join-Path $PSScriptRoot "messy-project"
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

# --- 가드 4: main.py 존재 확인 ---
$mainPy = Join-Path $resolvedCopy "main.py"
if (-not (Test-Path -LiteralPath $mainPy -PathType Leaf)) {
    Write-Error "사본에 main.py 가 없습니다: $mainPy"
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
    git commit --quiet -m "initial commit: messy-project fixture copy"
    if ($LASTEXITCODE -ne 0) { Write-Error "첫 커밋 실패"; exit 1 }

    # 2) main.py 만 건드리는 작은 커밋 5회 (HIST-01 핫스팟 이력)
    #    파일 끝에 ASCII 주석 한 줄씩 추가 — UTF-8(BOM 없음) 유지
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    for ($i = 1; $i -le 5; $i++) {
        [System.IO.File]::AppendAllText($mainPy, "`n# hotspot history edit $i", $utf8NoBom)
        git add main.py
        git commit --quiet -m "chore: touch main.py ($i/5)"
        if ($LASTEXITCODE -ne 0) { Write-Error "커밋 실패 ($i/5)"; exit 1 }
    }

    Write-Output "완료: $resolvedCopy 에 git 이력 생성 (첫 커밋 1회 + main.py 수정 커밋 5회)"
    git log --oneline
}
finally {
    Pop-Location
}
