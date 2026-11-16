DIGONTO DTFRIP  -  print and maintain an Epson L800 DTF printer (Ubuntu, macOS, Windows)
=========================================================================================
Part of the Digonto apps (digonto.dev). Based on the earlier "DTF RIP for Linux".

What it does
  * Prints PNG / TIFF / JPG / PDF / SVG on DTF film: colour first, white on top, in ONE run
    (ink order Y K W W M C, white in the two former light-cyan / light-magenta channels)
  * ICC colour management. Colour profiles are NOT included: add your printer's own profile
    (.icc / .icm, from your printer or ink seller) in Settings > Add profile.
  * White underbase with choke, soft or solid white, "white background = transparent",
    "no white under black", mirror, several pictures and copies on one sheet
  * Quality presets Draft / Standard / High / Maximum (up to 1440x1440 dpi)
  *   * Settings > Ink order: choose which ink is in which tank (default Y K W W M C); per-ink amount and curve
  * Settings > Printer / driver setup help (driver steps for Windows / macOS / Linux, opens Epson support and system printer settings)
  * Maintenance: nozzle check, head cleaning, power cleaning, head alignment, ink counters (Linux USB)
  * Test prints: channel check, ink density chart; keep-alive stripe after N idle hours

How it reaches the printer
  Ubuntu   direct USB (/dev/usb/lp0). The installer adds you to the 'lp' group - log out and in ONCE.
  Windows  install the Epson L800 driver once (so the printer exists in Windows). The program sends the print
           data RAW through the Windows print spooler - the Epson driver does not touch it.
  macOS    add the Epson L800 in System Settings > Printers & Scanners. The program sends the data RAW to that
           print queue (lp -o raw).
  If the printer is not found, open the panel > Settings > Printer and pick or type it
  (/dev/usb/lp0, cups:NAME or win:NAME).

Background service
  The installer starts a small background service at login (keep-alive for the white ink; it answers only this computer). Uninstall removes it.

Not included (same as before)
  * Waste ink counter reset  -> Epson L800 Adjustment Program (Windows)
  * Ink level reset          -> the ink button on the printer
  * Ink levels over the panel only work on Linux with a direct USB connection (needs escputil)

First prints: see the quality table in the panel; start with a small design at Standard.

Command line
  digonto-dtfrip print logo.png -w 120 -n 2 -q high
  digonto-dtfrip nozzle | clean | power-clean | ink | devices
  digonto-dtfrip test channels | density | keepalive
  (Windows: run from the app folder with  ...\venv\Scripts\python.exe digonto_dtfrip.py print ...)

Settings and uploads live in:  Ubuntu ~/.config/dtfrip + ~/.local/share/dtfrip
  macOS ~/Library/Application Support/DigontoDTFRIP    Windows %APPDATA%\DigontoDTFRIP
Existing Ubuntu settings of the old DTF RIP are kept and used.
