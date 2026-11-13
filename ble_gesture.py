"""BLE discovery and read-only diagnostics for a smart ring on macOS.

No manufacturer-specific motion format is assumed. Do not treat arbitrary
notification bytes as accelerometer values.
"""
import argparse
import asyncio
from datetime import datetime
from bleak import BleakClient, BleakScanner


async def scan(seconds: float):
    print(f"Scanning for {seconds:g} seconds. Keep the ring awake and nearby...")
    devices = await BleakScanner.discover(timeout=seconds, return_adv=True)
    if not devices:
        print("No BLE advertisements found. Check Bluetooth permissions and ring state.")
        return
    for identifier, (device, advertisement) in sorted(devices.items()):
        name = device.name or advertisement.local_name or "(unnamed)"
        uuids = ", ".join(advertisement.service_uuids) or "none advertised"
        print(f"{identifier} | {name} | RSSI {advertisement.rssi} | services: {uuids}")
    print("\nOn macOS, device identifiers are CoreBluetooth UUIDs, not MAC addresses.")


async def inspect(identifier: str, watch: float):
    print("Connecting read-only; no firmware changes or characteristic writes.")
    async with BleakClient(identifier, timeout=20.0) as client:
        print(f"Connected: {client.is_connected}")
        notify_chars = []
        for service in client.services:
            print(f"\nSERVICE {service.uuid} {service.description}")
            for char in service.characteristics:
                props = ", ".join(char.properties)
                print(f"  CHARACTERISTIC {char.uuid} [{props}]")
                for descriptor in char.descriptors:
                    print(f"    descriptor {descriptor.uuid}")
                if "notify" in char.properties or "indicate" in char.properties:
                    notify_chars.append(char)
        if watch <= 0:
            return
        if not notify_chars:
            print("No notification/indication characteristics found.")
            return

        def on_data(sender, data):
            print(f"{datetime.now().isoformat(timespec='milliseconds')} "
                  f"{sender.uuid} {bytes(data).hex(' ')}")

        started = []
        try:
            for char in notify_chars:
                try:
                    await client.start_notify(char, on_data)
                    started.append(char)
                    print(f"Listening on {char.uuid}")
                except Exception as exc:
                    print(f"Cannot subscribe to {char.uuid}: {exc}")
            if started:
                print(f"Watching for {watch:g}s. Move your hand gently; "
                      "avoid pairing with another app simultaneously.")
                await asyncio.sleep(watch)
        finally:
            for char in started:
                try:
                    await client.stop_notify(char)
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Read-only BLE ring explorer")
    sub = parser.add_subparsers(dest="command", required=True)
    scan_parser = sub.add_parser("scan", help="Find BLE devices, including unnamed ones")
    scan_parser.add_argument("--seconds", type=float, default=12)
    inspect_parser = sub.add_parser("inspect", help="List GATT services and optionally watch notifications")
    inspect_parser.add_argument("identifier", help="Device identifier from scan (quote it)")
    inspect_parser.add_argument("--watch", type=float, default=0, metavar="SECONDS")
    args = parser.parse_args()
    try:
        if args.command == "scan":
            if args.seconds <= 0:
                parser.error("--seconds must be positive")
            asyncio.run(scan(args.seconds))
        else:
            if args.watch < 0:
                parser.error("--watch cannot be negative")
            asyncio.run(inspect(args.identifier, args.watch))
    except (OSError, TimeoutError) as exc:
        print(f"Bluetooth error: {exc}")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
