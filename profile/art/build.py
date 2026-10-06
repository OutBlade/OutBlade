"""Generate the profile README artwork (dark + light variant of each SVG).

Run from anywhere:  python profile/art/build.py
Everything is plain SVG + CSS/SMIL animation so it renders inside GitHub <img>.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).parent

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    "dark": dict(
        bg="#0b0f17", panel="#111826", border="#263248", grid="#1b2536",
        text="#e6edf3", muted="#8b949e", faint="#3b4658", accent="#58a6ff",
        diff="#3fb950", poly="#f85149", m1="#2f81f7", m2="#a371f7", via="#e3b341", cyan="#39c5cf",
    ),
    "light": dict(
        bg="#ffffff", panel="#f6f8fa", border="#d0d7de", grid="#e8edf2",
        text="#1f2328", muted="#57606a", faint="#afb8c1", accent="#0969da",
        diff="#1a7f37", poly="#cf222e", m1="#0969da", m2="#8250df", via="#9a6700", cyan="#1b7c83",
    ),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, label, style, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">\n<style>\n{style}\n</style>\n{body}\n</svg>\n'
    )


def frame(w, h, t):
    """Rounded panel with a dashed scribe line and alignment crosses in the corners."""
    marks = []
    for x, y in [(22, 22), (w - 22, 22), (22, h - 22), (w - 22, h - 22)]:
        marks.append(
            f'<path d="M{x-7},{y}h14M{x},{y-7}v14" stroke="{t["faint"]}" stroke-width="1.5"/>'
        )
    return (
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>\n'
        f'<rect x="12" y="12" width="{w-24}" height="{h-24}" rx="8" fill="none" stroke="{t["grid"]}" stroke-dasharray="2 6"/>\n'
        + "\n".join(marks)
    )


def hatch_defs(t):
    return (
        "<defs>"
        f'<pattern id="hm1" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="6" height="6" fill="{t["m1"]}" fill-opacity=".18"/><path d="M0,0v6" stroke="{t["m1"]}" stroke-width="1.6" stroke-opacity=".7"/></pattern>'
        f'<pattern id="hm2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">'
        f'<rect width="6" height="6" fill="{t["m2"]}" fill-opacity=".14"/><path d="M0,0v6" stroke="{t["m2"]}" stroke-width="1.6" stroke-opacity=".7"/></pattern>'
        f'<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{t["grid"]}"/></pattern>'
        "</defs>"
    )


# --------------------------------------------------------------------------- banner
def banner(t):
    W, H = 1200, 380
    rnd = random.Random(7)
    L0, L1 = 600, 1168  # layout region
    shapes = []

    rows = [(52, 88), (146, 88), (240, 88)]
    for ry, rh in rows:
        # power rails (metal1)
        shapes.append(f'<rect x="{L0}" y="{ry}" width="{L1-L0}" height="9" fill="url(#hm1)" stroke="{t["m1"]}"/>')
        shapes.append(f'<rect x="{L0}" y="{ry+rh-9}" width="{L1-L0}" height="9" fill="url(#hm1)" stroke="{t["m1"]}"/>')
        x = L0 + rnd.randint(0, 20)
        while x < L1 - 70:
            cw = rnd.choice([60, 80, 100, 120])
            cw = min(cw, L1 - 10 - x)
            for dy in (18, 52):  # pmos / nmos diffusion
                shapes.append(
                    f'<rect x="{x}" y="{ry+dy}" width="{cw}" height="18" fill="{t["diff"]}" fill-opacity=".2" stroke="{t["diff"]}"/>'
                )
            gx = x + 14
            while gx < x + cw - 10:
                shapes.append(
                    f'<rect x="{gx}" y="{ry+12}" width="5" height="64" fill="{t["poly"]}" fill-opacity=".55" stroke="{t["poly"]}"/>'
                )
                cy = ry + (24 if rnd.random() < .5 else 58)
                shapes.append(f'<rect x="{gx+9}" y="{cy}" width="6" height="6" fill="{t["via"]}"/>')
                gx += 20
            if rnd.random() < .7:  # local metal1 strap
                shapes.append(
                    f'<rect x="{x+8}" y="{ry+40}" width="{max(cw-16, 20)}" height="7" fill="url(#hm1)" stroke="{t["m1"]}"/>'
                )
            x += cw + 12
    # metal2 verticals spanning rows, with vias at the ends
    for mx in range(L0 + 36, L1 - 20, 74):
        mx += rnd.randint(-8, 8)
        y0 = rnd.choice([44, 60, 138])
        y1 = rnd.choice([240, 300, 330])
        shapes.append(f'<rect x="{mx}" y="{y0}" width="9" height="{y1-y0}" fill="url(#hm2)" stroke="{t["m2"]}"/>')
        for vy in (y0 + 3, y1 - 9):
            shapes.append(
                f'<g><rect x="{mx+1.5}" y="{vy}" width="6" height="6" fill="{t["via"]}"/></g>'
            )

    legend = []
    lx = 896
    for name, col in [("DIFF", "diff"), ("POLY", "poly"), ("M1", "m1"), ("M2", "m2"), ("VIA", "via")]:
        legend.append(f'<rect x="{lx}" y="345" width="10" height="10" fill="{t[col]}" fill-opacity=".8"/>')
        legend.append(f'<text x="{lx+15}" y="354" class="mono s11 muted">{name}</text>')
        lx += 15 + len(name) * 7 + 18

    style = f"""
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
.muted {{ fill: {t['muted']}; }}
.s11 {{ font-size: 11px; }}
.scan {{ animation: scan 7s cubic-bezier(.45,.05,.55,.95) infinite alternate; }}
@keyframes scan {{ from {{ transform: translateX({L0}px); }} to {{ transform: translateX({L1-4}px); }} }}
.cursor {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.sel {{ animation: sel 3.5s ease-in-out infinite; }}
@keyframes sel {{ 0%,100% {{ stroke-opacity: .25; }} 50% {{ stroke-opacity: 1; }} }}
"""
    body = f"""{hatch_defs(t)}
<defs>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="{t['bg']}" stop-opacity="1"/>
    <stop offset="1" stop-color="{t['bg']}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="beam" x1="0" x2="1">
    <stop offset="0" stop-color="{t['accent']}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{t['accent']}" stop-opacity=".35"/>
    <stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="lay"><rect x="{L0}" y="36" width="{L1-L0}" height="300"/></clipPath>
</defs>
{frame(W, H, t)}
<rect x="24" y="24" width="{W-48}" height="{H-48}" fill="url(#dots)"/>
<g clip-path="url(#lay)">
{chr(10).join(shapes)}
<rect x="{L0}" y="36" width="160" height="300" fill="url(#fade)"/>
<g class="scan"><rect x="-22" y="36" width="44" height="300" fill="url(#beam)"/><rect x="-0.75" y="36" width="1.5" height="300" fill="{t['accent']}"/></g>
</g>
<rect class="sel" x="836" y="140" width="148" height="100" fill="none" stroke="{t['accent']}" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="836" y="134" class="mono s11" fill="{t['accent']}">CELL lenz_lens_res_0</text>

<text x="56" y="76" class="mono" font-size="13" fill="{t['muted']}" letter-spacing="1.5">DIE SK-01  ·  LOT OB-2026  ·  KARLSRUHE, DE</text>
<text x="54" y="148" class="sans" font-size="52" font-weight="700" fill="{t['text']}">Sebastian Kallfelz</text>
<text x="56" y="190" class="sans" font-size="21" font-weight="600" fill="{t['accent']}">Semiconductor process · Lithography · Yield</text>
<text x="56" y="226" class="sans" font-size="16" fill="{t['muted']}">Microelectronics (ETIT B.Sc.) · Karlsruhe Institute of Technology</text>
<text x="56" y="250" class="sans" font-size="16" fill="{t['muted']}">Research assistant · Institute of Microstructure Technology</text>
<rect x="56" y="282" width="282" height="30" rx="4" fill="{t['panel']}" stroke="{t['border']}"/>
<text x="68" y="302" xml:space="preserve" class="mono" font-size="13" fill="{t['text']}"><tspan fill="{t['diff']}">&gt;</tspan> X 12.400 µm  Y 08.150 µm  M1</text>
<rect class="cursor" x="318" y="290" width="8" height="15" fill="{t['accent']}"/>
{chr(10).join(legend)}
"""
    return svg(W, H, "Sebastian Kallfelz: semiconductor process, lithography and yield, drawn as a chip layout", style, body)


# --------------------------------------------------------------------------- datasheet
def datasheet(t):
    W, H = 1200, 740
    feats = [
        ("diff", "ETIT B.Sc., Karlsruhe Institute of Technology (KIT)"),
        ("diff", "Research assistant, IMT · Korvink group"),
        ("poly", "Superconducting Lenz-lens resonators for NMR"),
        ("poly", "Process models: Deal–Grove, implantation, plasma etch"),
        ("m1", "Lithography: resolution, DoF, OPC, GDSII / e-beam"),
        ("m1", "Analog IC design on the SKY130 open PDK + ngspice"),
        ("m2", "ML yield prediction, SPC and Bayesian DOE"),
    ]
    fl = []
    for i, (c, s) in enumerate(feats):
        y = 186 + i * 30
        fl.append(f'<rect x="50" y="{y-10}" width="9" height="9" fill="{t[c]}"/>')
        fl.append(f'<text x="70" y="{y}" class="sans" font-size="15" fill="{t["text"]}">{esc(s)}</text>')

    # DIP-12 package drawing
    bx, by, bw, bh = 836, 174, 150, 196
    left = ["PYTHON", "C++", "TYPESCRIPT", "VHDL", "SPICE", "GDSII"]
    right = ["SKY130", "KLAYOUT", "OPENROAD", "COMSOL", "ANSYS", "LATEX"]
    pins = []
    for i in range(6):
        y = by + 26 + i * 29
        pins.append(f'<rect x="{bx-22}" y="{y-5}" width="22" height="10" fill="{t["faint"]}"/>')
        pins.append(f'<rect x="{bx+bw}" y="{y-5}" width="22" height="10" fill="{t["faint"]}"/>')
        pins.append(f'<text x="{bx+8}" y="{y+4}" class="mono" font-size="11" fill="{t["muted"]}">{i+1}</text>')
        pins.append(f'<text x="{bx+bw-8}" y="{y+4}" class="mono" font-size="11" fill="{t["muted"]}" text-anchor="end">{12-i}</text>')
        pins.append(f'<text x="{bx-32}" y="{y+4}" class="mono" font-size="12" fill="{t["text"]}" text-anchor="end">{left[i]}</text>')
        pins.append(f'<text x="{bx+bw+32}" y="{y+4}" class="mono" font-size="12" fill="{t["text"]}">{right[i]}</text>')

    rows = [
        ("Operating location", "LOC", "Karlsruhe, Germany", "—"),
        ("Process window", "λ", "Litho · Oxidation · Implant · Etch", "front-end"),
        ("Design kit", "PDK", "SkyWater SKY130", "130 nm"),
        ("Simulation stack", "SIM", "ngspice · COMSOL · Ansys", "multiphysics"),
        ("Open-source output", "N_repo", "30+", "repositories"),
        ("Collaboration", "I_collab", "Open", "EDA · process · tooling"),
    ]
    cols = [48, 420, 560, 920]
    tl = [
        f'<rect x="40" y="446" width="{W-80}" height="32" fill="{t["panel"]}" stroke="{t["border"]}"/>',
    ]
    for x, h in zip(cols, ["PARAMETER", "SYMBOL", "VALUE", "UNIT / NOTE"]):
        tl.append(f'<text x="{x+8}" y="467" class="mono" font-size="12" font-weight="700" fill="{t["muted"]}" letter-spacing="1">{h}</text>')
    for i, r in enumerate(rows):
        y = 478 + i * 32
        tl.append(f'<line x1="40" y1="{y+32}" x2="{W-40}" y2="{y+32}" stroke="{t["grid"]}"/>')
        fonts = ["sans", "mono", "sans", "sans"]
        fills = [t["text"], t["accent"], t["text"], t["muted"]]
        for x, v, f, c in zip(cols, r, fonts, fills):
            tl.append(f'<text x="{x+8}" y="{y+21}" class="{f}" font-size="14" fill="{c}">{esc(v)}</text>')

    style = f"""
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
.pin1 {{ animation: pulse 2s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
"""
    body = f"""{frame(W, H, t)}
<text x="48" y="80" class="mono" font-size="34" font-weight="700" fill="{t['text']}">SK-KIT26</text>
<text x="252" y="80" class="mono" font-size="13" fill="{t['muted']}">Rev. 2026.10</text>
<text x="{W-48}" y="62" class="sans" font-size="15" fill="{t['muted']}" text-anchor="end">Microelectronics engineer · Process · Lithography · EDA</text>
<text x="{W-48}" y="86" class="mono" font-size="12" fill="{t['accent']}" text-anchor="end" letter-spacing="2">DATASHEET · PRELIMINARY</text>
<rect x="40" y="104" width="{W-80}" height="3" fill="{t['accent']}"/>

<text x="48" y="148" class="mono" font-size="14" font-weight="700" fill="{t['accent']}" letter-spacing="1">1  FEATURES</text>
{chr(10).join(fl)}

<text x="640" y="148" class="mono" font-size="14" font-weight="700" fill="{t['accent']}" letter-spacing="1">2  PIN CONFIGURATION</text>
<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{t['panel']}" stroke="{t['muted']}" stroke-width="1.5"/>
<path d="M{bx+bw/2-14},{by} a14,14 0 0,0 28,0" fill="{t['bg']}" stroke="{t['muted']}" stroke-width="1.5"/>
<circle class="pin1" cx="{bx+28}" cy="{by+22}" r="4" fill="{t['diff']}"/>
<text transform="translate({bx+bw/2+6},{by+bh/2}) rotate(-90)" class="mono" font-size="16" font-weight="700" fill="{t['text']}" text-anchor="middle">SK-KIT26</text>
<text x="{bx+bw/2}" y="{by+bh+24}" class="mono" font-size="11" fill="{t['muted']}" text-anchor="middle">DIP-12 · TOP VIEW</text>
{chr(10).join(pins)}

<text x="48" y="428" class="mono" font-size="14" font-weight="700" fill="{t['accent']}" letter-spacing="1">3  ELECTRICAL CHARACTERISTICS</text>
{chr(10).join(tl)}

<text x="48" y="{H-30}" class="mono" font-size="11" fill="{t['muted']}">OutBlade · github.com/OutBlade</text>
<text x="{W-48}" y="{H-30}" class="mono" font-size="11" fill="{t['muted']}" text-anchor="end">Page 1 of 1</text>
"""
    return svg(W, H, "About Sebastian Kallfelz, formatted as an IC datasheet", style, body)


# --------------------------------------------------------------------------- process flow
FLOW = [
    ("DESIGN", "librelane-ppa", "Fmax · PPA sweeps", "diff"),
    ("LAYOUT", "gds-inspector", "GDSII · density · DRC", "m1"),
    ("LITHO", "lithoforge", "masks · OPC · MSLA", "poly"),
    ("PROCESS", "litho-agent", "oxide · implant · etch", "m2"),
    ("YIELD", "semiyield", "ML yield · SPC · DOE", "via"),
    ("TEST", "cms-hgcal-readout", "ECON-D/T · noise", "cyan"),
]


def flow(t):
    W, H = 1200, 262
    pitch, cw, tip, y0, ch = 186, 196, 18, 70, 100
    period = 12
    seg = 100 / len(FLOW)
    centers = []
    parts = []
    for i, (name, repo, desc, col) in enumerate(FLOW):
        x0 = 40 + i * pitch
        notch = tip if i else 0
        d = f"M{x0},{y0} h{cw-tip} l{tip},{ch/2} l{-tip},{ch/2} h{-(cw-tip)} l{notch},{-ch/2} z"
        centers.append(x0 + cw / 2 + notch / 2 - 4)
        parts.append(f'<path d="{d}" fill="{t["panel"]}" stroke="{t[col]}" stroke-width="1.5"/>')
        parts.append(f'<path class="act" style="animation-delay:{i*period/len(FLOW)}s" d="{d}" fill="{t[col]}"/>')
        tx = x0 + 18 + notch
        parts.append(f'<text x="{tx}" y="{y0+30}" class="mono" font-size="12" fill="{t[col]}">{i+1:02d}</text>')
        parts.append(f'<text x="{tx+24}" y="{y0+30}" class="sans" font-size="16" font-weight="700" fill="{t["text"]}" letter-spacing="1">{name}</text>')
        parts.append(f'<text x="{tx}" y="{y0+58}" class="mono" font-size="12.5" fill="{t["text"]}">{repo}</text>')
        parts.append(f'<text x="{tx}" y="{y0+80}" class="sans" font-size="12.5" fill="{t["muted"]}">{esc(desc)}</text>')

    ty = 206
    track = [f'<line x1="{centers[0]}" y1="{ty}" x2="{centers[-1]}" y2="{ty}" stroke="{t["faint"]}" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round"/>']
    for i, c in enumerate(centers):
        track.append(f'<line x1="{c}" y1="{y0+ch+4}" x2="{c}" y2="{ty-8}" stroke="{t["grid"]}"/>')
        track.append(f'<circle cx="{c}" cy="{ty}" r="4" fill="{t["bg"]}" stroke="{t[FLOW[i][3]]}" stroke-width="1.5"/>')

    kf = []
    for i, c in enumerate(centers):
        a, hold = i * seg, i * seg + seg * .6
        kf.append(f"{a:.2f}%,{hold:.2f}% {{ transform: translateX({c:.1f}px); opacity: 1; }}")
    kf.append(f"99% {{ transform: translateX({centers[-1]+60:.1f}px); opacity: 0; }}")
    kf.append(f"100% {{ transform: translateX({centers[0]:.1f}px); opacity: 0; }}")

    style = f"""
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
.act {{ fill-opacity: 0; animation: act {period}s linear infinite; }}
@keyframes act {{ 0% {{ fill-opacity: 0; }} 1%,15% {{ fill-opacity: .16; }} 17%,100% {{ fill-opacity: 0; }} }}
.lot {{ animation: lot {period}s ease-in-out infinite; }}
@keyframes lot {{ {' '.join(kf)} }}
.blink {{ animation: blink 1.2s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
"""
    wafer = (
        f'<g class="lot"><g transform="translate(0,{ty})">'
        f'<circle r="13" fill="{t["panel"]}" stroke="{t["accent"]}" stroke-width="2"/>'
        f'<path d="M-6,-6h12v12h-12zM-6,0h12M0,-6v12" fill="none" stroke="{t["accent"]}" stroke-width="1"/>'
        f'<circle cy="13" r="2.5" fill="{t["bg"]}"/></g></g>'
    )
    body = f"""{frame(W, H, t)}
<text x="48" y="48" class="mono" font-size="13" fill="{t['muted']}" letter-spacing="1.5">PROCESS FLOW  ·  LOT OB-2026  ·  6 STEPS</text>
<text x="{W-48}" y="48" class="mono" font-size="12" fill="{t['diff']}" text-anchor="end" letter-spacing="1.5"><tspan class="blink">●</tspan> IN PROGRESS</text>
{chr(10).join(parts)}
{chr(10).join(track)}
{wafer}
<text x="48" y="{H-26}" class="mono" font-size="11" fill="{t['muted']}">each step is a repository · details in the table below</text>
"""
    return svg(W, H, "Process flow from design to test, one repository per step", style, body)


# --------------------------------------------------------------------------- wafer map
BINS = [
    ("Semiconductor & physics", 10, "diff"),
    ("Developer tools", 10, "m1"),
    ("Games", 8, "m2"),
    ("Math & learning", 4, "via"),
    ("Web & community", 3, "cyan"),
    ("Forks & archives", 5, "faint"),
]


def wafer(t):
    W, H = 1200, 440
    cx, cy, R, pitch, size = 236, 220, 184, 36, 31
    rnd = random.Random(26)
    dies = []
    n = int(R // pitch) + 2
    for j in range(-n, n):
        for i in range(-n, n):
            x, y = cx + i * pitch + (pitch - size) / 2 - pitch / 2, cy + j * pitch + (pitch - size) / 2 - pitch / 2
            corners = [(x, y), (x + size, y), (x, y + size), (x + size, y + size)]
            if all(math.hypot(px - cx, py - cy) < R - 6 for px, py in corners):
                dies.append((x, y))
    dies.sort(key=lambda d: (d[1], d[0]))
    bins = [b for b, (_, cnt, _) in enumerate(BINS) for _ in range(cnt)]
    slots = rnd.sample(range(len(dies)), len(bins))
    assign = dict(zip(slots, bins))

    dl = []
    probe = []
    for k, (x, y) in enumerate(dies):
        if k in assign:
            b = assign[k]
            col = t[BINS[b][2]]
            dl.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="3" fill="{col}" fill-opacity=".8"/>')
            dl.append(f'<text x="{x+size/2:.1f}" y="{y+size/2+4:.1f}" class="mono" font-size="11" fill="{t["bg"]}" text-anchor="middle" font-weight="700">{b+1}</text>')
            probe.append((x, y))
        else:
            dl.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="3" fill="none" stroke="{t["faint"]}" stroke-dasharray="2 3"/>')

    dur = len(probe) * 0.3
    px = ";".join(f"{x-3:.1f}" for x, _ in probe)
    py = ";".join(f"{y-3:.1f}" for _, y in probe)
    probe_el = (
        f'<rect width="{size+6}" height="{size+6}" rx="5" fill="none" stroke="{t["text"]}" stroke-width="2">'
        f'<animate attributeName="x" values="{px}" dur="{dur:.1f}s" calcMode="discrete" repeatCount="indefinite"/>'
        f'<animate attributeName="y" values="{py}" dur="{dur:.1f}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )

    total = sum(c for _, c, _ in BINS)
    leg = []
    for i, (name, cnt, col) in enumerate(BINS):
        y = 176 + i * 34
        leg.append(f'<rect x="520" y="{y-13}" width="16" height="16" rx="3" fill="{t[col]}" fill-opacity=".8"/>')
        leg.append(f'<text x="548" y="{y}" class="mono" font-size="13" fill="{t["muted"]}">BIN {i+1}</text>')
        leg.append(f'<text x="614" y="{y}" class="sans" font-size="15" fill="{t["text"]}">{esc(name)}</text>')
        leg.append(f'<rect x="850" y="{y-10}" width="{cnt*24}" height="10" rx="2" fill="{t[col]}" fill-opacity=".8"/>')
        leg.append(f'<text x="{850+cnt*24+10}" y="{y}" class="mono" font-size="13" fill="{t["muted"]}">{cnt}</text>')

    style = f"""
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
"""
    body = f"""{frame(W, H, t)}
<circle cx="{cx}" cy="{cy}" r="{R}" fill="{t['panel']}" stroke="{t['border']}" stroke-width="2"/>
<circle cx="{cx}" cy="{cy+R}" r="8" fill="{t['bg']}" stroke="{t['border']}" stroke-width="2"/>
<rect x="{cx-10}" y="{cy+R+1}" width="20" height="10" fill="{t['bg']}"/>
{chr(10).join(dl)}
{probe_el}
<text x="520" y="78" class="mono" font-size="14" font-weight="700" fill="{t['accent']}" letter-spacing="1">WAFER MAP · REPOSITORIES</text>
<text x="520" y="108" class="sans" font-size="15" fill="{t['muted']}">Every public repository is a die, binned by domain.</text>
<text x="520" y="130" class="sans" font-size="15" fill="{t['muted']}">Bin 1 is the work above; the other bins are listed below.</text>
{chr(10).join(leg)}
<text x="520" y="{H-46}" class="mono" font-size="12" fill="{t['muted']}" letter-spacing="1">{total} DIE  ·  {len(BINS)} BINS  ·  PROBE CARD OB-01</text>
"""
    return svg(W, H, "Wafer map of all public repositories, binned by domain", style, body)


# --------------------------------------------------------------------------- divider
def divider(t):
    W, H = 1200, 28
    marks = "".join(
        f'<path d="M{x-6},14h12M{x},8v12" stroke="{t["muted"]}" stroke-width="1.5"/>' for x in (12, 600, 1188)
    )
    body = (
        f'<line x1="24" y1="14" x2="588" y2="14" stroke="{t["faint"]}" stroke-dasharray="2 6"/>'
        f'<line x1="612" y1="14" x2="1176" y2="14" stroke="{t["faint"]}" stroke-dasharray="2 6"/>{marks}'
    )
    return svg(W, H, "section divider", "", body)


if __name__ == "__main__":
    for name, fn in [("banner", banner), ("datasheet", datasheet), ("flow", flow), ("wafer", wafer), ("divider", divider)]:
        for theme, t in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(t), encoding="utf-8")
    print("ok")
