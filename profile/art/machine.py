"""Animated cutaway of a High-NA EUV lithography scanner (dark + light SVG).

Run:  python profile/art/machine.py
Barlow (SIL OFL, profile/art/fonts) is subset and embedded so the SVG renders
identically inside GitHub's <img> sandbox, which cannot load external fonts.
"""
import base64
import io
import math
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

OUT = Path(__file__).parent
FONTS = OUT / "fonts"
CHARS = "".join(chr(c) for c in range(32, 127)) + "·₂µ–—×→°"

THEMES = {
    "light": dict(
        ground="#eef1f5", ink="#141c27", muted="#5b6673", leader="#8d98a6",
        shell="#ffffff", shell_line="#b7c0cb", seam="#d6dce3", cavity="#dde3ea",
        module="#f6f8fa", module_line="#97a2b0", mirror="#5d6b7c", mirror_hi="#ffffff",
        euv="#6a3df0", laser="#f2541b", stage="#c9d0d9", reticle="#273444", wafer="#3b4a5c",
        field="#d8dee6", exposed="#6a3df0", led="#2fbf71",
    ),
    "dark": dict(
        ground="#0f1318", ink="#e8edf3", muted="#97a3b1", leader="#56616e",
        shell="#cfd5dd", shell_line="#8f9aa7", seam="#b3bcc7", cavity="#161b22",
        module="#1e252e", module_line="#4e5a69", mirror="#a9b6c6", mirror_hi="#e9eef5",
        euv="#9c83ff", laser="#ff6a33", stage="#3a4552", reticle="#c3cdd9", wafer="#a8b6c6",
        field="#242c36", exposed="#9c83ff", led="#3ddc84",
    ),
}


def font_face(file, family, weight):
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga", "tnum"]
    f = TTFont(FONTS / file)
    sub = subset.Subsetter(opts)
    sub.populate(text=CHARS)
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face {{ font-family: '{family}'; font-weight: {weight}; src: url(data:font/woff;base64,{b64}) format('woff'); }}"


FACES = "\n".join([
    font_face("Barlow-Regular.ttf", "Barlow", 400),
    font_face("Barlow-SemiBold.ttf", "Barlow", 600),
    font_face("BarlowCondensed-Medium.ttf", "Barlow Condensed", 500),
])

# ---- geometry (machine coordinates; the whole machine is shifted down by OY)
OY = 92
P = (320, 460)              # plasma point
IF = (462, 318)             # intermediate focus
PATH = [IF, (615, 318), (540, 240), (720, 150), (810, 195), (690, 285), (860, 360), (700, 430), (790, 513)]
MIRRORS = PATH[1:-1]        # every bounce except the reticle is a mirror; reticle drawn separately
RETICLE = (720, 150)


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def mirror(prev, at, nxt, t, length=34):
    a = unit((prev[0] - at[0], prev[1] - at[1]))
    b = unit((nxt[0] - at[0], nxt[1] - at[1]))
    n = unit((a[0] + b[0], a[1] + b[1]))           # surface normal faces the light
    s = (-n[1], n[0])                               # surface direction
    h = length / 2
    x1, y1 = at[0] - s[0] * h, at[1] - s[1] * h
    x2, y2 = at[0] + s[0] * h, at[1] + s[1] * h
    bx, by = -n[0] * 5, -n[1] * 5                   # substrate thickness behind the coating
    return (
        f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} L{x2+bx:.1f},{y2+by:.1f} L{x1+bx:.1f},{y1+by:.1f} Z" fill="{t["mirror"]}"/>'
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["mirror_hi"]}" stroke-width="1.2"/>'
    )


def label(anchor, text_xy, text, t, anchor_mode="middle", elbow=None):
    ax, ay = anchor
    tx, ty = text_xy
    pts = [(ax, ay)] + ([elbow] if elbow else []) + [(tx, ty + (8 if ty > ay else -16))]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (
        f'<path d="{d}" fill="none" stroke="{t["leader"]}" stroke-width="1"/>'
        f'<circle cx="{ax}" cy="{ay}" r="2.5" fill="{t["leader"]}"/>'
        f'<text x="{tx}" y="{ty}" class="lbl" text-anchor="{anchor_mode}">{text}</text>'
    )


