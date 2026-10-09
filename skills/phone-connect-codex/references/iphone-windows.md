# iPhone：Windows 上的屏幕镜像

Windows 没有 Mac 的系统“iPhone 镜像”App。Windows“手机连接”可提供 iPhone 消息、通话、通知等功能，不能当作完整屏幕镜像。要在 Windows 显示 iPhone 画面，检查电脑是否已有可用的 AirPlay 接收软件，例如 AirServer 或 Reflector；优先复用正在运行的窗口。AirPlay 屏幕镜像仅显示画面，通常不能用电脑鼠标控制 iPhone；后续操作需用户在手机上完成。不要把安卓的 ADB/scrcpy 用于 iPhone。

1. 确认当前为可操作的本地 Windows 桌面。检查已安装或正在运行的 AirPlay 接收软件及其状态。不要仅凭安装记录声称镜像已连接。
2. 若没有接收软件，明确告诉用户需要安装第三方软件（可能收费），列出可选方案并等待用户选择和安装授权；不静默下载、安装或购买。
3. 打开或复用接收软件，确认其接收端名称。按软件提示确保 iPhone 和电脑在可互通的同一网络；如接收端未出现，先检查软件和网络状态，不盲目改系统网络或防火墙设置。
4. 指引用户在 iPhone“控制中心”点“屏幕镜像”，选择确认过的接收端；如出现代码，由用户在所示设备输入。连接后观察 Windows 接收窗口，实际显示 iPhone 当前画面才报告成功。
5. 操作请求以接收窗口的最新画面为依据，明确告诉用户在哪个手机控件上操作。用户操作后重新观察；断开、黑屏或受保护画面时先诊断。不能因接收窗口可点击而推断 iPhone 接受点击。

参考：[Apple 的“隔空播放”与“iPhone 镜像”区别](https://support.apple.com/zh-cn/120421)、[AirServer 的 iPhone 投屏步骤](https://support.airserver.com/support/solutions/articles/43000535997-how-to-screen-mirror-your-ios-device-to-airserver)、[Reflector 的 iPhone 投屏步骤](https://help.airsquirrels.com/reflector/how-to-screen-mirror-an-iphone)、[Microsoft Phone Link](https://support.microsoft.com/en-us/windows/apps/phonelink/phone-link-requirements-and-setup)。软件兼容性和费用以当前官方页面及本机实际状态为准。
