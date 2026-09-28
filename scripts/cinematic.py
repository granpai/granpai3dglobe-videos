#!/usr/bin/env python3
"""Kinetic 9:16 HVAC product film from the live recorded WebGL demo."""
import math
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from promo import soundtrack

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
TMP = OUT / 'cinematic-frames'
TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS, LENGTH = 720, 1280, 24, 17
NAVY = (5, 15, 28)
CYAN = (0, 224, 239)
CORAL = (255, 91, 91)
WHITE = (245, 250, 252)
MUTED = (156, 189, 203)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def f(size, bold=True): return ImageFont.truetype(BOLD if bold else REG, size)
def clamp(x): return max(0, min(1, x))
def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def video_frames(source, start, duration, crop, prefix):
    x, y, w, h = crop
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(start), '-t', str(duration), '-i', str(source),
           '-vf', f'fps=12,crop={w}:{h}:{x}:{y},scale=640:640:flags=lanczos', str(TMP / f'{prefix}-%03d.jpg')]
    subprocess.run(cmd, check=True)
    return sorted(TMP.glob(f'{prefix}-*.jpg'))


def base(t):
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im, 'RGBA')
    for radius in range(610, 70, -35):
        a = int(2 + 10 * (610 - radius) / 540)
        d.ellipse((470-radius, 550-radius, 470+radius, 550+radius), fill=(0, 128, 161, a))
    for i in range(13):
        y = 90 + i * 91 + int(5 * math.sin(t * 1.3 + i))
        d.line((0, y, W, y), fill=(65, 135, 155, 18), width=1)
    for i in range(12):
        x = 22 + i * 64
        d.line((x, 0, x, H), fill=(65, 135, 155, 14), width=1)
    d.text((40, 38), 'GRANPAI', font=f(22), fill=WHITE)
    d.text((W-40, 39), '3D GLOBE', font=f(18), fill=CYAN, anchor='ra')
    d.line((40, 82, W-40, 82), fill=(*CYAN, 110), width=2)
    return im


def txt(d, x, y, value, size, color=WHITE, bold=True, anchor=None):
    d.text((int(x), int(y)), value, font=f(size, bold), fill=color, anchor=anchor)


def image_at(paths, local_t, duration):
    if not paths: raise RuntimeError('Missing source frames')
    idx = min(len(paths)-1, max(0, int(clamp(local_t / duration) * (len(paths)-1))))
    return Image.open(paths[idx]).convert('RGB')


def rounded_paste(canvas, image, x, y, width, height, radius=28, opacity=255):
    image = image.resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')
    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width-1, height-1), radius=radius, fill=opacity)
    image.putalpha(mask)
    canvas.paste(image, (int(x), int(y)), image)


