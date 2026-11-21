"""Renders the profile header: an SEM micrograph of my name, written in resist.

    python profile/build.py

Writes profile/sem.svg (slow-scan animation) and profile/sem.jpg (still).
Nothing here is drawn by hand. A height map is built from the resist pattern,
and the secondary-electron image is computed from it: edge brightening,
detector shadowing, charging halo, substrate grain and shot noise.

Needs numpy, scipy and Pillow. The fonts are Windows system fonts; they are
only used at build time and are not part of the output.
"""
from pathlib import Path
import base64
import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, shift as nd_shift

OUT = Path(__file__).parent
FONTS = Path("C:/Windows/Fonts")

W, H = 1600, 1000          # image area
BAR = 92                   # data bar
SS = 2                     # supersampling
HFW_UM = 6.0               # horizontal field width
PX_PER_UM = W / HFW_UM     # 266.7 px per micron
MAG = 128_000 / HFW_UM     # 128 mm reference display -> ~21 300x

rng = np.random.default_rng(1350)  # 13.50 nm


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except (OSError, ValueError):
            pass
    return f


# ---------------------------------------------------------------- pattern

def pattern():
    """The resist layout, at supersampled resolution. 1 = resist."""
    w, h = W * SS, H * SS
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)

    name = font("bahnschrift.ttf", 168 * SS, "SemiBold")
    d.text((150 * SS, 330 * SS), "SEBASTIAN", font=name, fill=255)
    d.text((150 * SS, 520 * SS), "KALLFELZ", font=name, fill=255)

    small = font("bahnschrift.ttf", 36 * SS, "SemiBold")
    d.text((156 * SS, 738 * SS), "MICROELECTRONICS  ·  KIT KARLSRUHE", font=small, fill=255)

    # alignment cross, upper right
    cx, cy, arm, t = 1380 * SS, 190 * SS, 70 * SS, 9 * SS
    d.rectangle([cx - arm, cy - t, cx + arm, cy + t], fill=255)
    d.rectangle([cx - t, cy - arm, cx + t, cy + arm], fill=255)

    # dose-test line/space grating along the bottom edge, running off frame
    x = 1040 * SS
    for i in range(14):
        lw = int((10 - i * 0.45) * SS)
        d.rectangle([x, 820 * SS, x + lw, 1000 * SS + 10], fill=255)
        x += lw * 2 + 6 * SS

    m = np.asarray(img, dtype=np.float32) / 255.0
    # line edge roughness: perturb the edge with low-pass noise, re-threshold
    rough = gaussian_filter(rng.standard_normal(m.shape).astype(np.float32), 2.2 * SS)
    rough /= rough.std()
    m = gaussian_filter(m, 1.4 * SS)
    m = (m + 0.055 * rough > 0.5).astype(np.float32)
    return m


def particle(sig, x, y, r):
    """A dust particle sitting on the surface: bright rim, charged core."""
    hgt, wid = sig.shape
    yy, xx = np.ogrid[:hgt, :wid]
    a = np.hypot(xx - x, (yy - y) / 0.82)
    blob = np.clip(1 - a / r, 0, 1)
    rim = np.exp(-((a - r * 0.82) / (r * 0.12)) ** 2)
    shade = np.clip(1 - np.hypot(xx - x - r * 0.5, (yy - y - r * 0.6) / 0.82) / (r * 1.5), 0, 1)
    return sig - 0.10 * shade * (blob == 0) + 0.45 * blob ** 0.6 + 0.5 * rim


# ---------------------------------------------------------------- imaging

def secondary_electrons(m):
    s = SS
    hgt = gaussian_filter(m, 2.0 * s)                         # sloped sidewalls
    gy, gx = np.gradient(hgt)
    edge = np.hypot(gx, gy)
    edge /= np.percentile(edge, 99.7)

    sig = 0.20 + 0.17 * m                                      # material contrast
    sig += 0.58 * np.clip(edge, 0, 1.4) ** 0.85                # edge effect
    sig += 0.16 * gaussian_filter(edge, 3.5 * s) * m           # SE escape near edges lifts the top
    sig += 0.10 * np.clip((gx - gy) / (np.abs(gx).max() + 1e-6) * 6, -1, 1)  # detector side
    shadow = gaussian_filter(nd_shift(m, (7 * s, 7 * s), order=0), 9 * s)
    sig -= 0.07 * shadow * (1 - m)                             # shadow on the substrate
    sig += 0.07 * gaussian_filter(m, 30 * s)                   # charging halo

    yy, xx = np.mgrid[:m.shape[0], :m.shape[1]].astype(np.float32)
    sig += 0.035 * (1 - xx / m.shape[1]) - 0.03 * ((yy / m.shape[0]) - 0.5) ** 2   # uneven field

    grain = gaussian_filter(rng.standard_normal(m.shape).astype(np.float32), 0.9 * s)
    mottle = gaussian_filter(rng.standard_normal(m.shape).astype(np.float32), 14 * s)
    sig += 0.025 * grain / grain.std() + 0.011 * mottle / mottle.std()

    sig = particle(sig, 1265 * s, 455 * s, 17 * s)
    sig = particle(sig, 302 * s, 880 * s, 6 * s)
    return sig


