"""Error diffusion keeps the requested amount of ink."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dtfrip.core import Halftoner, packbits, _packbits_py  # noqa

LEVELS = [0.0, 0.13, 0.58, 1.0]
VOL = np.array(LEVELS)

for v in (0.02, 0.1, 0.3, 0.5, 0.8, 1.0):
    h = Halftoner(512, LEVELS, [0, 1, 2, 3])
    out = np.zeros((256, 512), np.uint8)
    for y in range(0, 256, 32):
        h.run(np.full((32, 512), v, np.float32), out[y:y + 32])
    got = VOL[out].mean()
    assert abs(got - v) < 0.01, (v, got)
print("OK  error diffusion: ink amount preserved within 1 %")

rng = np.random.default_rng(1)
for n in range(200):
    row = bytes(rng.choice([0, 0, 0, 255, 17], size=rng.integers(1, 700)).astype(np.uint8))
    assert packbits(row) == _packbits_py(row)
    # decode
    from dtfrip.escp2_decode import unpack_rle
    enc = packbits(row)
    dec, _ = unpack_rle(enc, 0, len(row))
    assert dec == row
print("OK  PackBits: C and Python encoders agree and decode back exactly")
