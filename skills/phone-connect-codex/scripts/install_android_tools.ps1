param(
    [ValidateSet('Check', 'Install')]
    [string]$Mode = 'Check'
)

$ErrorActionPreference = 'Stop'
if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw 'This installer is for Windows only.'
}

function Update-SessionPath {
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = (@($env:Path, $machinePath, $userPath) | Where-Object { $_ }) -join ';'
}

function Find-Tool([string]$name) {
    $found = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { return $found.Source }
    return $null
}

Update-SessionPath
$adb = Find-Tool 'adb.exe'
$scrcpy = Find-Tool 'scrcpy.exe'
$winget = Find-Tool 'winget.exe'
Write-Output "WinGet: $(if ($winget) { $winget } else { 'missing' })"
Write-Output "ADB: $(if ($adb) { $adb } else { 'missing' })"
Write-Output "scrcpy: $(if ($scrcpy) { $scrcpy } else { 'missing' })"

if ($Mode -eq 'Check') { return }
if ($adb -and $scrcpy) {
    Write-Output 'ADB and scrcpy are already installed; nothing to install.'
    return
}

if (-not $winget) {
    if (Get-Command Get-AppxPackage -ErrorAction SilentlyContinue) {
        $appInstaller = Get-AppxPackage -Name Microsoft.DesktopAppInstaller -ErrorAction SilentlyContinue
        if ($appInstaller) {
            try {
                Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
                Update-SessionPath
                $winget = Find-Tool 'winget.exe'
            } catch {
                Write-Warning "App Installer registration failed: $_"
            }
        }
    }
}
if (-not $winget) {
    throw 'WinGet is unavailable. Install or enable Microsoft App Installer, then rerun this script: https://learn.microsoft.com/windows/package-manager/winget/'
}

if (-not $scrcpy) {
    & $winget install --id Genymobile.scrcpy --exact --source winget
    if ($LASTEXITCODE -ne 0) { throw "scrcpy installation failed with exit code $LASTEXITCODE." }
    Update-SessionPath
    $scrcpy = Find-Tool 'scrcpy.exe'
    $adb = Find-Tool 'adb.exe'
}
if (-not $adb) {
    & $winget install --id Google.PlatformTools --exact --source winget
    if ($LASTEXITCODE -ne 0) { throw "ADB installation failed with exit code $LASTEXITCODE." }
    Update-SessionPath
    $adb = Find-Tool 'adb.exe'
}
if (-not $scrcpy) { throw 'scrcpy was installed but is not on the current PATH. Reopen the local terminal and check again.' }
if (-not $adb) { throw 'ADB was installed but is not on the current PATH. Reopen the local terminal and check again.' }

& $adb version | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'ADB version check failed.' }
& $scrcpy --version | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'scrcpy version check failed.' }
Write-Output "Verified ADB: $adb"
Write-Output "Verified scrcpy: $scrcpy"
