<#
.SYNOPSIS
  프로젝트 주치의(project-doctor) 스킬을 Claude Code 에 설치합니다.

.DESCRIPTION
  이 저장소의 skills/project-doctor 를 ~/.claude/skills/project-doctor 로 복사하고,
  설치가 인식 가능한 상태인지(SKILL.md 존재·버전)까지 확인합니다.
  여러 번 실행해도 안전합니다(덮어쓰기). 설치 후 Claude Code 를 새로 시작하면 /project-doctor 가 인식됩니다.

.PARAMETER Check
  복사하지 않고 현재 설치 상태만 점검합니다.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install.ps1
.EXAMPLE
  powershell -File install.ps1 -Check
#>
[CmdletBinding()]
param([switch]$Check)

$ErrorActionPreference = 'Stop'

$SkillName = 'project-doctor'
$Src       = Join-Path $PSScriptRoot "skills/$SkillName"
$DstRoot   = Join-Path $HOME '.claude/skills'
$Dst       = Join-Path $DstRoot $SkillName
$SkillMd   = Join-Path $Dst 'SKILL.md'

function Get-SkillVersion {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    foreach ($line in Get-Content -Path $Path -TotalCount 12 -Encoding UTF8) {
        if ($line -match '스킬 버전:\s*\*{0,2}v([\d.]+)') { return $matches[1] }
    }
    return $null
}

function Test-Install {
    if (-not (Test-Path $SkillMd)) {
        Write-Host "[X] 미설치 — $SkillMd 없음" -ForegroundColor Red
        return $false
    }
    $ver = Get-SkillVersion -Path $SkillMd
    Write-Host "[OK] 설치됨: $Dst (버전 v$ver)" -ForegroundColor Green
    Write-Host "     Claude Code 를 새로 시작하면 /project-doctor 가 인식됩니다."
    return $true
}

if ($Check) {
    if (Test-Install) { exit 0 } else { exit 1 }
}

if (-not (Test-Path (Join-Path $Src 'SKILL.md'))) {
    Write-Host "[X] 원본을 찾을 수 없습니다: $Src" -ForegroundColor Red
    Write-Host "    이 스크립트는 저장소 루트에서 실행해야 합니다 (skills/ 폴더가 보이는 위치)." -ForegroundColor Yellow
    exit 1
}

$srcVer = Get-SkillVersion -Path (Join-Path $Src 'SKILL.md')
New-Item -ItemType Directory -Force -Path $DstRoot | Out-Null
# 기존 설치 폴더를 먼저 비운다 — 업데이트에서 사라진/개명된 참조 문서가 남지 않도록 (install.sh의 rm -rf와 동작 일치).
# $DstRoot(다른 스킬들이 든 ~/.claude/skills)가 아니라 $Dst(project-doctor 폴더)만 지운다.
if (Test-Path $Dst) { Remove-Item -Recurse -Force -Path $Dst }
Copy-Item -Recurse -Force -Path $Src -Destination $DstRoot
Write-Host "[OK] 복사 완료: skills/$SkillName  ->  $Dst (v$srcVer)" -ForegroundColor Green
Write-Host ""
Test-Install | Out-Null
