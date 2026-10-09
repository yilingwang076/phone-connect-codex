# 安卓镜像依赖：检查与自动安装

仅在**本地 Mac 或 Windows 终端**为实际安卓接入任务补齐缺失依赖。下面的 `scripts/` 路径都从本 Skill 文件夹解析为绝对路径，不依赖当前工作目录。先运行检查模式并告诉用户将安装哪些工具、来源和可能的系统权限提示；随后执行安装模式。用户已要求自动接入时，无需因普通缺失依赖再次停下确认；系统安装器要求输入密码、接受条款或授权时由用户在本机完成，不索取密码。已存在的工具不重装或升级。安装失败时保留错误输出，停止接入并说明阻碍，不反复重试。

## Mac

执行 `bash scripts/install_android_tools.sh --check`，必要时执行 `bash scripts/install_android_tools.sh --install`。脚本只在 ADB 或 scrcpy 缺失时需要 Homebrew；Homebrew 缺失时从 [Homebrew 官方安装脚本](https://brew.sh/) 下载并运行，然后按 [scrcpy 官方 Mac 指引](https://github.com/Genymobile/scrcpy/blob/master/doc/macos.md) 安装缺失的 `android-platform-tools` 和／或 `scrcpy`。Homebrew 安装可能要求 Xcode 命令行工具、管理员密码或交互式确认。使用带终端交互的本地会话运行安装模式；若没有可交互终端，说明原因并让用户在本机终端执行，不使用不受监督的 sudo。

## Windows

在 PowerShell 中执行 `& scripts/install_android_tools.ps1 -Mode Check`，必要时执行 `& scripts/install_android_tools.ps1 -Mode Install`。脚本优先使用已有 WinGet 安装 [Genymobile.scrcpy](https://github.com/Genymobile/scrcpy/blob/master/doc/windows.md)，若安装后仍缺少独立 ADB 命令，再安装 `Google.PlatformTools`；从已安装的 Microsoft App Installer 注册 WinGet 后可继续。若 App Installer／WinGet 本身不可用，按 [Microsoft WinGet 文档](https://learn.microsoft.com/en-us/windows/package-manager/winget/)提示用户安装或启用它，再继续；不把 Homebrew 安装到原生 Windows。若设备策略阻止 PowerShell 脚本，遵守该策略，改为经允许的终端命令或请管理员协助。

安装后重新检查 `adb version`、`scrcpy --version` 和 `adb devices -l`。若工具已安装但当前 Codex 进程仍找不到它们，刷新终端环境或重开本地会话，再继续；不要误报安装失败。Windows 上的 OEM USB 驱动只在设备识别失败且厂商说明要求时另行排查。
