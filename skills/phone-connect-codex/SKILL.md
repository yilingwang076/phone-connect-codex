---
name: phone-connect-codex
description: 在 Mac 或 Windows 电脑上接入并镜像安卓手机或 iPhone，按设备组合选择 ADB/scrcpy、Mac iPhone 镜像或 Windows AirPlay 接收软件；安卓工具缺失时自动安装。适用于“帮我接入与操作安卓手机”“帮我接入与操作iPhone手机”及手机投屏请求。
---

# 手机镜像

先确认电脑是 Mac 还是 Windows，以及手机是安卓还是 iPhone。仅在能访问这台电脑的本地执行环境中检查设备和操作界面；云端环境无法直接接入用户本地 USB 或桌面。手机类型或当前电脑不明且无法从环境判断时，再询问用户。

| 组合 | 接入方式 | 电脑端能力 |
| --- | --- | --- |
| Mac + 安卓 | USB、ADB、scrcpy | 镜像与控制；读 [安卓流程](references/android.md)。 |
| Windows + 安卓 | USB、ADB、scrcpy | 镜像与控制；读 [安卓流程](references/android.md)。 |
| Mac + iPhone | 系统“iPhone 镜像” | 镜像与控制；读 [Mac iPhone 流程](references/iphone.md)。 |
| Windows + iPhone | 已有的 AirPlay 接收软件 + iPhone“屏幕镜像” | 镜像画面，通常在 iPhone 上操作；读 [Windows iPhone 流程](references/iphone-windows.md)。 |

先检查对应工具或 App 是否已安装、运行，不重复安装或启动。安卓连接缺少 ADB 或 scrcpy 时，按 [依赖自动安装](references/install-android-tools.md) 在本地补齐；Mac 在需要时自动安装 Homebrew，Windows 使用 WinGet，不在原生 Windows 安装 Homebrew。Windows + iPhone 缺少 AirPlay 接收软件时，说明需要额外软件及可能的授权或费用，请用户选择后再安装；不能把 Windows 的“手机连接”称作完整 iPhone 屏幕镜像，也不能承诺由电脑控制 iPhone。

仅在实际看到手机画面的窗口时报告镜像成功，并描述当前界面。操作以最新画面为依据，关键步骤后重新观察；失败时先截图分析，不连续盲点。受保护内容可能无法显示。付款、发送消息、删除内容等动作需要用户明确授权。不为测试改变手机设置或安装额外软件；缺失依赖的安装只在实际接入任务需要时执行。