def wafer_inset(t, cx, cy, r):
    pitch_x, pitch_y = 14, 17
    fields = []
    for j in range(-6, 7):
        y = cy + j * pitch_y - pitch_y / 2
        row = []
        for i in range(-7, 8):
            x = cx + i * pitch_x - pitch_x / 2
            if all(math.hypot(px - cx, py - cy) < r - 5 for px, py in
                   [(x, y), (x + pitch_x - 2, y), (x, y + pitch_y - 2), (x + pitch_x - 2, y + pitch_y - 2)]):
                row.append((x, y))
        if row:
            fields.append(row if len(fields) % 2 == 0 else row[::-1])   # serpentine exposure order
    order = [f for row in fields for f in row]
    n = len(order)
    css, els = [], []
    for k, (x, y) in enumerate(order):
        s = 4 + 84 * k / n
        css.append(
            f"@keyframes f{k} {{ 0%,{s:.2f}% {{ fill: {t['field']}; }} {s+0.6:.2f}% {{ fill: {t['mirror_hi']}; }} "
            f"{s+2.2:.2f}%,93% {{ fill: {t['exposed']}; fill-opacity: .55; }} 97%,100% {{ fill: {t['field']}; }} }}"
        )
        els.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{pitch_x-2}" height="{pitch_y-2}" rx="1.5" style="animation: f{k} 14s linear infinite"/>')
    svg = (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{t["module"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'
        f'<path d="M{cx-7},{cy+r-0.5} a7,7 0 0,1 14,0" fill="{t["ground"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'
        f'<g fill="{t["field"]}">{"".join(els)}</g>'
    )
    return svg, "\n".join(css)


def build(t):
    W, H = 1200, 800
    css_fields = ""

    shell = f"""
<rect x="214" y="96" width="754" height="456" rx="20" fill="{t['shell']}" stroke="{t['shell_line']}" stroke-width="1.5"/>
<rect x="232" y="112" width="718" height="424" rx="12" fill="{t['cavity']}"/>
<rect x="232" y="112" width="718" height="424" rx="12" fill="url(#grid)" opacity=".7"/>
<rect x="196" y="552" width="790" height="10" rx="2" fill="{t['shell_line']}"/>
<rect x="220" y="562" width="40" height="8" fill="{t['shell_line']}"/><rect x="922" y="562" width="40" height="8" fill="{t['shell_line']}"/>
<rect x="262" y="70" width="250" height="30" rx="10" fill="{t['shell']}" stroke="{t['shell_line']}" stroke-width="1.5"/>
<rect x="560" y="60" width="380" height="40" rx="12" fill="{t['shell']}" stroke="{t['shell_line']}" stroke-width="1.5"/>
<g stroke="{t['seam']}" stroke-width="1.2">
  <line x1="420" y1="96" x2="420" y2="112"/><line x1="660" y1="96" x2="660" y2="112"/><line x1="900" y1="96" x2="900" y2="112"/>
  <line x1="420" y1="536" x2="420" y2="552"/><line x1="620" y1="536" x2="620" y2="552"/><line x1="214" y1="320" x2="232" y2="320"/><line x1="950" y1="320" x2="968" y2="320"/>
  <line x1="600" y1="68" x2="600" y2="100"/><line x1="900" y1="68" x2="900" y2="100"/>
</g>
<g fill="{t['seam']}"><rect x="290" y="80" width="3" height="12" rx="1"/><rect x="299" y="80" width="3" height="12" rx="1"/><rect x="308" y="80" width="3" height="12" rx="1"/><rect x="317" y="80" width="3" height="12" rx="1"/><rect x="326" y="80" width="3" height="12" rx="1"/><rect x="335" y="80" width="3" height="12" rx="1"/><rect x="344" y="80" width="3" height="12" rx="1"/><rect x="353" y="80" width="3" height="12" rx="1"/><rect x="362" y="80" width="3" height="12" rx="1"/><rect x="371" y="80" width="3" height="12" rx="1"/><rect x="380" y="80" width="3" height="12" rx="1"/><rect x="389" y="80" width="3" height="12" rx="1"/><rect x="398" y="80" width="3" height="12" rx="1"/></g>
<path d="M232,524 V124 a12,12 0 0,1 12,-12 H938" fill="none" stroke="{t['shell_line']}" stroke-opacity=".55" stroke-width="3"/>
<rect x="878" y="78" width="44" height="4" rx="2" class="led" fill="{t['led']}"/>
"""

    vessel = f'<rect x="238" y="334" width="208" height="196" rx="16" fill="{t["module"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'
    illum = f'<rect x="478" y="186" width="176" height="156" rx="12" fill="{t["module"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'
    pob = f'<rect x="668" y="174" width="226" height="306" rx="14" fill="{t["module"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'
    neck = f'<path d="M430,346 L462,318 L486,330 L446,372 Z" fill="{t["module"]}" stroke="{t["module_line"]}" stroke-width="1.5"/>'

    # collector: ellipsoidal shell around the plasma, facing the intermediate focus
    a0, a1, rc = math.radians(70), math.radians(200), 70
    c0 = (P[0] + rc * math.cos(a0), P[1] + rc * math.sin(a0))
    c1 = (P[0] + rc * math.cos(a1), P[1] + rc * math.sin(a1))
    hole = (P[0] + rc * math.cos(math.radians(135)), P[1] + rc * math.sin(math.radians(135)))
    collector = (
        f'<path d="M{c0[0]:.1f},{c0[1]:.1f} A{rc},{rc} 0 0,1 {c1[0]:.1f},{c1[1]:.1f}" fill="none" stroke="{t["mirror"]}" stroke-width="7" stroke-linecap="round"/>'
        f'<path d="M{c0[0]:.1f},{c0[1]:.1f} A{rc},{rc} 0 0,1 {c1[0]:.1f},{c1[1]:.1f}" fill="none" stroke="{t["mirror_hi"]}" stroke-width="1.2" transform="translate({P[0]},{P[1]}) scale(.955) translate({-P[0]},{-P[1]})"/>'
        f'<circle cx="{hole[0]:.1f}" cy="{hole[1]:.1f}" r="4.5" fill="{t["module"]}"/>'
    )
    cone = f'<path d="M{c0[0]:.1f},{c0[1]:.1f} L{IF[0]},{IF[1]} L{c1[0]:.1f},{c1[1]:.1f} A{rc},{rc} 0 0,0 {c0[0]:.1f},{c0[1]:.1f} Z" fill="url(#cone)" class="cone"/>'

    beam_d = "M" + " L".join(f"{x},{y}" for x, y in PATH)
    beam = (
        f'<path d="{beam_d}" fill="none" stroke="{t["euv"]}" stroke-opacity=".22" stroke-width="9" stroke-linejoin="round"/>'
        f'<path d="{beam_d}" fill="none" stroke="{t["euv"]}" stroke-width="2.2" stroke-linejoin="round" stroke-dasharray="3 9" class="photons"/>'
    )
    mirrors = "".join(mirror(PATH[i - 1], PATH[i], PATH[i + 1], t) for i in range(1, len(PATH) - 1) if PATH[i] != RETICLE)

    nozzle = (
        f'<rect x="308" y="318" width="24" height="26" rx="3" fill="{t["stage"]}" stroke="{t["module_line"]}"/>'
        f'<path d="M314,344 L326,344 L320,354 Z" fill="{t["module_line"]}"/>'
        + "".join(f'<circle cx="{P[0]}" cy="0" r="2.6" fill="{t["mirror"]}" class="drop" style="animation-delay:{-k*0.24:.2f}s"/>' for k in range(5))
    )
    laser_box = (
        f'<rect x="40" y="496" width="150" height="72" rx="10" fill="{t["shell"]}" stroke="{t["shell_line"]}" stroke-width="1.5"/>'
        f'<text x="56" y="526" class="lbl" style="fill:#141c27">CO₂ drive laser</text>'
        f'<text x="56" y="548" class="sub" style="fill:#5b6673">10.6 µm, pulsed</text>'
        f'<rect x="168" y="526" width="22" height="16" fill="{t["stage"]}"/>'
    )
    laser = (
        f'<path d="M190,534 L{hole[0]:.1f},{hole[1]:.1f} L{P[0]},{P[1]}" fill="none" stroke="{t["laser"]}" stroke-width="2.4" stroke-dasharray="14 10" class="laser"/>'
    )
    plasma = (
        f'<circle cx="{P[0]}" cy="{P[1]}" r="20" fill="url(#plasma)" class="plasma"/>'
        f'<circle cx="{P[0]}" cy="{P[1]}" r="3.2" fill="#ffffff"/>'
    )

    reticle_stage = (
        f'<rect x="590" y="118" width="316" height="22" rx="5" fill="{t["stage"]}" stroke="{t["module_line"]}"/>'
        f'<g class="rscan"><rect x="652" y="140" width="136" height="8" rx="1.5" fill="{t["reticle"]}"/>'
        f'<rect x="664" y="148" width="112" height="2" fill="{t["mirror_hi"]}" opacity=".8"/></g>'
    )
    wafer_stage = (
        f'<rect x="640" y="526" width="316" height="22" rx="5" fill="{t["stage"]}" stroke="{t["module_line"]}"/>'
        f'<g class="wscan"><rect x="700" y="516" width="180" height="10" rx="2" fill="{t["module_line"]}"/>'
        f'<rect x="715" y="511" width="150" height="4" rx="1" fill="{t["wafer"]}"/></g>'
    )

    inset, css_fields = wafer_inset(t, 1080, 372, 84)

    labels = "".join([
        label((320, 320), (320, 44), "Tin droplet generator", t),
        label((566, 190), (560, 44), "Illuminator", t),
        label((748, 118), (748, 44), "Reticle stage", t),
        label((894, 300), (902, 44), "Projection optics", t, elbow=(902, 300)),
        label((262, 470), (262, 622), "Collector mirror", t, elbow=(262, 470)),
        label((P[0] + 6, P[1] + 6), (400, 622), "Tin plasma · 13.5 nm", t, elbow=(400, 520)),
        label(IF, (540, 622), "Intermediate focus", t, elbow=(540, 360)),
        label((800, 548), (800, 622), "Wafer stage", t),
    ])
    inset_link = f'<path d="M880,518 C940,518 960,440 996,420" fill="none" stroke="{t["leader"]}" stroke-dasharray="3 4"/>'
    inset_lbl = f'<text x="1080" y="490" class="lbl" text-anchor="middle">Wafer, top view</text><text x="1080" y="510" class="sub" text-anchor="middle">fields exposed in scan order</text>'

    style = f"""
{FACES}
.name {{ font: 600 46px 'Barlow', sans-serif; fill: {t['ink']}; letter-spacing: -0.01em; }}
.lead {{ font: 400 19px 'Barlow', sans-serif; fill: {t['muted']}; }}
.lbl {{ font: 500 15px 'Barlow Condensed', sans-serif; fill: {t['ink']}; letter-spacing: .02em; }}
.sub {{ font: 400 13px 'Barlow', sans-serif; fill: {t['muted']}; }}
.cap {{ font: 400 13.5px 'Barlow', sans-serif; fill: {t['muted']}; }}
.photons {{ animation: flow .9s linear infinite; }}
@keyframes flow {{ to {{ stroke-dashoffset: -12; }} }}
.laser {{ animation: laser .45s linear infinite; }}
@keyframes laser {{ 0% {{ stroke-dashoffset: 0; opacity: 1; }} 50% {{ opacity: .35; }} 100% {{ stroke-dashoffset: -24; opacity: 1; }} }}
.plasma {{ transform-box: fill-box; transform-origin: center; animation: plasma .24s ease-out infinite; }}
@keyframes plasma {{ 0% {{ transform: scale(.45); opacity: 1; }} 100% {{ transform: scale(1.15); opacity: .15; }} }}
.cone {{ animation: cone .24s ease-out infinite; }}
@keyframes cone {{ 0% {{ opacity: 1; }} 100% {{ opacity: .55; }} }}
.drop {{ animation: drop 1.2s linear infinite; }}
@keyframes drop {{ 0% {{ transform: translateY(356px); opacity: 1; }} 92% {{ opacity: 1; }} 100% {{ transform: translateY({P[1]}px); opacity: 0; }} }}
.rscan {{ animation: rscan 3.5s ease-in-out infinite alternate; }}
@keyframes rscan {{ from {{ transform: translateX(-46px); }} to {{ transform: translateX(46px); }} }}
.wscan {{ animation: wscan 3.5s ease-in-out infinite alternate; }}
@keyframes wscan {{ from {{ transform: translateX(11.5px); }} to {{ transform: translateX(-11.5px); }} }}
.led {{ animation: led 2.4s ease-in-out infinite; }}
@keyframes led {{ 50% {{ opacity: .35; }} }}
{css_fields}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""
    defs = f"""
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24,0H0V24" fill="none" stroke="{t['seam']}" stroke-opacity=".35" stroke-width=".8"/></pattern>
  <radialGradient id="plasma"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="{t['euv']}" stop-opacity=".9"/><stop offset="1" stop-color="{t['euv']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="cone" gradientUnits="userSpaceOnUse" x1="{P[0]}" y1="{P[1]}" x2="{IF[0]}" y2="{IF[1]}">
    <stop offset="0" stop-color="{t['euv']}" stop-opacity=".30"/><stop offset="1" stop-color="{t['euv']}" stop-opacity=".08"/>
  </linearGradient>
</defs>"""

    body = f"""{defs}
<rect width="{W}" height="{H}" rx="16" fill="{t['ground']}"/>
<text x="48" y="64" class="name">Sebastian Kallfelz</text>
<text x="50" y="96" class="lead">Microelectronics at KIT · tools for lithography, process and yield</text>
<g transform="translate(0,{OY})">
{shell}
{laser_box}
{vessel}{neck}{illum}{pob}
{cone}
{beam}
{collector}
{mirrors}
{nozzle}
{laser}
{plasma}
{reticle_stage}
{wafer_stage}
{inset_link}
{inset}
{inset_lbl}
{labels}
</g>
<text x="48" y="{H-28}" class="cap">High-NA EUV scanner, cut away. A CO₂ laser turns tin droplets into plasma; its 13.5 nm light travels by mirrors only, from mask to wafer. Illustration, not to scale.</text>
"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Sebastian Kallfelz. Animated cutaway of a High-NA EUV lithography scanner, light running from tin plasma through mirrors to the wafer.">\n'
        f"<style>{style}</style>\n{body}</svg>\n"
    )


if __name__ == "__main__":
    for name, t in THEMES.items():
        (OUT / f"machine-{name}.svg").write_text(build(t), encoding="utf-8")
    print("ok")
