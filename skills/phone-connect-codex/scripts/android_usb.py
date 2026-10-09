#!/usr/bin/env python3
"""Local, serial-explicit ADB/scrcpy helper for a real Android device."""

import argparse
import hashlib
import json
import ntpath
import os
import re
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path


class DeviceError(Exception):
    pass


def command(argv, *, timeout=15, check=True):
    try:
        result = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DeviceError(f"Command failed: {argv[0]}: {exc}") from exc
    if check and result.returncode:
        detail = (result.stderr or result.stdout).decode(errors="replace").strip()
        raise DeviceError(f"{argv[0]} exited {result.returncode}: {detail}")
    return result


def require(name):
    path = find_tool(name)
    if not path:
        raise DeviceError(f"Missing {name}; inspect this local computer before installing anything.")
    return path


def find_tool(name):
    path = shutil.which(name)
    if path:
        return path
    if sys.platform == "darwin":
        for directory in ("/opt/homebrew/bin", "/usr/local/bin"):
            path = shutil.which(name, path=directory)
            if path:
                return path
    if os.name == "nt":
        directories = []
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            directories.append(str(Path(local_app_data) / "Microsoft" / "WinGet" / "Links"))
        try:
            import winreg
            locations = (
                (winreg.HKEY_CURRENT_USER, r"Environment"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            )
            for hive, key_name in locations:
                try:
                    with winreg.OpenKey(hive, key_name) as key:
                        value, _ = winreg.QueryValueEx(key, "Path")
                        directories.extend(os.path.expandvars(value).split(os.pathsep))
                except OSError:
                    continue
        except ImportError:
            pass
        return shutil.which(name, path=os.pathsep.join(directories))
    return None


def adb(*args, timeout=15):
    return command([require("adb"), *args], timeout=timeout)


def discover():
    output = adb("devices", "-l").stdout.decode(errors="replace")
    devices = []
    for line in output.splitlines():
        if not line.strip() or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            serial = parts[0]
            detail = " ".join(parts[2:])
            transport = "emulator" if serial.startswith("emulator-") else "network" if ":" in serial else "usb"
            devices.append({"serial": serial, "state": parts[1], "transport": transport, "detail": detail})
    return devices


def selected(serial=None):
    devices = discover()
    usb_devices = [d for d in devices if d["transport"] == "usb"]
    if serial:
        match = next((d for d in devices if d["serial"] == serial), None)
        if not match:
            raise DeviceError(f"Selected serial {serial!r} is not in adb devices -l: {devices}")
        if match["transport"] != "usb":
            raise DeviceError(f"Selected device is {match['transport']}, not a USB phone.")
        if match["state"] != "device":
            raise DeviceError(f"Selected device is {match['state']}; resolve that state on the phone first.")
        return match, usb_devices
    if not usb_devices:
        raise DeviceError(f"No USB ADB phone found. Check the local cable and USB debugging. ADB listed: {devices}")
    if len(usb_devices) != 1:
        raise DeviceError(f"Multiple USB devices found; ask the user to choose a serial: {usb_devices}")
    only = usb_devices[0]
    if only["state"] != "device":
        raise DeviceError(f"Device is {only['state']}; resolve that state on the phone first: {only}")
    return only, usb_devices


def on_device(serial, *args, timeout=15):
    return adb("-s", serial, *args, timeout=timeout)


def property_value(serial, name):
    return on_device(serial, "shell", "getprop", name).stdout.decode(errors="replace").strip()


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise DeviceError("ADB did not return a valid PNG; inspect the device and protection state.")
    return struct.unpack(">II", data[16:24])


def capture(serial):
    data = on_device(serial, "exec-out", "screencap", "-p", timeout=30).stdout
    size = png_size(data)
    return data, size


def image_path(label):
    return Path.cwd() / f"android-{label}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"


def save_capture(serial, path):
    data, size = capture(serial)
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path), "pixels": list(size), "orientation": "landscape" if size[0] > size[1] else "portrait"}


def state_path(serial):
    key = hashlib.sha256(serial.encode()).hexdigest()[:16]
    folder = Path(tempfile.gettempdir()) / "android-usb-control"
    folder.mkdir(mode=0o700, exist_ok=True)
    return folder / f"mirror-{key}.json"


