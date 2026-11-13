# VAMOTRA Smart Ring — BLE Gesture Control Research

**Status:** BLE discovery and diagnostics implemented. Gesture control is **not yet verified** for this ring. We need to establish whether its BLE protocol exposes live motion readings. No firmware modification is attempted.

## Mac setup

Use Python 3.10+ and enable Bluetooth access for Terminal (System Settings → Privacy & Security → Bluetooth).

```bash
git clone https://github.com/neeladhruvasai-tech/bee-device-scanner.git
cd bee-device-scanner
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python ble_gesture.py scan --seconds 15
```

Look for the ring name, or an **unnamed** device. On macOS, the identifier is a CoreBluetooth UUID rather than a hardware MAC address. Compare scan results with the ring awake versus asleep/off to help identify it.

Then run:

```bash
python ble_gesture.py inspect "PASTE-DEVICE-IDENTIFIER-HERE"
python ble_gesture.py inspect "PASTE-DEVICE-IDENTIFIER-HERE" --watch 20
```

The second command listens to all subscribable notification/indication characteristics for 20 seconds and prints raw bytes. It **does not decode** those bytes into motion data, control the Mac, write to the ring, or upload observations.

## Next experiment

1. Capture baseline notifications while the ring is stationary.
2. Repeat while moving the hand left and right.
3. Compare timestamps and payloads; identify a documented or experimentally defensible motion data format.
4. Only if motion samples can be decoded reliably, add gesture classification, calibration, debounce/cooldown and opt-in keyboard shortcuts.

Some consumer rings expose only proprietary health summaries and no live IMU data. In that case ring-only gesture control may not be possible without manufacturer protocol support.

## Privacy and safety

Raw BLE notifications may contain private device information. Review/redact identifiers and payloads before sharing logs. Do not run random write commands or attempt firmware flashing. If the device is connected to its phone app, disconnect the app before testing if necessary.
