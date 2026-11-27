from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import numpy as np
import math

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public" / "textures" / "earth_atmos_2048.jpg"
OUT = ROOT / "media" / "itch"
OUT.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT / "portada-630x500.png"
S = 2
W, H = 630*S, 500*S

def font(name, size):
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf")
    ]
    for f in candidates:
        if f.exists():
            return ImageFont.truetype(str(f), size*S)
    return ImageFont.load_default()

# Fondo azul petróleo con luz verde suave.
yy, xx = np.mgrid[0:H, 0:W]
top = np.array([5, 20, 30], dtype=np.float32)
bottom = np.array([8, 43, 37], dtype=np.float32)
t = np.clip(yy / H, 0, 1)[..., None]
bg = top*(1-t) + bottom*t
glow = np.exp(-(((xx-930)/(590))**2 + ((yy-470)/(520))**2))[..., None]
bg = np.clip(bg + glow*np.array([0, 28, 17], dtype=np.float32), 0, 255).astype(np.uint8)
canvas = Image.fromarray(bg, "RGB").convert("RGBA")
draw = ImageDraw.Draw(canvas, "RGBA")

# Ticks and subtle stars add a scientific observatory feel.
for x in range(28*S, W, 34*S):
    draw.line((x, 0, x, H), fill=(120, 220, 145, 12), width=1*S)
for y in range(24*S, H, 34*S):
    draw.line((0, y, W, y), fill=(120, 220, 145, 10), width=1*S)
for px, py, rr, aa in [(55,70,2,120),(305,45,1.5,120),(567,78,2,90),(530,417,2,110),(325,392,1.5,90),(590,303,1.5,100)]:
    draw.ellipse((int(px*S-rr*S), int(py*S-rr*S), int(px*S+rr*S), int(py*S+rr*S)), fill=(195,244,212,aa))

# Ambient halo behind the sphere.
halo = Image.new("RGBA", (W,H), (0,0,0,0))
hd = ImageDraw.Draw(halo, "RGBA")
cx, cy, radius = 924, 500, 365
hd.ellipse((cx-radius,cy-radius,cx+radius,cy+radius), fill=(48,180,106,44))
halo = halo.filter(ImageFilter.GaussianBlur(100*S))
canvas = Image.alpha_composite(canvas, halo)

# Map the equirectangular Earth texture onto a shaded sphere.
tex = Image.open(SRC).convert("RGB").resize((2048,1024), Image.Resampling.LANCZOS)
tex_arr = np.asarray(tex)
radius = 160
grid = 2*radius
gy, gx = np.mgrid[-radius:radius, -radius:radius]
xn = gx / radius
yn = gy / radius
rr = xn*xn + yn*yn
inside = rr <= 1.0
z = np.sqrt(np.maximum(0, 1.0-rr))
lon = np.arctan2(xn, z)
lat = np.arcsin(np.clip(-yn, -1, 1))
u = np.mod((lon/(2*np.pi) + 0.5), 1.0)
v = np.clip(0.5 - lat/np.pi, 0, 1)
ix = np.minimum((u*(tex_arr.shape[1]-1)).astype(np.int32), tex_arr.shape[1]-1)
iy = np.minimum((v*(tex_arr.shape[0]-1)).astype(np.int32), tex_arr.shape[0]-1)
sphere = tex_arr[iy, ix].astype(np.float32)
# Soft light from upper-left; the night edge remains visible.
light = np.array([-0.48, -0.55, 0.68], dtype=np.float32)
light /= np.linalg.norm(light)
diff = np.clip((xn*light[0] + (-yn)*light[1] + z*light[2]), 0, 1)
shade = (0.30 + 0.78*diff)[..., None]
sphere = np.clip(sphere*shade + np.array([4,10,17],dtype=np.float32),0,255).astype(np.uint8)
rgba = np.zeros((grid,grid,4),dtype=np.uint8)
rgba[:,:,:3] = sphere
rgba[:,:,3] = np.where(inside, 255, 0).astype(np.uint8)
sphere_img = Image.fromarray(rgba, "RGBA").resize((grid*S,grid*S), Image.Resampling.LANCZOS)
sx, sy = 302*S, 90*S
# Atmosphere rim and soft shadow.
rim = Image.new("RGBA",(W,H),(0,0,0,0))
rd=ImageDraw.Draw(rim,"RGBA")
rd.ellipse((sx-3*S,sy-3*S,sx+(grid+3)*S,sy+(grid+3)*S),outline=(112,237,171,185),width=3*S)
rim=rim.filter(ImageFilter.GaussianBlur(1.2*S))
canvas=Image.alpha_composite(canvas,rim)
canvas.alpha_composite(sphere_img,(sx,sy))