def ps_rows():
    if os.name == "nt":
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            raise DeviceError("PowerShell is unavailable; mirror process status is unknown.")
        query = "Get-CimInstance Win32_Process -Filter \"Name='scrcpy.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
        result = command([powershell, "-NoProfile", "-Command", query], check=False)
        if result.returncode:
            raise DeviceError("Cannot inspect Windows processes; mirror status is unknown.")
        output = result.stdout.decode(errors="replace").strip()
        if not output or output == "null":
            return []
        try:
            records = json.loads(output)
        except json.JSONDecodeError as exc:
            raise DeviceError("Cannot parse Windows process list; mirror status is unknown.") from exc
        if isinstance(records, dict):
            records = [records]
        rows = []
        for record in records:
            line = record.get("CommandLine") or ""
            if not line:
                raise DeviceError("A scrcpy process has no accessible command line; mirror status is unknown.")
            try:
                args = [value.strip('"') for value in shlex.split(line, posix=False)]
            except ValueError:
                raise DeviceError("Cannot parse a scrcpy command line; mirror status is unknown.")
            if args and ntpath.basename(args[0]).lower() == "scrcpy.exe":
                rows.append({"pid": int(record["ProcessId"]), "args": args})
            else:
                raise DeviceError("Cannot identify a scrcpy process; mirror status is unknown.")
        return rows
    result = command(["ps", "-axo", "pid=,command="], check=False)
    if result.returncode:
        raise DeviceError("Cannot inspect local processes; mirror status is unknown. Use a local terminal with process access.")
    rows = []
    for line in result.stdout.decode(errors="replace").splitlines():
        match = re.match(r"\s*(\d+)\s+(.+)", line)
        if not match:
            continue
        try:
            args = shlex.split(match.group(2))
        except ValueError:
            continue
        if args and Path(args[0]).name == "scrcpy":
            rows.append({"pid": int(match.group(1)), "args": args})
    return rows


def ps_start(pid):
    if os.name == "nt":
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            return ""
        query = f"(Get-CimInstance Win32_Process -Filter 'ProcessId = {int(pid)}').CreationDate"
        result = command([powershell, "-NoProfile", "-Command", query], check=False)
        return result.stdout.decode(errors="replace").strip() if result.returncode == 0 else ""
    result = command(["ps", "-p", str(pid), "-o", "lstart="], check=False)
    return result.stdout.decode(errors="replace").strip() if result.returncode == 0 else ""


def explicit_serial(args):
    for index, value in enumerate(args):
        if value in ("-s", "--serial") and index + 1 < len(args):
            return args[index + 1]
        if value.startswith("--serial="):
            return value.split("=", 1)[1]
    return None


def mirror_status(serial, all_devices):
    rows = ps_rows()
    matched = []
    ambiguous = []
    for row in rows:
        tagged = explicit_serial(row["args"])
        if tagged == serial or (tagged is None and len(all_devices) == 1):
            matched.append(row)
        elif tagged is None:
            ambiguous.append(row)
    return {"running": matched, "ambiguous": ambiguous}


def mirror_start(serial, all_devices, background):
    status = mirror_status(serial, all_devices)
    if status["running"]:
        print(json.dumps({"result": "already_running", **status}, ensure_ascii=False))
        return
    if status["ambiguous"]:
        raise DeviceError(f"Existing untagged scrcpy process could belong to this device: {status['ambiguous']}")
    scrcpy = require("scrcpy")
    args = [scrcpy, "--serial", serial, "--no-audio"]
    path = state_path(serial)
    log_path = path.with_suffix(".log")
    launch_options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" and background else {"start_new_session": background} if os.name != "nt" else {}
    with log_path.open("ab") as log:
        process = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, **launch_options)
    time.sleep(0.8)
    if process.poll() is not None:
        raise DeviceError(f"scrcpy exited with {process.returncode}; inspect {log_path}")
    started = ps_start(process.pid)
    if not started:
        process.terminate()
        raise DeviceError("Cannot verify scrcpy process creation time; stopped this launch rather than leaving an untracked mirror.")
    marker = {"serial": serial, "pid": process.pid, "started": started, "args": args, "log": str(log_path)}
    path.write_text(json.dumps(marker), encoding="utf-8")
    print(json.dumps({"result": "started", "background": background, **marker}, ensure_ascii=False))
    if not background:
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait(timeout=5)
        finally:
            path.unlink(missing_ok=True)


def mirror_stop(serial):
    path = state_path(serial)
    if not path.exists():
        raise DeviceError("No mirror tracked by this helper for the selected device; leaving existing mirrors untouched.")
    marker = json.loads(path.read_text(encoding="utf-8"))
    pid = marker.get("pid")
    row = next((r for r in ps_rows() if r["pid"] == pid), None)
    if not row:
        path.unlink(missing_ok=True)
        print(json.dumps({"result": "already_stopped", "pid": pid}))
        return
    started = ps_start(pid)
    if marker.get("serial") != serial or explicit_serial(row["args"]) != serial or not started or started != marker.get("started"):
        raise DeviceError("Tracked PID no longer matches this helper's scrcpy process; refusing to stop it.")
    os.kill(pid, signal.SIGTERM)
    path.unlink(missing_ok=True)
    print(json.dumps({"result": "stopped", "pid": pid}))


