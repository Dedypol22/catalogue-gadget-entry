"""Render 'The Updraft Espresso Machine' catalogue photo with PIL.

Draws at 2x supersample (2048x1536) and downscales to 1024x768.
Deterministic, no random, no fonts, no text.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import math
import os

S = 2  # supersample factor
W, H = 1024 * S, 768 * S


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        c = lerp(top, bottom, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c
    return img


def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def bezier(p0, p1, p2, p3, n=120):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def main():
    # ---- backdrop: warm light-grey vertical gradient ----
    img = vgrad((W, H), (240, 238, 233), (203, 199, 192))
    d = ImageDraw.Draw(img, "RGBA")

    horizon = int(H * 0.74)
    # counter surface (slightly warmer / darker, soft horizon blend)
    counter = vgrad((W, H - horizon), (216, 212, 205), (188, 183, 175))
    img.paste(counter, (0, horizon))
    d = ImageDraw.Draw(img, "RGBA")
    # soft horizon glow band
    for i in range(30 * S):
        a = int(28 * (1 - i / (30 * S)))
        d.line([(0, horizon - i), (W, horizon - i)], fill=(255, 255, 255, a))

    # ---- soft shadows layer ----
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    # contact shadow under machine
    sd.ellipse([150 * S, 545 * S, 580 * S, 610 * S], fill=(40, 35, 30, 120))
    # shadow ellipse directly below floating cup (sells levitation)
    sd.ellipse([640 * S, 560 * S, 850 * S, 612 * S], fill=(40, 35, 30, 95))
    # saucer shadow
    sd.ellipse([648 * S, 578 * S, 842 * S, 622 * S], fill=(40, 35, 30, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(14 * S))
    img = Image.alpha_composite(img.convert("RGBA"), sh)
    d = ImageDraw.Draw(img, "RGBA")

    # ================= ESPRESSO MACHINE =================
    mx0, my0, mx1, my1 = 185 * S, 150 * S, 565 * S, 560 * S
    # side depth (right edge, darker steel)
    rrect(d, [mx0 + 18 * S, my0 + 10 * S, mx1 + 16 * S, my1], 26 * S, fill=(118, 120, 124, 255))
    # main body
    rrect(d, [mx0, my0, mx1, my1], 26 * S, fill=(178, 180, 184, 255))
    # brushed-metal horizontal gradient bands
    for i in range(46):
        y = my0 + i * ((my1 - my0) // 46)
        shade = 172 + int(10 * math.sin(i * 0.55)) + (i % 3) * 2
        shade = max(155, min(195, shade))
        d.line([(mx0 + 8 * S, y), (mx1 - 8 * S, y)],
               fill=(shade, shade + 2, shade + 6, 34), width=3 * S)
    # top warmer tray
    rrect(d, [mx0 + 14 * S, my0 + 12 * S, mx1 - 14 * S, my0 + 52 * S], 12 * S,
          fill=(205, 207, 210, 255), outline=(130, 132, 136, 255), width=2 * S)
    for gx in range(mx0 + 40 * S, mx1 - 30 * S, 34 * S):
        d.line([(gx, my0 + 20 * S), (gx, my0 + 44 * S)], fill=(150, 152, 156, 255), width=3 * S)
    # glossy highlight streaks on steel (vertical soft bands)
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.polygon([(225 * S, 165 * S), (265 * S, 165 * S), (245 * S, 545 * S), (210 * S, 545 * S)],
               fill=(255, 255, 255, 55))
    hd.polygon([(480 * S, 165 * S), (505 * S, 165 * S), (500 * S, 545 * S), (478 * S, 545 * S)],
               fill=(255, 255, 255, 40))
    hl = hl.filter(ImageFilter.GaussianBlur(8 * S))
    img = Image.alpha_composite(img, hl)
    d = ImageDraw.Draw(img, "RGBA")
    # front panel (darker inset)
    rrect(d, [mx0 + 28 * S, 225 * S, mx1 - 28 * S, 330 * S], 14 * S,
          fill=(88, 90, 96, 255), outline=(120, 122, 128, 255), width=2 * S)

    # pressure gauge (round, left on panel)
    gx, gy, gr = 285 * S, 278 * S, 38 * S
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(242, 240, 234, 255),
              outline=(52, 52, 56, 255), width=5 * S)
    d.ellipse([gx - gr + 7 * S, gy - gr + 7 * S, gx + gr - 7 * S, gy + gr - 7 * S],
              outline=(170, 168, 160, 255), width=2 * S)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x1 = gx + int((gr - 12 * S) * math.cos(a)); y1 = gy + int((gr - 12 * S) * math.sin(a))
        x2 = gx + int((gr - 6 * S) * math.cos(a)); y2 = gy + int((gr - 6 * S) * math.sin(a))
        d.line([(x1, y1), (x2, y2)], fill=(70, 70, 74, 255), width=2 * S)
    na = math.radians(-35)
    d.line([(gx, gy), (gx + int((gr - 13 * S) * math.cos(na)), gy + int((gr - 13 * S) * math.sin(na)))],
           fill=(178, 44, 36, 255), width=4 * S)
    d.ellipse([gx - 5 * S, gy - 5 * S, gx + 5 * S, gy + 5 * S], fill=(40, 40, 44, 255))

    # two small knobs (right on panel)
    for kx in (420 * S, 495 * S):
        d.ellipse([kx - 24 * S, 254 * S, kx + 24 * S, 302 * S], fill=(48, 48, 52, 255))
        d.ellipse([kx - 24 * S, 250 * S, kx + 24 * S, 298 * S], fill=(72, 72, 78, 255),
                  outline=(30, 30, 34, 255), width=2 * S)
        d.line([(kx, 258 * S), (kx + 10 * S, 266 * S)], fill=(210, 210, 214, 255), width=3 * S)
    # small indicator lamp
    d.ellipse([368 * S, 266 * S, 384 * S, 282 * S], fill=(214, 92, 52, 255),
              outline=(120, 50, 30, 255), width=2 * S)
    d.ellipse([371 * S, 268 * S, 377 * S, 274 * S], fill=(255, 200, 160, 255))

    # group head / portafilter housing
    rrect(d, [300 * S, 345 * S, 470 * S, 385 * S], 10 * S, fill=(105, 107, 112, 255),
          outline=(70, 72, 76, 255), width=2 * S)
    # spout (where coffee returns to)
    spout = (385 * S, 408 * S)
    d.polygon([(362 * S, 385 * S), (408 * S, 385 * S), (398 * S, 410 * S), (372 * S, 410 * S)],
              fill=(70, 72, 76, 255))
    # portafilter basket + handle angled down-right
    d.ellipse([318 * S, 378 * S, 452 * S, 404 * S], fill=(60, 60, 64, 255))
    d.polygon([(430 * S, 386 * S), (560 * S, 448 * S), (548 * S, 472 * S), (418 * S, 402 * S)],
              fill=(38, 36, 34, 255))
    d.ellipse([538 * S, 438 * S, 566 * S, 476 * S], fill=(38, 36, 34, 255))

    # drip tray with grid lines
    rrect(d, [215 * S, 500 * S, 535 * S, 560 * S], 10 * S, fill=(96, 98, 102, 255),
          outline=(64, 66, 70, 255), width=2 * S)
    for gx in range(235 * S, 520 * S, 26 * S):
        d.line([(gx, 508 * S), (gx, 552 * S)], fill=(150, 152, 156, 255), width=3 * S)
    for gy2 in (518 * S, 536 * S):
        d.line([(225 * S, gy2), (525 * S, gy2)], fill=(150, 152, 156, 255), width=3 * S)
    # feet
    for fx in (215 * S, 510 * S):
        rrect(d, [fx, 558 * S, fx + 28 * S, 578 * S], 5 * S, fill=(45, 45, 48, 255))

    # ================= SAUCER (the one accessory) =================
    sx, sy = 745 * S, 592 * S
    d.ellipse([sx - 105 * S, sy - 26 * S, sx + 105 * S, sy + 26 * S], fill=(228, 226, 222, 255),
              outline=(178, 176, 170, 255), width=2 * S)
    d.ellipse([sx - 62 * S, sy - 15 * S, sx + 62 * S, sy + 15 * S], fill=(238, 236, 232, 255),
              outline=(195, 193, 187, 255), width=2 * S)
    d.arc([sx - 105 * S, sy - 26 * S, sx + 105 * S, sy + 26 * S], 20, 160,
          fill=(255, 255, 255, 255), width=3 * S)

    # ================= UPWARD COFFEE STREAM =================
    # Smooth arc from cup (right) UP and LEFT into the spout.
    cup_top = (700 * S, 352 * S)
    pts = bezier(cup_top, (690 * S, 250 * S), (470 * S, 250 * S), spout, n=140)
    # glossy brown tapered stream: draw circles shrinking toward spout
    for i, (x, y) in enumerate(pts):
        t = i / (len(pts) - 1)
        r = (7.5 - 3.5 * t) * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=(92, 52, 26, 255))
    # lighter highlight line offset up-left along the stream
    pts_h = bezier((cup_top[0] - 3 * S, cup_top[1] - 3 * S),
                   (687 * S, 247 * S), (470 * S, 247 * S),
                   (spout[0] - 2 * S, spout[1] - 3 * S), n=140)
    for i, (x, y) in enumerate(pts_h):
        t = i / (len(pts_h) - 1)
        r = (2.4 - 1.1 * t) * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=(196, 138, 88, 220))
    # small splash droplets near cup surface
    for (dx, dy, dr) in ((-16, -14, 4), (10, -20, 3), (22, -8, 3)):
        d.ellipse([(cup_top[0] + dx * S - dr * S, cup_top[1] + dy * S - dr * S),
                   (cup_top[0] + dx * S + dr * S, cup_top[1] + dy * S + dr * S)],
                  fill=(92, 52, 26, 255))

    # ================= LEVITATING CUP =================
    cx, cy = 745 * S, 385 * S  # cup body centre
    # handle (right side) drawn behind body
    d.arc([cx + 52 * S, cy - 42 * S, cx + 118 * S, cy + 38 * S], -80, 95,
          fill=(225, 223, 219, 255), width=13 * S)
    d.arc([cx + 52 * S, cy - 42 * S, cx + 118 * S, cy + 38 * S], -80, 95,
          fill=(250, 249, 246, 255), width=8 * S)
    # cup body: tapered white ceramic
    d.polygon([(cx - 78 * S, cy - 55 * S), (cx + 78 * S, cy - 55 * S),
               (cx + 58 * S, cy + 62 * S), (cx - 58 * S, cy + 62 * S)],
              fill=(246, 245, 242, 255))
    # flat base shading (thin band at the cup's foot)
    d.polygon([(cx - 58 * S, cy + 62 * S), (cx + 58 * S, cy + 62 * S),
               (cx + 54 * S, cy + 50 * S), (cx - 54 * S, cy + 50 * S)],
              fill=(228, 226, 222, 255))
    d.polygon([(cx - 78 * S, cy - 55 * S), (cx + 78 * S, cy - 55 * S),
               (cx + 58 * S, cy + 62 * S), (cx - 58 * S, cy + 62 * S)],
              outline=(185, 183, 177, 255))
    # ceramic shading: soft grey on right, highlight on left
    d.polygon([(cx + 34 * S, cy - 52 * S), (cx + 78 * S, cy - 55 * S),
               (cx + 58 * S, cy + 62 * S), (cx + 30 * S, cy + 58 * S)],
              fill=(226, 224, 220, 120))
    d.polygon([(cx - 66 * S, cy - 50 * S), (cx - 48 * S, cy - 52 * S),
               (cx - 38 * S, cy + 55 * S), (cx - 50 * S, cy + 58 * S)],
              fill=(255, 255, 255, 140))
    # rim + coffee surface (dark ellipse inside rim)
    d.ellipse([cx - 78 * S, cy - 72 * S, cx + 78 * S, cy - 38 * S], fill=(250, 249, 246, 255),
              outline=(185, 183, 177, 255), width=2 * S)
    d.ellipse([cx - 66 * S, cy - 67 * S, cx + 66 * S, cy - 43 * S], fill=(62, 34, 18, 255))
    d.ellipse([cx - 66 * S, cy - 67 * S, cx + 66 * S, cy - 43 * S], outline=(110, 70, 40, 255), width=2 * S)
    # coffee crema highlight arc
    d.arc([cx - 58 * S, cy - 64 * S, cx + 58 * S, cy - 46 * S], 180, 320,
          fill=(168, 110, 62, 255), width=3 * S)

    # ================= STEAM WISPS =================
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(st)
    for xoff, ph in ((-28, 0.0), (24, 1.6)):
        wpts = []
        for i in range(61):
            t = i / 60
            wx = cx + xoff * S + int(13 * S * math.sin(t * 5.2 + ph))
            wy = (cy - 78 * S) - int(t * 78 * S)
            wpts.append((wx, wy))
        std.line(wpts, fill=(255, 255, 255, 120), width=5 * S)
    st = st.filter(ImageFilter.GaussianBlur(4 * S))
    img = Image.alpha_composite(img, st)

    # ---- downscale + save ----
    img = img.convert("RGB").resize((1024, 768), Image.LANCZOS)
    # NOTE: adaptive-palette quantization was tried and reverted — it
    # banded the blurred contact shadows into hard discs. A gentle
    # 6-bit posterize instead keeps the soft studio shadows smooth
    # while cutting the PNG to ~78 KB.
    img = ImageOps.posterize(img, 6)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print("saved", out, img.size, os.path.getsize(out))


if __name__ == "__main__":
    main()
