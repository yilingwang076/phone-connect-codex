# 手机镜像 · Phone Connect for Codex

一个可复用的 Codex Skill，用于在本地电脑接入手机、显示手机画面，并在可用的组合上操作手机。Skill 位于 [`skills/phone-connect-codex`](skills/phone-connect-codex)。

| 电脑 | 手机 | 方式 | 能力 |
| --- | --- | --- | --- |
| Mac | 安卓 | USB、ADB、scrcpy | 镜像和控制 |
| Windows | 安卓 | USB、ADB、scrcpy | 镜像和控制 |
| Mac | iPhone | macOS 的“iPhone 镜像” | 镜像和控制，受 Apple 系统条件限制 |
| Windows | iPhone | 已安装的 AirPlay 接收软件 | 镜像；通常需在 iPhone 上操作 |

安卓路径会先检查依赖，只在缺少工具且实际需要连接时安装。Mac 使用 Homebrew 安装 ADB/scrcpy，必要时安装 Homebrew；Windows 使用 WinGet 安装 scrcpy 和所需的 Android Platform Tools。安装器可能要求用户在本机完成系统授权。Windows + iPhone 需要另行选择 AirPlay 接收软件，Skill 不会自行购买或安装这类软件。

## 安装

在 Codex 中调用 `$skill-installer`，提供这个公开地址：

`https://github.com/yilingwang076/phone-connect-codex/tree/main/skills/phone-connect-codex`

也可在本机终端运行 Codex 自带的安装脚本：

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo yilingwang076/phone-connect-codex \
  --path skills/phone-connect-codex
```

Windows 用户可直接在 Codex 里提供上述 GitHub 地址给 `$skill-installer`，无需照搬 Mac 的 `~` 路径。安装后在下一轮对话中使用：

- “帮我接入与操作安卓手机”
- “帮我接入与操作 iPhone 手机”
- “帮我把手机镜像到电脑上”

Codex 必须运行在能访问本机 USB 和桌面的环境中；云端会话无法直接控制用户电脑上的手机。使用时请按提示完成手机上的调试授权或镜像连接。付款、发送消息、删除内容等动作需要用户明确授权。

## 验证范围

当前 Mac + Redmi 安卓设备已完成连接与截图测试。其他品牌和 Windows 路径尚未实机验证；适用范围以设备、系统和标准 ADB/scrcpy 或系统镜像功能的支持情况为准。尤其是 Windows + iPhone 的 AirPlay 方式不等于由 Windows 控制 iPhone。

## License

MIT，见 [LICENSE](LICENSE)。
