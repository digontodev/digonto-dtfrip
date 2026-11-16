"""Render a .prn file the way it would come out of the printer (low-res simulation).

usage: python3 tests/simulate.py job.prn out.png [vres hres]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dtfrip.escp2_decode import COLOR_NAMES, decode  # noqa


def simulate(prn, vres, hres, scale=8):
    data = Path(prn).read_bytes()
    pitch = vres // 90
    Hc, Wc = (vres * 14) // scale + 2, (hres * 9) // scale + 2   # A4 + 1" top offset
    acc = {}

    def sink(color, xs, ys, lvl, vpos, hpos, pno, st):
        y = (vpos * vres // st["v_unit"] + ys * pitch) // scale
        x = (hpos * hres // st["h_unit"] + xs * (hres // st["base_h"])) // scale
        a = acc.setdefault(color, np.zeros((Hc, Wc), np.float32))
        np.add.at(a, (y, x), lvl.astype(np.float32) / 3.0)

    decode(data, sink=sink)
    tot = sum(acc.values())
    ys, xs = np.nonzero(tot)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return {COLOR_NAMES[c]: np.clip(a[y0:y1, x0:x1] / (scale * scale), 0, 1) for c, a in acc.items()}


def picture(ink, mirror_back=True):
    """Transfer seen on a black shirt: white base under the colour layer."""
    z = np.zeros_like(next(iter(ink.values())))
    C, M, Y, K = (ink.get(k, z) for k in "CMYK")
    Wt = np.clip(ink.get("LC", z) + ink.get("LM", z), 0, 1)
    base = np.dstack([Wt] * 3) * 240 + 25 * (1 - np.dstack([Wt] * 3))
    col = np.dstack([(1 - C) * (1 - K), (1 - M) * (1 - K), (1 - Y) * (1 - K)])
    img = base * col
    if mirror_back:
        img = img[:, ::-1]; Wt = Wt[:, ::-1]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), Image.fromarray((Wt * 255).astype(np.uint8))


if __name__ == "__main__":
    prn, out = sys.argv[1], sys.argv[2]
    vres = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
    hres = int(sys.argv[4]) if len(sys.argv) > 4 else 1440
    ink = simulate(prn, vres, hres)
    a, b = picture(ink)
    a.save(out); b.save(out.replace(".png", "_white.png"))
    print({k: round(float(v.mean()), 3) for k, v in ink.items()})
