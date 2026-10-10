"""Build the final GHSF logo SVGs: text outlined, ghost tilt and placement baked in.

Geometry matches option C of concepts/logo-concepts-r4.html (viewfinder, ghost 1 at 10 degrees).
Run:  python build_logo.py   ->  writes logo/*.svg
"""
import math
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).parent
FONTS = HERE / "fonts"
OUT = HERE / "logo"

BLACK, LIME, DEEP, BONE = "#0B0D0A", "#8BE234", "#3F7A2A", "#EDEFE6"

# ---- affine helpers (SVG matrix a b c d e f) -------------------------------
def mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a*A + c*B, b*A + d*B, a*C + c*D, b*C + d*D, a*E + c*F + e, b*E + d*F + f)

def translate(x, y): return (1, 0, 0, 1, x, y)
def scale(s): return (s, 0, 0, s, 0, 0)
def rotate(deg, cx, cy):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return mul(translate(cx, cy), mul((c, s, -s, c, 0, 0), translate(-cx, -cy)))
def apply(m, p):
    a, b, c, d, e, f = m
    return (a*p[0] + c*p[1] + e, b*p[0] + d*p[1] + f)

# ---- shapes as lists of subpaths: [("M",(x,y)), ("C",p1,p2,p3), ("L",p), ("Z",)] ----
GHOST_BODY = [("M", (80, 8)), ("C", (42, 8), (22, 38), (22, 74)), ("L", (22, 128)),
              ("C", (22, 140), (34, 144), (42, 134)), ("C", (48, 126), (56, 126), (62, 136)),
              ("C", (68, 146), (92, 146), (98, 136)), ("C", (104, 126), (112, 126), (118, 134)),
              ("C", (126, 144), (138, 140), (138, 128)), ("L", (138, 74)),
              ("C", (138, 38), (118, 8), (80, 8)), ("Z",)]

def ellipse(cx, cy, rx, ry):
    k = 0.5522847498
    return [("M", (cx + rx, cy)),
            ("C", (cx + rx, cy + k*ry), (cx + k*rx, cy + ry), (cx, cy + ry)),
            ("C", (cx - k*rx, cy + ry), (cx - rx, cy + k*ry), (cx - rx, cy)),
            ("C", (cx - rx, cy - k*ry), (cx - k*rx, cy - ry), (cx, cy - ry)),
            ("C", (cx + k*rx, cy - ry), (cx + rx, cy - k*ry), (cx + rx, cy)), ("Z",)]

GHOST_FACE = [ellipse(61, 66, 9, 14), ellipse(99, 66, 9, 14), ellipse(80, 102, 7, 9)]

def bracket(cx, cy, dx, dy, w):
    """Filled outline of an L-shaped stroke with square caps (corner at cx,cy)."""
    h, sx, sy = w / 2, math.copysign(1, dx), math.copysign(1, dy)
    pts = [(cx - sx*h, cy + dy + sy*h), (cx - sx*h, cy - sy*h), (cx + dx + sx*h, cy - sy*h),
           (cx + dx + sx*h, cy + sy*h), (cx + sx*h, cy + sy*h), (cx + sx*h, cy + dy + sy*h)]
    return [("M", pts[0])] + [("L", p) for p in pts[1:]] + [("Z",)]

def fmt(n): return f"{n:.2f}".rstrip("0").rstrip(".")

def to_d(subpaths, m, bounds):
    out = []
    for sp in subpaths:
        for seg in sp:
            if seg[0] == "Z":
                out.append("Z"); continue
            pts = [apply(m, p) for p in seg[1:]]
            for x, y in pts:  # control-point bounds: conservative, fine for a viewBox
                bounds.add(x, y)
            out.append(seg[0] + " ".join(f"{fmt(x)},{fmt(y)}" for x, y in pts))
    return "".join(out)

class Bounds:
    def __init__(self): self.b = [math.inf, math.inf, -math.inf, -math.inf]
    def add(self, x, y):
        b = self.b; b[0] = min(b[0], x); b[1] = min(b[1], y); b[2] = max(b[2], x); b[3] = max(b[3], y)

# ---- text ------------------------------------------------------------------
def load(name, wght=None):
    f = TTFont(FONTS / name)
    return instantiateVariableFont(f, {"wght": wght}) if wght else f

