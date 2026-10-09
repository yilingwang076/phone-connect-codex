# Input and edge cases

## Coordinate discipline

View the exact screenshot used for `--image`. Derive x/y from its pixel dimensions and visible controls; do not carry coordinates between screens, devices, or orientations. The helper rejects a tap/swipe if a fresh pre-action capture has different dimensions. It saves an after-action screenshot, which must be viewed before deciding the next input. If the UI remains unchanged, diagnose from a new screenshot instead of repeating.

## Text

ADB's `input text` has uneven Unicode support and escaping behavior. For Chinese, first check the actual scrcpy version and whether clipboard paste into the focused field succeeds; alternatively use the device keyboard manually. If a helper IME would be needed, describe the software and obtain authorization before installation. Do not assume copied text reached the device without visual confirmation. For messages, posts, payments, and deletions, explicit user authorization remains necessary at the action.

## Blockers

- A lock screen can hide app content and require the user's unlock method. Do not request or enter a secret by guesswork.
- An all-black PNG can mean a sleeping screen as well as protected content. Read `adb -s SERIAL shell dumpsys power` for wakefulness; if a wake key is appropriate, send it once and recapture. If it stays black, stop and ask the user to inspect/unlock the phone rather than repeatedly injecting input.
- USB authorization dialogs may appear only on the phone. Resolve them there, then rerun discovery.
- Connection loss changes ADB state. Stop input, rerun `devices`, and confirm the selected serial before resuming.
- Protected apps or `FLAG_SECURE` windows may yield blank/black screenshots or refuse mirroring. Report that limit and use visible, authorized alternatives; do not bypass protection.
- Some OEMs restrict shell input or scrcpy control even when capture works. Capture the current state, inspect the error, and consult the appropriate manufacturer setting only if relevant. ADB `device` alone does not prove control capability.
- If process inspection is unavailable, mirror status is unknown. Do not start a second scrcpy instance until the current mirror has been identified.
