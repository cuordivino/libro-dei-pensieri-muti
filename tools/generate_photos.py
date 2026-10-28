# -*- coding: utf-8 -*-
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
os.makedirs(base_dir, exist_ok=True)

# Generate 48 unique, rich, atmospheric black and white chiaroscuro images
# Size: 800 x 1000 (4:5 portrait, classic photographic format)
WIDTH = 800
HEIGHT = 1000

# Emotional visual themes for chiaroscuro photography
themes = [
    # 0: deep abyss / water reflection
    {"type": "water", "light_pos": (400, 750), "beam": True},
    # 1: cage / shadow bars / needle
    {"type": "bars", "light_pos": (200, 300), "beam": False},
    # 2: flame / circus / embers
    {"type": "ember", "light_pos": (400, 500), "beam": True},
    # 3: serpent / curved shadow / smoke
    {"type": "smoke", "light_pos": (550, 400), "beam": True},
    # 4: window / dusk horizon
    {"type": "window", "light_pos": (400, 350), "beam": True},
    # 5: glass / blur / rain
    {"type": "rain", "light_pos": (300, 400), "beam": False},
    # 6: stone / lone monolith / texture
    {"type": "stone", "light_pos": (400, 600), "beam": True},
    # 7: thorns / silhouette / fog
    {"type": "thorns", "light_pos": (400, 250), "beam": True},
    # 8: mirror / sensual silhouette
    {"type": "mirror", "light_pos": (450, 380), "beam": True},
    # 9: veil / lace / shadow
    {"type": "veil", "light_pos": (350, 300), "beam": True},
    # 10: church bench / candle glow
    {"type": "candle", "light_pos": (400, 550), "beam": True},
    # 11: wild beast / dark woods
    {"type": "forest", "light_pos": (400, 200), "beam": True},
    # 12: ointment / hands / dripping
    {"type": "hands", "light_pos": (400, 480), "beam": True},
    # 13: twisted sheets / bed chiaroscuro
    {"type": "sheets", "light_pos": (350, 600), "beam": False},
    # 14: female silhouette / heels / shadow
    {"type": "silhouette", "light_pos": (400, 350), "beam": True},
    # 15: teeth / bite / flame spark
    {"type": "spark", "light_pos": (420, 500), "beam": True},
    # 16: cello / strings / music shadow
    {"type": "strings", "light_pos": (400, 450), "beam": True},
    # 17: falling leaf / stark tree
    {"type": "leaf", "light_pos": (400, 300), "beam": True},
    # 18: rabbit / running shadow / clock
    {"type": "clock", "light_pos": (400, 400), "beam": True},
    # 19: venetian mask / dramatic light
    {"type": "mask", "light_pos": (400, 380), "beam": True},
    # 20: anchor / foggy pier
    {"type": "pier", "light_pos": (400, 650), "beam": True},
    # 21: laughing shadow / alley
    {"type": "alley", "light_pos": (500, 300), "beam": True},
    # 22: storm cloud / lightning split
    {"type": "lightning", "light_pos": (400, 250), "beam": True},
    # 23: cut flower / single branch
    {"type": "flower", "light_pos": (400, 450), "beam": True},
    # 24: christmas bauble / shattered glass
    {"type": "glass_ball", "light_pos": (400, 400), "beam": True},
    # 25: drowning / hand from dark water
    {"type": "water_hand", "light_pos": (400, 600), "beam": True},
    # 26: moka pot / coffee steam chiaroscuro
    {"type": "moka", "light_pos": (400, 520), "beam": True},
    # 27: razor blade / wire / tightrope
    {"type": "wire", "light_pos": (400, 400), "beam": True},
    # 28: flesh / raw stone / hunger
    {"type": "flesh_stone", "light_pos": (380, 420), "beam": True},
    # 29: eternal sea / waves in black and white
    {"type": "sea", "light_pos": (400, 600), "beam": True},
    # 30: linear path / horizon ray of light
    {"type": "path", "light_pos": (400, 450), "beam": True},
    # 31: open threshold / door frame shadow
    {"type": "door", "light_pos": (400, 350), "beam": True},
    # 32: glowing embers / ashes
    {"type": "embers", "light_pos": (400, 600), "beam": True},
    # 33: still portrait / smoke from lips
    {"type": "smoke_portrait", "light_pos": (400, 380), "beam": True},
    # 34: dawn mist / distant bell tower
    {"type": "dawn_tower", "light_pos": (400, 300), "beam": True},
    # 35: eyes / macro gaze through dark
    {"type": "eyes", "light_pos": (400, 450), "beam": True},
    # 36: fire sparks / traditional hearth
    {"type": "hearth", "light_pos": (400, 550), "beam": True},
    # 37: winter frost / frozen footprints
    {"type": "frost", "light_pos": (400, 500), "beam": True},
    # 38: burning paper / incandescent edge
    {"type": "burn_paper", "light_pos": (400, 450), "beam": True},
    # 39: closed old book / dust particles
    {"type": "closed_book", "light_pos": (400, 500), "beam": True},
    # 40: shroud / white marble / scythe shadow
    {"type": "marble", "light_pos": (400, 350), "beam": True},
    # 41: wind gusts / dark pines
    {"type": "wind_trees", "light_pos": (400, 300), "beam": True},
    # 42: solitary mint leaf / water droplet
    {"type": "leaf_drop", "light_pos": (400, 500), "beam": True},
    # 43: fleeting footsteps / foggy street
    {"type": "street_fog", "light_pos": (400, 450), "beam": True},
    # 44: folded hands / pocket watch
    {"type": "watch", "light_pos": (400, 480), "beam": True},
    # 45: abstract motion blur / lights
    {"type": "motion", "light_pos": (400, 500), "beam": True},
    # 46: wine glass / dark liquid splash
    {"type": "wine_glass", "light_pos": (400, 520), "beam": True},
    # 47: open sky / solitary bird in flight
    {"type": "flight", "light_pos": (400, 350), "beam": True}
]

