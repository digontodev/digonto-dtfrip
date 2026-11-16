"""Verify our ESC/P2 output lands every dot exactly where Gutenprint would put it."""
import io
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dtfrip.escp2 import JobGeometry, JobWriter, dot_mask, nozzle_groups, simple_groups  # noqa
from dtfrip.escp2_decode import COLOR_NAMES, decode, render  # noqa
from dtfrip.modes import RESOLUTIONS  # noqa

REF = Path(__file__).resolve().parent / "ref"   # Gutenprint 5.3.4 output, escp2-artisan50


def make_job(resname, planes, groups, feed, top_pt=0, left_pt=9):
    res = RESOLUTIONS[resname]
    buf = io.BytesIO()
    jw = JobWriter(buf, JobGeometry(res, left_pt=left_pt, top_pt=top_pt, unidirectional=False))
    jw.header(); jw.passes(planes, groups, feed, dot_mask()); jw.footer()
    return buf.getvalue()


def dots_of(data, res):
    cmds, st, dots = decode(data)
    return cmds, render(dots, st, res.vres, res.hres)


def band_planes(res, rows_img=360, width_in=1.0, band=(100, 110)):
    fy = res.vres // 720
    H = rows_img * fy; W = int(width_in * res.hres)
    p = np.zeros((H, W), np.uint8); p[band[0] * fy:band[1] * fy] = 3
    return {c: p for c in ["K", "C", "LC", "M", "LM", "Y"]}


def check_vs_gutenprint(resname, feed, passes):
    res = RESOLUTIONS[resname]
    planes = band_planes(res)
    data = make_job(resname, planes, simple_groups(feed, passes, list(planes)), feed)
    _, ours = dots_of(data, res)
    ref = REF / {"720x720": "band_720sw.prn", "1440x720": "band_1440x720sw.prn",
                 "1440x1440": "band_1440x1440ov.prn"}[resname]
    _, theirs = dots_of(ref.read_bytes(), res)
    for code, (y, x, l, p) in ours.items():
        ty, tx, tl, tp = theirs[code]
        a = set(zip(y.tolist(), x.tolist())); b = set(zip(ty.tolist(), tx.tolist()))
        assert len(a) == len(y), f"{COLOR_NAMES[code]}: a pixel was printed twice"
        assert a == b, f"{resname} {COLOR_NAMES[code]}: positions differ ({len(a ^ b)} dots)"
    print(f"OK  {resname}: identical dot positions to Gutenprint for all 6 channels")


def check_split(resname, feed, pc, pw):
    """Full block: every pixel exactly once per channel; white always after colour."""
    res = RESOLUTIONS[resname]
    fy = res.vres // 720
    H = 300 * fy; W = int(0.5 * res.hres)
    rng = np.random.default_rng(0)
    planes = {c: rng.integers(1, 4, size=(H, W), dtype=np.uint8) for c in ["K", "C", "M", "Y", "LC", "LM"]}
    groups = nozzle_groups(feed, pc, pw, colour_first=True)
    data = make_job(resname, planes, groups, feed, top_pt=36)
    cmds, out = dots_of(data, res)
    top = res.vres + 36 * res.vres // 72
    shift = {"LC": res.head_shift, "M": res.head_shift, "Y": res.head_shift}
    last_colour = np.full(H, -1); first_white = np.full(H, 10**9)
    for code, (y, x, l, p) in out.items():
        name = COLOR_NAMES[code]
        yy = y - top - shift.get(name, 0)
        img = np.zeros((H, W), np.int32)
        np.add.at(img, (yy, x), 1)
        assert img.min() == 1 and img.max() == 1, f"{name}: coverage {img.min()}..{img.max()} (want exactly 1)"
        rec = np.zeros((H, W), np.uint8); rec[yy, x] = l
        assert np.array_equal(rec, planes[name]), f"{name}: dot levels differ"
        if name in ("LC", "LM"):
            np.minimum.at(first_white, yy, p)
        else:
            np.maximum.at(last_colour, yy, p)
    gap = (first_white - last_colour).min()
    assert gap > 0, "white printed before colour finished on some row"
    npass = len({c[6] for c in cmds if c[0] == "ESC i"})
    print(f"OK  {resname} split feed={feed} colour {pc}p / white {pw}p: every dot once, "
          f"white starts >= {gap} passes after colour on every row ({npass} head passes)")


if __name__ == "__main__":
    check_vs_gutenprint("1440x720", 45, 2)
    check_vs_gutenprint("1440x1440", 45, 2)
    check_vs_gutenprint("720x720", 45, 2)
    for resname, feed, pc, pw in [("720x720", 43, 1, 1), ("1440x720", 21, 2, 2),
                                  ("1440x1440", 11, 4, 4), ("1440x1440", 7, 6, 6),
                                  ("2880x1440", 11, 4, 4)]:
        check_split(resname, feed, pc, pw)


def check_header(resname, ref_name):
    res = RESOLUTIONS[resname]
    buf = io.BytesIO()
    jw = JobWriter(buf, JobGeometry(res, unidirectional=False)); jw.header()
    ref = (REF / ref_name).read_bytes()
    ref_hdr = ref[:ref.find(b"\x1b(v")]
    assert buf.getvalue() == ref_hdr, f"{resname}: header differs\n{buf.getvalue()!r}\n{ref_hdr!r}"
    jw2 = JobWriter(io.BytesIO(), JobGeometry(res)); jw2.footer()
    print(f"OK  {resname}: job header byte-identical to Gutenprint")


if __name__ == "__main__":
    check_header("720x720", "r_720sw.prn")
    check_header("1440x720", "r_1440x720sw.prn")
    check_header("1440x1440", "r_1440x1440ov.prn")
    check_header("2880x1440", "r_2880x1440sw.prn")
