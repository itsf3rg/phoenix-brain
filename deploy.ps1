$ErrorActionPreference = "Stop"

$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"

$gradlePath = Join-Path $PSScriptRoot "android\gradle-8.9\bin\gradle.bat"
$adbPath = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"

Write-Host "Compiling GigBoss APK using local Gradle 8.0 and Studio JDK..."
Set-Location -Path (Join-Path $PSScriptRoot "android")

# Outputting full gradle info
& $gradlePath assembleDebug

if ($LASTEXITCODE -ne 0) {
    Write-Host "Gradle build failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}

Write-Host "APK Built Successfully. Installing to connected device via ADB..."
$apkPath = Join-Path $PSScriptRoot "android\app\build\outputs\apk\debug\app-debug.apk"

if (-Not (Test-Path $apkPath)) {
    Write-Host "Could not find built APK at $apkPath"
    exit 1
}

& $adbPath install -r $apkPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "ADB install failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}

Write-Host "Launching GigBoss on device..."
& $adbPath shell am start -n com.gigboss/.MainActivity

Write-Host "Deployment Complete!"