# Crisp outer border and restrained orbit.
draw = ImageDraw.Draw(canvas, "RGBA")
draw.ellipse((sx-2*S,sy-2*S,sx+(grid+2)*S,sy+(grid+2)*S),outline=(105,221,163,220),width=1*S)
draw.arc((sx-23*S,sy+36*S,sx+(grid+23)*S,sy+(grid-34)*S), 195, 334, fill=(164,232,116,135), width=2*S)
# A small location marker on the globe.
mx, my = 493*S, 224*S
draw.ellipse((mx-5*S,my-5*S,mx+5*S,my+5*S),fill=(201,255,112,255),outline=(9,36,30,255),width=2*S)
draw.ellipse((mx-11*S,my-11*S,mx+11*S,my+11*S),outline=(201,255,112,100),width=1*S)

# Branding and title.
draw = ImageDraw.Draw(canvas, "RGBA")
# Leaf icon.
draw.ellipse((32*S,34*S,48*S,47*S), fill=(140,230,71,255))
draw.line((35*S,46*S,46*S,34*S), fill=(7,48,30,255), width=2*S)
draw.text((57*S,29*S), "BIOLAB 3D", font=font("segoeuib.ttf",18), fill=(166,244,91,255), stroke_width=0)
draw.text((32*S,81*S), "Observatorio", font=font("segoeuib.ttf",31), fill=(245,250,244,255))
draw.text((32*S,119*S), "Global de", font=font("segoeuib.ttf",31), fill=(245,250,244,255))
draw.text((32*S,157*S), "Cultivos", font=font("segoeuib.ttf",31), fill=(245,250,244,255))
draw.rounded_rectangle((32*S,211*S,213*S,216*S),radius=2*S,fill=(142,225,73,255))
draw.text((32*S,230*S), "Clima · suelo · biodiversidad", font=font("segoeui.ttf",12), fill=(176,203,186,255))
# Topic tags.
tags = [("SIMULACIÓN 3D", 32, 278, 124), ("DATOS GLOBALES", 164, 278, 133)]
for label, x, y, width in tags:
    draw.rounded_rectangle((x*S,y*S,(x+width)*S,(y+28)*S),radius=12*S,fill=(15,55,48,220),outline=(87,155,98,150),width=1*S)
    draw.text(((x+11)*S,(y+7)*S), label, font=font("segoeuib.ttf",8), fill=(213,242,213,255))
draw.text((32*S,392*S), "PROYECTO FINAL  ·  HTML5", font=font("segoeuib.ttf",10), fill=(164,215,175,255))
draw.text((32*S,414*S), "Explora el mundo, compara ambientes y", font=font("segoeui.ttf",9), fill=(144,174,158,255))
draw.text((32*S,431*S), "simula decisiones para tus cultivos.", font=font("segoeui.ttf",9), fill=(144,174,158,255))

# Thin border and final downsample.
draw.rounded_rectangle((7*S,7*S,W-7*S,H-7*S),radius=17*S,outline=(106,174,124,95),width=1*S)
canvas = canvas.convert("RGB").resize((630,500), Image.Resampling.LANCZOS)
canvas.save(OUT_FILE, format="PNG", optimize=True)
print(f"{OUT_FILE} {canvas.size[0]}x{canvas.size[1]} {OUT_FILE.stat().st_size} bytes")