def text_d(font, text, size, cx, baseline, spacing, bounds):
    # ponytail: no GPOS kerning (all-caps, few pairs); add uharfbuzz shaping if a pair looks off
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    s = size / font["head"].unitsPerEm
    names = [cmap[ord(ch)] for ch in text]
    width = sum(hmtx[n][0] * s for n in names) + spacing * (len(names) - 1)
    x, pen = cx - width / 2, SVGPathPen(gs, ntos=fmt)
    for n in names:
        t = (s, 0, 0, -s, x, baseline)
        gs[n].draw(TransformPen(pen, t))
        bp = BoundsPen(gs); gs[n].draw(bp)
        if bp.bounds:
            for px, py in ((bp.bounds[0], bp.bounds[1]), (bp.bounds[2], bp.bounds[3])):
                bounds.add(*apply(t, (px, py)))
        x += hmtx[n][0] * s + spacing
    return pen.getCommands()

# ---- build -----------------------------------------------------------------
def ghost_matrix(x, y, w, h):
    # <use> of a 160x156 symbol, preserveAspectRatio xMidYMid meet, then rotate(-10 80 78)
    k = min(w / 160, h / 156)
    place = mul(translate(x + (w - 160*k) / 2, y + (h - 156*k) / 2), scale(k))
    return mul(place, rotate(-10, 80, 78))

def svg(title, parts, bounds, pad=4):
    x0, y0, x1, y1 = bounds.b
    vb = f"{fmt(x0 - pad)} {fmt(y0 - pad)} {fmt(x1 - x0 + 2*pad)} {fmt(y1 - y0 + 2*pad)}"
    # evenodd only where a shape has holes (ghost face); glyphs can have overlapping contours
    body = "\n".join(f'  <path id="{i}" fill="{c}" fill-rule="{"evenodd" if i == "ghost" else "nonzero"}" d="{d}"/>'
                     for i, c, d in parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n  <title>{title}</title>\n'
            f"{body}\n</svg>\n")

def circle(cx, cy, r): return [ellipse(cx, cy, r, r)]

def build(kind, alfa, osw700, osw600):
    b = Bounds()
    if kind == "badge":
        gm = ghost_matrix(98, 34, 204, 199)
        corners, w = [(60, 20, 50, 50), (340, 20, -50, 50), (340, 240, -50, -50), (60, 240, 50, -50)], 12
        dot = circle(96, 54, 9)
        texts = [("ghsf", LIME, text_d(alfa, "GHSF", 80, 200, 320, 3, b)),
                 ("ghost-hunters", BONE, text_d(osw700, "GHOST HUNTERS", 34, 200, 360, 3, b)),
                 ("of-south-florida", LIME, text_d(osw600, "OF SOUTH FLORIDA", 26, 200, 394, 5, b))]
    else:
        gm = ghost_matrix(44, 14, 112, 109)
        corners, w = [(30, 12, 28, 28), (170, 12, -28, 28), (170, 128, -28, -28), (30, 128, 28, -28)], 9
        dot = circle(48, 30, 6)
        texts = [("ghsf", LIME, text_d(alfa, "GHSF", 52, 100, 188, 0, b))]
    frame = to_d([bracket(*c, w) for c in corners] + dot, (1, 0, 0, 1, 0, 0), b)
    ghost = to_d([GHOST_BODY] + GHOST_FACE, gm, b)  # evenodd: face is a true hole
    face = to_d(GHOST_FACE, gm, Bounds())
    full = [("frame", LIME, frame), ("ghost", BONE, ghost),
            ("ghost-face-black-thread", BLACK, face)] + texts
    mono = [("frame", "#000000", frame), ("ghost", "#000000", ghost)] + [(i, "#000000", d) for i, _, d in texts]
    # light garments: bone thread would vanish, so it becomes black and the face shows the shirt
    light = [(i, BLACK if c == BONE else c, d) for i, c, d in full if i != "ghost-face-black-thread"]
    name = "GHSF badge" if kind == "badge" else "GHSF hat mark"
    return svg(name, full, b), svg(name + " (one colour)", mono, b), svg(name + " (light garment)", light, b)

def main():
    # self-check: square-capped bracket outline and rotation math
    assert bracket(60, 20, 50, 50, 12)[:3] == [("M", (54, 76)), ("L", (54, 14)), ("L", (116, 14))]
    assert all(abs(a - b) < 1e-9 for a, b in zip(apply(rotate(-10, 80, 78), (80, 78)), (80, 78)))

    alfa = load("AlfaSlabOne-Regular.ttf")
    osw700, osw600 = load("Oswald-VF.ttf", 700), load("Oswald-VF.ttf", 600)
    OUT.mkdir(exist_ok=True)
    for kind in ("badge", "mark"):
        full, mono, light = build(kind, alfa, osw700, osw600)
        (OUT / f"ghsf-{kind}.svg").write_text(full, encoding="utf-8")
        (OUT / f"ghsf-{kind}-1color.svg").write_text(mono, encoding="utf-8")
        (OUT / f"ghsf-{kind}-light.svg").write_text(light, encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))

if __name__ == "__main__":
    main()