def make_chiaroscuro_image(idx, theme_info):
    img = Image.new("L", (WIDTH, HEIGHT), color=10)
    draw = ImageDraw.Draw(img)
    
    # 1. Base dark chiaroscuro gradient
    lx, ly = theme_info.get("light_pos", (400, 400))
    for r in range(700, 0, -5):
        # brightness drops with distance
        val = int(math.pow(1 - (r / 700), 1.8) * 190)
        draw.ellipse([lx - r, ly - r, lx + r, ly + r], fill=val)
    
    # 2. Add subtle textural shapes depending on theme
    ttype = theme_info["type"]
    
    if ttype in ["bars", "wire"]:
        for x in range(80, WIDTH, 120):
            draw.line([(x, 0), (x + 30, HEIGHT)], fill=5, width=18)
            draw.line([(x + 2, 0), (x + 32, HEIGHT)], fill=80, width=2)
            
    elif ttype in ["window", "door"]:
        # Door / window frame
        draw.rectangle([180, 150, 620, 850], outline=160, width=6)
        draw.rectangle([190, 160, 610, 840], fill=140)
        draw.line([(400, 160), (400, 840)], fill=20, width=8)
        draw.line([(190, 480), (610, 480)], fill=20, width=8)
        # Silhouette
        draw.ellipse([360, 480, 440, 570], fill=15)
        draw.polygon([(340, 570), (460, 570), (480, 840), (320, 840)], fill=15)
        
    elif ttype in ["candle", "hearth", "ember", "spark"]:
        # Central flame / glow
        draw.ellipse([lx - 30, ly - 70, lx + 30, ly + 40], fill=240)
        draw.ellipse([lx - 12, ly - 50, lx + 12, ly + 15], fill=255)
        # Candle stalk or ground
        draw.rectangle([lx - 18, ly + 35, lx + 18, ly + 250], fill=35)
        # floating sparks
        random.seed(idx * 7)
        for _ in range(60):
            sx = random.randint(150, 650)
            sy = random.randint(100, 700)
            s_rad = random.randint(1, 4)
            draw.ellipse([sx, sy, sx + s_rad, sy + s_rad], fill=random.randint(120, 230))
            
    elif ttype in ["moka"]:
        # Moka coffee pot silhouette
        # bottom chamber
        draw.polygon([(330, 720), (470, 720), (450, 580), (350, 580)], fill=45)
        # middle ring
        draw.rectangle([340, 570, 460, 580], fill=90)
        # top chamber
        draw.polygon([(350, 570), (450, 570), (480, 440), (320, 440)], fill=50)
        # lid
        draw.polygon([(320, 440), (480, 440), (400, 400)], fill=60)
        draw.ellipse([390, 385, 410, 405], fill=80)
        # steam rising
        for offset in [-25, 0, 25]:
            for step in range(15):
                sy = 380 - step * 18
                sx = 400 + offset + int(math.sin(step * 0.8) * 30)
                draw.ellipse([sx - step*2, sy - step*2, sx + step*2, sy + step*2], fill=min(200, 30 + step * 10))
                
    elif ttype in ["mask"]:
        # Venetian mask silhouette
        draw.ellipse([260, 300, 540, 520], fill=180)
        draw.ellipse([310, 380, 370, 425], fill=15)
        draw.ellipse([430, 380, 490, 425], fill=15)
        # Shadow cast
        draw.polygon([(260, 480), (540, 480), (440, 680), (360, 680)], fill=120)
        
    elif ttype in ["leaf", "flower"]:
        # Stalk and solitary leaf
        draw.line([(400, 800), (400, 450), (440, 350)], fill=140, width=4)
        draw.polygon([(440, 350), (530, 320), (570, 380), (490, 420)], fill=190)
        draw.polygon([(400, 500), (320, 460), (280, 520), (350, 560)], fill=150)
        
    elif ttype in ["closed_book"]:
        # Book lying on wooden table
        draw.polygon([(220, 560), (520, 480), (620, 540), (300, 630)], fill=170)
        draw.polygon([(220, 560), (300, 630), (300, 680), (220, 610)], fill=60)
        draw.polygon([(300, 630), (620, 540), (620, 580), (300, 680)], fill=90)
        
    elif ttype in ["smoke", "smoke_portrait"]:
        # Atmospheric ethereal smoke ribbons
        random.seed(idx * 13)
        for ribbon in range(6):
            base_x = 350 + ribbon * 20
            points = []
            for y in range(850, 150, -30):
                x = base_x + int(math.sin(y * 0.015 + ribbon) * 80) + random.randint(-15, 15)
                points.append((x, y))
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=random.randint(60, 180), width=random.randint(8, 28))
    else:
        # Organic architectural / chiaroscuro diagonals
        draw.polygon([(100, 0), (700, 0), (800, HEIGHT), (400, HEIGHT)], fill=70)
        draw.line([(150, 0), (650, HEIGHT)], fill=180, width=3)
        draw.line([(300, 0), (800, HEIGHT)], fill=120, width=2)
    
    # 3. Apply soft cinematic Gaussian blur for photographic depth of field
    img = img.filter(ImageFilter.GaussianBlur(radius=3.5))
    
    # 4. Add film grain texture
    grain_img = Image.new("L", (WIDTH, HEIGHT))
    grain_draw = ImageDraw.Draw(grain_img)
    random.seed(idx * 31)
    for _ in range(12000):
        gx = random.randint(0, WIDTH - 1)
        gy = random.randint(0, HEIGHT - 1)
        grain_draw.point((gx, gy), fill=random.randint(40, 210))
    
    grain_img = grain_img.filter(ImageFilter.GaussianBlur(radius=0.7))
    img = Image.blend(img, grain_img, alpha=0.12)
    
    # 5. Vignette (darken edges like a vintage medium format camera)
    vignette = Image.new("L", (WIDTH, HEIGHT), color=255)
    v_draw = ImageDraw.Draw(vignette)
    for r in range(600, 200, -10):
        intensity = int((r / 600) * 255)
        v_draw.ellipse([400 - r, 500 - int(r*1.2), 400 + r, 500 + int(r*1.2)], fill=intensity)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=40))
    
    # Multiply image with vignette
    final_img = Image.composite(img, Image.new("L", (WIDTH, HEIGHT), 5), vignette)
    
    # Save as high-quality JPEG
    filename = f"poesia_{idx + 1}.jpg"
    final_img.save(os.path.join(base_dir, filename), "JPEG", quality=90)

for i in range(48):
    th = themes[i % len(themes)]
    make_chiaroscuro_image(i, th)

print("Generated 48 chiaroscuro black & white photos in /images/")