def downsample(a, k=SS):
    h, w = a.shape
    return a[: h // k * k, : w // k * k].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def frame(sig, noise, line_jitter=0.0, blur=0.0):
    a = sig.copy()
    if blur:
        a = gaussian_filter(a, blur)
    a = a + noise * rng.standard_normal(a.shape).astype(np.float32)
    a += 0.006 * rng.standard_normal((a.shape[0], 1)).astype(np.float32)   # line-to-line banding
    if line_jitter:
        for i, dx in enumerate(rng.normal(0, line_jitter, a.shape[0])):
            a[i] = np.roll(a[i], int(round(dx)))
    a = np.clip(a, 0, 1) ** 0.92
    return (a * 255).astype(np.uint8)


# ---------------------------------------------------------------- data bar

def data_bar():
    bar = Image.new("L", (W, BAR), 0)
    d = ImageDraw.Draw(bar)
    lab = font("arial.ttf", 17)
    val = font("arial.ttf", 25)
    cells = [
        ("HV", "5.00 kV"),
        ("WD", "4.1 mm"),
        ("mag", f"{round(MAG, -2):,.0f} x".replace(",", " ")),
        ("det", "ETD"),
        ("mode", "SE"),
        ("HFW", f"{HFW_UM:.2f} µm"),
        ("sample", "OutBlade · PMMA on Si"),
    ]
    x = 22
    for label, value in cells:
        d.text((x, 16), label, font=lab, fill=150)
        d.text((x, 42), value, font=val, fill=235)
        x += max(d.textlength(label, font=lab), d.textlength(value, font=val)) + 34
        d.line([(x - 17, 14), (x - 17, BAR - 14)], fill=70, width=1)

    # scale bar: exactly 1 µm at this field width
    L = round(PX_PER_UM)
    x1 = W - 40
    x0 = x1 - L
    d.text((x0 + L / 2 - d.textlength("1 µm", font=val) / 2, 14), "1 µm", font=val, fill=235)
    d.rectangle([x0, 56, x1, 66], fill=235)
    d.rectangle([x0, 50, x0 + 2, 72], fill=235)
    d.rectangle([x1 - 2, 50, x1, 72], fill=235)
    return np.asarray(bar)


# ---------------------------------------------------------------- output

def jpeg(arr, q):
    buf = io.BytesIO()
    Image.fromarray(arr, "L").save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return buf.getvalue()


def main():
    sig = downsample(secondary_electrons(pattern()))
    bar = data_bar()

    slow = np.vstack([frame(sig, 0.035), bar])
    # TV-rate frame: half resolution, heavy noise, scan jitter
    fast = frame(downsample(sig, 2), 0.16, line_jitter=0.8, blur=0.5)
    fast = np.vstack([np.asarray(Image.fromarray(fast).resize((W, H), Image.BILINEAR)), bar])

    still = jpeg(slow, 88)
    (OUT / "sem.jpg").write_bytes(still)

    b_slow = base64.b64encode(jpeg(slow, 84)).decode()
    b_fast = base64.b64encode(jpeg(fast, 55)).decode()
    total = H + BAR
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {total}" width="{W}" height="{total}" role="img" aria-label="Scanning electron micrograph: the name Sebastian Kallfelz written in resist on silicon, with an alignment cross, a dose-test grating and a 1 micron scale bar.">
<defs><clipPath id="scanned"><rect x="0" y="0" width="{W}" height="0"><animate attributeName="height" from="0" to="{H}" begin="0.4s" dur="3.2s" fill="freeze"/></rect></clipPath>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.45"/></linearGradient></defs>
<image width="{W}" height="{total}" xlink:href="data:image/jpeg;base64,{b_fast}"/>
<image width="{W}" height="{total}" clip-path="url(#scanned)" xlink:href="data:image/jpeg;base64,{b_slow}"/>
<g opacity="0"><rect x="0" y="-26" width="{W}" height="26" fill="url(#beam)"/><rect x="0" y="0" width="{W}" height="1.5" fill="#fff"/>
<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {H}" begin="0.4s" dur="3.2s" fill="freeze"/>
<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.03;0.97;1" begin="0.4s" dur="3.2s" fill="freeze"/></g>
</svg>'''
    (OUT / "sem.svg").write_text(svg, encoding="utf-8")
    print(f"sem.jpg {len(still) // 1024} KB, sem.svg {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
