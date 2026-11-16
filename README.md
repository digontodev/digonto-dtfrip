# Digonto DTFRIP

Print and maintain an Epson L800 DTF printer (colour + white in one run)

This program is also inside [Digonto Studio](https://github.com/digontodev/digonto-studio), the download with every Digonto program.

Part of the **Digonto** programs - [digonto.dev](https://digonto.dev). Works completely offline: no account, no internet, no tracking.

## Download

Get the newest version from the **[Releases page](https://github.com/digontodev/digonto-dtfrip/releases/latest)**:

| System | File |
|---|---|
| Windows 10 / 11 (64-bit) | `Digonto-DTFRIP-<version>-Windows-Setup.exe` |
| macOS 11 or newer, Apple silicon (M1 and newer) | `Digonto-DTFRIP-<version>-macOS-arm64.dmg` |
| Ubuntu 24.04+ / Debian 13+ (64-bit) | `digonto-dtfrip_<version>_amd64.deb` |

- **Windows:** run the setup file. Windows may show "Windows protected your PC": click *More info* > *Run anyway* (the program is not signed yet).
- **macOS:** open the .dmg and drag the program into Applications. The first time, right-click it and choose *Open* (the program is not from the App Store).
- **Ubuntu / Debian:** `sudo apt install ./digonto-dtfrip_<version>_amd64.deb`

## Colour profiles

**Colour profiles are not included.** Printer and ink makers own their profiles, so they cannot be shared here.
Add the CMYK colour profile (`.icc` / `.icm`) of your own printer - from your printer or ink seller, or your RIP software -
in the program: **Settings > Add profile**, then choose it in the Print tab.

## Build it yourself

The installers are made by GitHub Actions (`.github/workflows/release.yml`) on Linux, macOS and Windows.
To build on your own computer: install the libraries in `requirements.txt` and PyInstaller, then run
`python packaging/build.py --root .. --apps digonto-dtfrip`.

To run from source: `pip install --require-hashes -r requirements.txt` then `python digonto_dtfrip.py`.

## Licence

GNU Affero General Public License v3.0 or later - see [LICENSE](LICENSE). Copyright (C) Digonto.