def checked_image(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise DeviceError(f"Screenshot does not exist: {path}")
    if time.time() - path.stat().st_mtime > 300:
        raise DeviceError("Screenshot is older than five minutes; capture and inspect a new one.")
    return png_size(path.read_bytes())


def coordinate(value, maximum, label):
    if not 0 <= value < maximum:
        raise DeviceError(f"{label}={value} is outside the screenshot bound 0..{maximum - 1}")


def action(args, serial):
    if args.action in ("tap", "swipe"):
        previous_size = checked_image(args.image)
        _, current_size = capture(serial)
        if previous_size != current_size:
            raise DeviceError(f"Screen dimensions changed from {previous_size} to {current_size}; inspect a new screenshot.")
        if args.action == "tap":
            coordinate(args.x, current_size[0], "x")
            coordinate(args.y, current_size[1], "y")
            command_args = ("tap", str(args.x), str(args.y))
        else:
            for name, maximum in (("x1", current_size[0]), ("x2", current_size[0]), ("y1", current_size[1]), ("y2", current_size[1])):
                coordinate(getattr(args, name), maximum, name)
            if not 50 <= args.duration_ms <= 10000:
                raise DeviceError("Swipe duration must be 50–10000 ms.")
            command_args = ("swipe", str(args.x1), str(args.y1), str(args.x2), str(args.y2), str(args.duration_ms))
        adb_args = ("shell", "input", *command_args)
    else:
        code = "KEYCODE_BACK" if args.action == "back" else "KEYCODE_HOME" if args.action == "home" else args.code
        if not re.fullmatch(r"KEYCODE_[A-Z0-9_]+|\d{1,3}", code):
            raise DeviceError("Key must be a KEYCODE_* name or a 1–3 digit Android key code.")
        adb_args = ("shell", "input", "keyevent", code)
    try:
        on_device(serial, *adb_args)
    except DeviceError as exc:
        try:
            result = save_capture(serial, args.after or image_path("failure"))
        except DeviceError:
            raise exc
        raise DeviceError(f"{exc}; inspect {result['path']} before retrying.") from exc
    try:
        result = save_capture(serial, args.after or image_path("after"))
    except DeviceError as exc:
        raise DeviceError(f"Input was sent, but verification screenshot failed: {exc}. Stop and inspect before retrying.") from exc
    print(json.dumps({"action": args.action, "after": result}, ensure_ascii=False))


def add_serial(parser):
    parser.add_argument("--serial", help="Exact serial from adb devices -l; required when multiple devices are listed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("devices", help="List all ADB states without selecting a device")
    sub.add_parser("doctor", help="Check local OS, tools, and ADB devices")
    info = sub.add_parser("info", help="Read selected device properties")
    add_serial(info)
    shot = sub.add_parser("screenshot", help="Save an ADB screenshot")
    add_serial(shot)
    shot.add_argument("--out", type=Path, help="Output PNG path")
    mirror = sub.add_parser("mirror", help="Inspect, start, or stop scrcpy")
    mirror_sub = mirror.add_subparsers(dest="mirror_action", required=True)
    for name in ("status", "start", "stop"):
        child = mirror_sub.add_parser(name)
        add_serial(child)
        if name == "start":
            child.add_argument("--background", action="store_true")
    tap = sub.add_parser("tap", help="Tap coordinates from a recently viewed screenshot")
    add_serial(tap)
    tap.add_argument("--image", type=Path, required=True)
    tap.add_argument("--x", type=int, required=True)
    tap.add_argument("--y", type=int, required=True)
    tap.add_argument("--after", type=Path)
    swipe = sub.add_parser("swipe", help="Swipe coordinates from a recently viewed screenshot")
    add_serial(swipe)
    swipe.add_argument("--image", type=Path, required=True)
    for name in ("x1", "y1", "x2", "y2"):
        swipe.add_argument(f"--{name}", type=int, required=True)
    swipe.add_argument("--duration-ms", type=int, default=350)
    swipe.add_argument("--after", type=Path)
    for name in ("back", "home", "key"):
        item = sub.add_parser(name)
        add_serial(item)
        item.add_argument("--after", type=Path)
        if name == "key":
            item.add_argument("--code", required=True)
    args = parser.parse_args()
    try:
        if args.action == "doctor":
            tools = {name: find_tool(name) for name in ("adb", "scrcpy")}
            result = {"os": sys.platform, "tools": tools}
            if tools["adb"]:
                try:
                    result["devices"] = discover()
                except DeviceError as exc:
                    result["adb_error"] = str(exc)
            print(json.dumps(result, ensure_ascii=False))
            return
        if args.action == "devices":
            print(json.dumps(discover(), ensure_ascii=False))
            return
        device, all_devices = selected(args.serial)
        serial = device["serial"]
        if args.action == "info":
            size = on_device(serial, "shell", "wm", "size").stdout.decode(errors="replace").strip()
            print(json.dumps({"serial": serial, "brand": property_value(serial, "ro.product.brand"), "model": property_value(serial, "ro.product.model"), "android": property_value(serial, "ro.build.version.release"), "wm_size": size}, ensure_ascii=False))
        elif args.action == "screenshot":
            print(json.dumps(save_capture(serial, args.out or image_path("screen")), ensure_ascii=False))
        elif args.action == "mirror":
            if args.mirror_action == "status":
                print(json.dumps(mirror_status(serial, all_devices), ensure_ascii=False))
            elif args.mirror_action == "start":
                mirror_start(serial, all_devices, args.background)
            else:
                mirror_stop(serial)
        else:
            action(args, serial)
    except DeviceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
