# First connection and troubleshooting

## General USB setup

Use a data-capable USB cable and connect the phone to the Mac or Windows PC. On the phone, enable Developer options, enable USB debugging, and approve the computer's RSA debugging prompt. Then check `adb devices -l`. ADB access does not universally require USB file transfer mode, and `USB installation` is not a default prerequisite. Do not toggle either setting without evidence that this particular device needs it.

`device` means ADB is authorized and ready. `unauthorized` means the phone needs the debugging approval prompt; unlock it and approve the trusted computer. `offline` means the transport is present but unusable; inspect the cable/port and reconnect, then check again. An empty list means check cable, USB port, debugging state, and whether this is the local computer rather than a cloud host. On Windows, if only this device fails to appear, check the manufacturer's USB driver guidance. If ADB itself cannot start because a sandbox denies its local socket, request local terminal permission. Avoid restarting the ADB server while another active workflow depends on it.

If the phone is locked, wake/unlock it with the user as appropriate. Never guess a passcode. If an authorization prompt is not visible, inspect the physical screen and screenshot before any retry.

## Manufacturer differences

Menus vary by Android version, region, and skin. These are leads, not universal paths. If the shown menu differs, ask for the exact model/OS version or a Settings screenshot instead of inventing steps.

| Family | Where to look |
| --- | --- |
| Google/near-stock Android | Settings → About phone → Build number (tap repeatedly); USB debugging is commonly under Settings → System → Developer options. |
| Samsung Galaxy | Settings → About phone → Software information → Build number (seven taps); Developer options appears in Settings. |
| Xiaomi / Redmi | On MIUI-era devices, Settings → My device → All specs → MIUI version (seven taps), then Additional settings → Developer options. HyperOS labels can differ; search Settings for Developer options/USB debugging. |
| OPPO / OnePlus using ColorOS | ColorOS 14–16 commonly uses About device → Version → Version No.; USB debugging may be under System & update or Additional settings depending on release. |
| vivo | One official guide uses About phone → Software information → Version, then System management → Developer options; older guides use Build number and Settings → System. |
| Other brands | Search Settings for Developer options and USB debugging; request model and Settings screenshot if ambiguous. |

For Xiaomi/Redmi **only**, if ADB screenshots work but tap/swipe injection is denied, inspect whether “USB debugging (Security settings)” is relevant. It can have extra prompts/account requirements. Do not enable it silently. Do not generalize that requirement to other brands.

Sources: [Android ADB](https://developer.android.com/tools/adb), [Android Developer options](https://developer.android.com/studio/debug/dev-options), [Samsung](https://www.samsung.com/us/support/answer/ANS10003430/), [Xiaomi](https://www.mi.com/my/support/article/KA-06515/), [OPPO](https://support.oppo.com/au/answer/?aid=neu9332), [vivo manual](https://asia-exstatic-vivofs.vivo.com/PSee2l50xoirPK7y/1740713719699/ccedd0784d8e3510d11a8cb348ed56e9.pdf), [scrcpy](https://github.com/Genymobile/scrcpy).
