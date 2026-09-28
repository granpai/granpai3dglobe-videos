#!/usr/bin/env python3
"""Render a music-backed vertical promo from a live Playwright capture."""
import json
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
ASSETS = OUT / 'promo-assets'
ASSETS.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
WHITE = '#F6FAFC'
CYAN = '#00DBEF'
MUTED = '#A8C4D0'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

COPY = {
    'hvac': [
        ('FOR MULTI-LOCATION SITES', 'NINE LOCATIONS.\nONE MAP.', 'What if your locations were the experience?'),
        ('01  /  EXPLORE', 'FROM GLOBAL VIEW\nTO LOCAL DETAIL.', 'Every pin opens real information.'),
        ('02  /  CONVERT', 'HELP VISITORS\nTAKE THE NEXT STEP.', 'Phone · email · directions in one tap.'),
        ('BUILT FOR WORDPRESS', 'YOUR WORLD.\nON YOUR WEBSITE.', 'TRY THE LIVE DEMO'),
    ],
    'timeline': [
        ('GROWTH TIMELINE · PRO', 'YOUR STORY.\nON THE GLOBE.', 'Turn years of growth into a moment.'),
        ('01  /  WATCH', 'ONE YEAR\nAT A TIME.', 'See each new location appear.'),
        ('02  /  EXPLORE', 'MAKE YOUR\nMILESTONES MOVE.', 'A timeline visitors can control.'),
        ('BUILT FOR WORDPRESS', 'SHOW HOW FAR\nYOU HAVE COME.', 'TRY THE LIVE DEMO'),
    ],
    'global-impact': [
        ('PIN LIST SIDEBAR · PRO', 'EVERY PROJECT.\nONE GLOBE.', 'A fictional example of global impact.'),
        ('01  /  BROWSE', 'FIND EVERY\nLOCATION FAST.', 'A list beside the interactive globe.'),
        ('02  /  EXPLORE', 'FROM A NAME\nTO A STORY.', 'Open project details in one tap.'),
        ('BUILT FOR WORDPRESS', 'MAKE YOUR\nIMPACT VISIBLE.', 'TRY THE LIVE DEMO'),
    ],
}


def run(args):
    subprocess.run(args, check=True)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def background():
    # Navy radial lighting and fine grid, rendered locally without stock art.
    y, x = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((x - 760) / 650) ** 2 + ((y - 820) / 740) ** 2) * 1.7)
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for c, base, power in ((0, 5, 8), (1, 14, 32), (2, 29, 43)):
        arr[:, :, c] = np.clip(base + glow * power, 0, 255).astype('uint8')
    im = Image.fromarray(arr, 'RGB').convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    for gx in range(54, W, 72):
        for gy in range(80, H, 72):
            d.ellipse((gx, gy, gx + 2, gy + 2), fill=(57, 129, 151, 42))
    d.line((78, 126, 1002, 126), fill=(73, 149, 167, 90), width=2)
    d.line((78, 1795, 1002, 1795), fill=(73, 149, 167, 90), width=2)
    return im


def make_card(name, idx, box):
    label, title, caption = COPY[name][idx]
    im = background()
    d = ImageDraw.Draw(im, 'RGBA')
    d.text((80, 73), 'GRANPAI  /  3D GLOBE', font=font(25, True), fill=CYAN)
    d.text((80, 211), label, font=font(27, True), fill=CYAN)
    title_size = 76 if max(map(len, title.split('\n'))) < 17 else 65
    d.multiline_text((76, 280), title, font=font(title_size, True), fill=WHITE, spacing=14)
    x, y, w, h = box
    d.rounded_rectangle((x - 8, y - 8, x + w + 8, y + h + 8), radius=36, outline=(0, 219, 239, 155), width=3)
    d.line((x + 35, y + h + 34, x + 220, y + h + 34), fill=CYAN, width=7)
    if idx == 3:
        d.rounded_rectangle((80, 1500, 1000, 1607), radius=54, fill=(0, 219, 239, 255))
        d.text((W / 2, 1554), caption, font=font(36, True), fill='#041824', anchor='mm')
        d.text((W / 2, 1680), '3dglobe.granpai.com', font=font(38, True), fill=WHITE, anchor='mm')
    else:
        d.text((80, 1580), caption, font=font(34), fill=MUTED)
        d.text((80, 1695), '3dglobe.granpai.com', font=font(30, True), fill=CYAN)
    d.text((1002, 1830), f'{idx + 1:02d} / 04', font=font(24, True), fill=MUTED, anchor='ra')
    path = ASSETS / f'{name}-card-{idx}.png'
    im.convert('RGB').save(path)
    return path