def frame(t, globe, modal, full):
    im = base(t)
    d = ImageDraw.Draw(im, 'RGBA')
    if t < 2.45:
        k = ease(t / .45)
        txt(d, 40, 145 - 36*(1-k), 'THE OLD WAY', 22, CORAL)
        txt(d, 40, 200 - 40*(1-k), 'NINE BRANCHES.', 54)
        txt(d, 40, 270 - 40*(1-k), 'ONE LONG LIST.', 50)
        cities = ['SEATTLE', 'LOS ANGELES', 'PHOENIX', 'DENVER', 'DALLAS', 'CHICAGO', 'ATLANTA', 'NEW YORK', 'MIAMI']
        for i, city in enumerate(cities):
            phase = ease((t - .12*i) / .45)
            y = 404 + i*77 + int((1-phase)*80)
            if y > H-50: continue
            d.rounded_rectangle((40, y, 680, y+62), radius=13, fill=(24, 43, 59, int(155*phase)))
            txt(d, 64, y+16, f'{i+1:02d}', 23, CORAL)
            txt(d, 131, y+12, city, 28, (*WHITE, int(220*phase)))
            d.ellipse((636, y+25, 648, y+37), fill=(*CORAL, int(200*phase)))
        txt(d, 40, 1175, 'Would you explore this?', 28, MUTED, False)
    elif t < 3.2:
        p = ease((t - 2.45) / .75)
        for i in range(7):
            r = 60 + p*510 - i*44
            if r <= 0: continue
            d.ellipse((360-r, 650-r, 360+r, 650+r), outline=(*CYAN, max(0, 100-i*13)), width=4)
        txt(d, W/2, 640, 'WHAT IF IT MOVED?', 42, WHITE, anchor='mm')
        d.rectangle((0, H-15, W*p, H), fill=CYAN)
    elif t < 7.3:
        q = t - 3.2
        appear = ease(q / .65)
        txt(d, 40, 168-55*(1-appear), 'ONE WORLD.', 60)
        txt(d, 40, 244-55*(1-appear), 'ALL YOUR LOCATIONS.', 39, CYAN)
        g = image_at(globe, q, 4.1)
        size = int(250 + 394*appear)
        rounded_paste(im, g, (W-size)/2, 358 + (640-size)/2, size, size, radius=size//2)
        d = ImageDraw.Draw(im, 'RGBA')
        for j in range(2):
            r = int(329 + 19*math.sin(q*2+j))
            d.arc((360-r, 676-r, 360+r, 676+r), 35+j*180, 195+j*180, fill=(*CYAN, 150), width=3)
        d.rounded_rectangle((40, 1100, 680, 1180), radius=25, fill=(10, 39, 53, 235), outline=(*CYAN, 120), width=2)
        txt(d, 67, 1123, 'DRAG  ·  DISCOVER  ·  EXPLORE', 25, WHITE)
    elif t < 11.7:
        q = t - 7.3
        appear = ease(q/.55)
        txt(d, 40, 162, 'TAP A PIN.', 62)
        txt(d, 40, 247, 'THE DETAILS APPEAR.', 36, CYAN)
        g = image_at(globe, min(q+1, 4), 4.1)
        rounded_paste(im, g, 413, 345, 260, 260, radius=130, opacity=160)
        m = image_at(modal, q, 4.4)
        # The modal is the real plugin UI, cropped from its live capture.
        w = int(580*appear)
        h = int(560*appear)
        rounded_paste(im, m, 70 + (580-w)/2, 392 + (560-h)/2, max(1,w), max(1,h), radius=22)
        d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((62, 385, 658, 970), radius=32, outline=(*CYAN, 195), width=3)
        txt(d, 40, 1052, 'DETAILS. CONTACT. DIRECTIONS.', 28, WHITE)
        if q > 2.0:
            pulse = int(140 + 60*math.sin(q*8))
            d.ellipse((120-pulse/5, 838-pulse/5, 305+pulse/5, 892+pulse/5), outline=(*CORAL, 160), width=4)
    elif t < 14.8:
        q = t-11.7
        appear = ease(q/.5)
        txt(d, 40, 159, 'FROM A LIST...', 49, MUTED)
        txt(d, 40, 235, 'TO AN EXPERIENCE.', 45, CYAN)
        # A fast split-screen reveal makes the contrast visual.
        d.rounded_rectangle((30, 380, 344, 1010), radius=23, fill=(22, 37, 52, 235))
        for i, city in enumerate(['SEATTLE','DENVER','DALLAS','ATLANTA','MIAMI']):
            d.rounded_rectangle((48, 420+i*106, 324, 496+i*106), radius=10, fill=(49, 64, 75, 180))
            txt(d, 70, 444+i*106, city, 21, MUTED)
        g = image_at(globe, q, 3.1)
        width = int(345*appear)
        rounded_paste(im, g, 357, 510, max(1,width), 420, radius=28)
        d = ImageDraw.Draw(im, 'RGBA')
        d.line((350, 405, 350, 1000), fill=(*CYAN, 180), width=4)
        txt(d, 45, 1100, 'Real 3D. Interactive pins.', 28, WHITE)
        txt(d, 45, 1150, 'Made for WordPress.', 27, MUTED, False)
    else:
        q=t-14.8
        appear=ease(q/.55)
        g=image_at(globe, min(q+1, 4), 4.1)
        size=int(310+270*appear)
        rounded_paste(im, g, (W-size)/2, 267+(580-size)/2, size, size, radius=size//2)
        d=ImageDraw.Draw(im, 'RGBA')
        txt(d, W/2, 920, 'MAKE YOUR MAP', 48, WHITE, anchor='mm')
        txt(d, W/2, 987, 'THE MOMENT.', 53, CYAN, anchor='mm')
        d.rounded_rectangle((50, 1080, 670, 1165), radius=42, fill=CYAN)
        txt(d, 360, 1123, 'TRY THE LIVE DEMO  →', 26, NAVY, anchor='mm')
        txt(d, 360, 1220, '3dglobe.granpai.com', 22, WHITE, anchor='mm')
    if t > LENGTH-.45:
        im=Image.blend(im, Image.new('RGB',(W,H),NAVY), ease((t-(LENGTH-.45))/.45))
    return im


def main():
    import json
    meta=json.loads((OUT/'hvac.json').read_text())
    anchor=float(meta['trimSeconds'])
    source=OUT/'hvac.webm'
    globe=video_frames(source, anchor-5, 10, (690,210,580,570), 'globe')
    modal=video_frames(source, anchor+2, 9, (230,293,420,404), 'modal')
    full=[]
    if len(globe)<5 or len(modal)<5: raise RuntimeError('Live capture too short for cinematic edit')
    if '--storyboard' in sys.argv:
        ims=[]
        for t in (1, 4.5, 8.5, 12.5, 15.7):
            x=frame(t,globe,modal,full);x.thumbnail((360,640));ims.append(x)
        board=Image.new('RGB',(360*5,640),NAVY)
        for i,x in enumerate(ims): board.paste(x,(i*360,0))
        board.save(OUT/'hvac-cinematic-storyboard.jpg')
        return
    music=OUT/'hvac-cinematic-music.wav'
    soundtrack(music,LENGTH)
    target=OUT/'hvac-cinematic.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-i',str(music),'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','192k','-t',str(LENGTH),'-movflags','+faststart',str(target)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(FPS*LENGTH):
        p.stdin.write(frame(n/FPS,globe,modal,full).tobytes())
    p.stdin.close()
    if p.wait(): raise RuntimeError('FFmpeg render failed')
    print(target)

if __name__=='__main__': main()
