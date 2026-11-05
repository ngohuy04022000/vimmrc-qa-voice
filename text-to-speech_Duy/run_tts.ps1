<#
.SYNOPSIS
    Script chay nhanh tong hop tieng noi Text-to-Speech (Matcha-TTS).
.EXAMPLE
    .\run_tts.ps1
    .\run_tts.ps1 -Text "Xin chào các bạn."
    .\run_tts.ps1 -File test_sentence.txt
    .\run_tts.ps1 -File test_sentence.txt -Engine edge -Voice nu
#>
param(
    [string]$Text,
    [string]$File = "test_sentence.txt",
    [string]$Engine = "matcha",
    [string]$Voice = "nu",
    [string]$Rate = "+0%",
    [string]$Output,
    [switch]$LaunchApp
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if ($LaunchApp) {
    Write-Host "[Khởi động] Đang chạy cả Backend (:8000) và Frontend (:4200)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\..'; python -m uvicorn scripts.api_server:app --host 127.0.0.1 --port 8000"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\..\web-interface_Luong'; npm start"
    Write-Host "Truy cập giao diện Web tại: http://localhost:4200/" -ForegroundColor Green
    return
}

$cmdArgs = @()
if ($Text) {
    $cmdArgs += @("-t", $Text)
} else {
    $cmdArgs += @("-f", $File)
}

$cmdArgs += @("-e", $Engine)
if ($Engine -eq "edge") {
    $cmdArgs += @("-v", $Voice)
}
if ($Rate -ne "+0%") {
    $cmdArgs += @("--rate", $Rate)
}
if ($Output) {
    $cmdArgs += @("-o", $Output)
}

Write-Host "[TTS] Đang chạy: python synthesize.py $cmdArgs" -ForegroundColor Yellow
python synthesize.py @cmdArgs