def soundtrack(path, seconds=20, sr=44100):
    # Original ambient beat, generated for this promo. No music license or download.
    n = int(seconds * sr)
    out = np.zeros(n, np.float32)
    bpm = 112
    beat = 60 / bpm
    chords = [[164.81, 196, 246.94], [146.83, 185.0, 220], [130.81, 164.81, 196], [146.83, 196, 246.94]]
    t = np.arange(n, dtype=np.float32) / sr
    for bar in range(math.ceil(seconds / (beat * 4))):
        start = int(bar * beat * 4 * sr)
        length = min(int(beat * 4 * sr), n - start)
        if length <= 0:
            break
        u = np.arange(length, dtype=np.float32) / sr
        chord = chords[bar % 4]
        pad = sum(np.sin(2 * np.pi * f * u + .2 * np.sin(2 * np.pi * .23 * u)) for f in chord) / 3
        out[start:start + length] += .085 * pad * np.minimum(1, u * 2.5) * np.minimum(1, (length / sr - u) * 2.5)
        for eighth in range(8):
            at = start + int(eighth * beat * .5 * sr)
            dur = min(int(.32 * sr), n - at)
            if dur <= 0: continue
            q = np.arange(dur, dtype=np.float32) / sr
            pitch = chord[[0, 1, 2, 1, 0, 2, 1, 2][eighth]] * (2 if eighth in (3, 7) else 1)
            out[at:at + dur] += .055 * np.sin(2 * np.pi * pitch * q) * np.exp(-12 * q)
    for b in range(int(seconds / beat)):
        at = int(b * beat * sr)
        dur = min(int(.25 * sr), n - at)
        if dur <= 0: continue
        u = np.arange(dur, dtype=np.float32) / sr
        kick = np.sin(2 * np.pi * (65 * u + 55 * (1 - np.exp(-25 * u)) / 25)) * np.exp(-19 * u)
        out[at:at + dur] += .22 * kick
        if b % 2:
            rng = np.random.default_rng(b + 100)
            noise = rng.standard_normal(dur).astype(np.float32)
            out[at:at + dur] += .018 * noise * np.exp(-35 * u)
    for cut in (4, 9, 14):
        at = int((cut - .12) * sr)
        dur = min(int(.3 * sr), n - at)
        rng = np.random.default_rng(400 + cut)
        noise = rng.standard_normal(dur).astype(np.float32)
        airy = np.diff(noise, prepend=noise[0])
        envelope = np.sin(np.linspace(0, np.pi, dur, dtype=np.float32)) ** 2
        out[at:at + dur] += .018 * airy * envelope
    # Soft opening and final fade.
    out *= np.minimum(1, t / .4) * np.minimum(1, (seconds - t) / 1.2)
    out = np.tanh(out * 1.7) * .65
    stereo = np.stack([out, np.roll(out, 37) * .98], axis=1)
    pcm = (stereo * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr); f.writeframes(pcm.tobytes())


def render(name):
    meta = json.loads((OUT / f'{name}.json').read_text())
    source = OUT / f'{name}.webm'
    anchor = float(meta['trimSeconds'])
    # Each cut uses authentic footage from the same live browser recording.
    scenes = [
        (max(0, anchor - 4), 4, (695, 205, 570, 560), (90, 600, 900, 900)),
        (anchor + 1, 5, (200, 205, 1080, 570), (40, 650, 1000, 528)),
        (anchor + 6, 5, (210, 285, 455, 430), (120, 555, 840, 790)),
        (anchor + 11, 5, (695, 205, 570, 560), (115, 520, 850, 850)),
    ]
    parts = []
    for i, (start, dur, crop, box) in enumerate(scenes):
        bx, by, bw, bh = box
        cx, cy, cw, ch = crop
        card = make_card(name, i, box)
        part = OUT / f'{name}-scene-{i}.mp4'
        fade = ',fade=t=in:st=0:d=0.35' if i == 0 else (',fade=t=out:st=4.55:d=0.45' if i == 3 else '')
        vf = f'[1:v]crop={cw}:{ch}:{cx}:{cy},scale={bw}:{bh},setsar=1[clip];[0:v][clip]overlay={bx}:{by}:shortest=1,format=yuv420p{fade}[v]'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', '30', '-i', str(card), '-ss', str(start), '-t', str(dur), '-i', str(source), '-filter_complex', vf, '-map', '[v]', '-t', str(dur), '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', str(part)])
        parts.append(part)
    listing = ASSETS / f'{name}-concat.txt'
    listing.write_text(''.join(f"file '{p.resolve()}'\n" for p in parts))
    music = ASSETS / f'{name}-original-music.wav'
    soundtrack(music, 19)
    final = OUT / f'{name}-promo.mp4'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(music), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(final)])
    print(final)


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'hvac'
    if name not in COPY:
        raise SystemExit(f'Unknown demo: {name}')
    render(name)
