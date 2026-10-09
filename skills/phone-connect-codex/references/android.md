# 安卓手机：Mac 或 Windows 上的 USB、ADB 与 scrcpy

使用**实际连接手机的本地电脑终端**。云端环境无法访问本地 USB；若执行沙箱阻止 ADB 服务或进程检查，申请本地执行权限，不把它误判为没有设备。

以下 `scripts/android_usb.py` 均指本 Skill 文件夹内脚本，执行时解析为绝对路径并加 Python 启动命令。Mac 可用 `python3`，Windows 可用 `py -3` 或已安装的 `python`；先检查当前命令。Windows 首次 USB 接入若识别失败，可按设备厂商说明排查 USB 驱动，不把驱动安装设为通用前提。

1. 运行 `scripts/android_usb.py doctor` 检查操作系统、ADB、scrcpy 和设备。缺失 ADB 或 scrcpy 时，按 [依赖自动安装](install-android-tools.md) 检查并安装；已安装工具不重复安装。若 Python 不可用，先使用该参考中的系统原生安装脚本，再在可用终端直接执行 `adb` 和 `scrcpy`。
2. 运行 `scripts/android_usb.py devices`，它使用 `adb devices -l`。只有一台就自动选择；多台时列出设备让用户选择，后续传 `--serial SERIAL`。区分 `device`、`unauthorized`、`offline`、无设备，详见 [首次连接与排查](connection.md)。
3. 运行 `scripts/android_usb.py info [--serial SERIAL]` 读取品牌、型号、Android 版本和屏幕尺寸，不预设厂商或坐标。
4. 先运行 `scripts/android_usb.py mirror status [--serial SERIAL]`。如没有现有镜像，再用 `mirror start`；可加 `--background`。`mirror stop` 只关闭本脚本跟踪到的镜像。无法确认现有镜像归属时先排查，不重复启动。Windows 进程检查依赖 PowerShell/CIM；不可用时状态未知。
5. 运行 `scripts/android_usb.py screenshot [--serial SERIAL] --out PATH`，实际打开图片并报告当前画面。以截图像素尺寸和方向为准。

点击和滑动要传**刚查看过的截图** `--image PATH`，从可见 UI 定位坐标；脚本会与操作前的新截图比对尺寸，并输出操作后截图。返回、主页、按键操作前先观察，之后查看输出截图。失败时先截图分析，不能连续盲点。

中文输入前先检查 scrcpy 剪贴板粘贴或手机键盘能否使用；`adb shell input text` 不应被当作可靠的中文输入方式。安装额外输入工具前先说明并取得授权。文本、锁屏、弹窗、受保护页面和控制受限时读 [输入与边界情况](operation.md)。

不为验证而改变开发者设置或安装手机软件。标准 ADB 与 scrcpy 支持构成通用范围，不保证每一款安卓设备都能截图或注入输入。小米/Redmi 的“USB 调试（安全设置）”仅在这类设备控制受限时专项排查。
