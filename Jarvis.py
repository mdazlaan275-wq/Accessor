"""
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗    ██╗  ██╗██╗   ██╗██████╗
 ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ██║  ██║██║   ██║██╔══██╗
 ██║███████║██████╔╝██║   ██║██║███████╗    ███████║██║   ██║██║  ██║
 ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ██╔══██║██║   ██║██║  ██║
 ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║    ██║  ██║╚██████╔╝██████╔╝
 ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
 STARK INDUSTRIES  //  MARK VII  //  CLASSIFIED  //  AI CORE ONLINE
 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

import pygame
import math
import random
import threading
import os
import sys
import types
import time
import colorsys
import ollama
import pyttsx3
import pyperclip

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
BOOT_SOUND_PATH = r"C:\Users\mdazl\Downloads\Futuristic_HUD_UI_Visuals_Sound_Design(128k).wav"
WIDTH, HEIGHT   = 1280, 800
TARGET_FPS      = 60

# Ollama model router
MODEL_DEFAULT   = "jarvis"          # fallback / general chat
MODEL_CODE_BIG  = "qwen2.5-coder:14b"
MODEL_CODE_FAST = "qwen2.5-coder:7b"
MODEL_VISION    = "llava"

# JARVIS personality system prompt
JARVIS_SYSTEM = (
    "You are JARVIS — Just A Rather Very Intelligent System, the AI of Tony Stark / Iron Man. "
    "You are calm, precise, slightly witty, and always call the user 'sir' or 'ma'am'. "
    "Keep responses concise unless asked for detail. "
    "When answering code questions, provide clean, commented code."
)

# ═══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
C_BLACK     = (  0,   2,   6)
C_DARK      = (  4,   8,  14)
C_PANEL     = (  8,  14,  22)
C_PANEL_BDR = (  0, 180, 220)
C_CYAN      = (  0, 240, 255)
C_CYAN_DIM  = (  0, 120, 160)
C_CYAN_MID  = (  0, 180, 210)
C_GOLD      = (255, 190,  40)
C_GOLD_DIM  = (140, 100,  20)
C_RED       = (255,  40,  40)
C_RED_DIM   = (160,  20,  20)
C_GREEN     = (  0, 255, 140)
C_GREEN_DIM = (  0, 100,  60)
C_WHITE     = (220, 235, 245)
C_GREY      = ( 60,  75,  90)
C_PLASMA    = ( 80, 200, 255)
C_ORANGE    = (255, 120,  20)

# ═══════════════════════════════════════════════════════════════════════════════
#  TECH SENTENCES
# ═══════════════════════════════════════════════════════════════════════════════
TECH_SENTENCES = [
    "Neural core engaged",
    "Quantum pipeline init",
    "Adaptive inference active",
    "Cognitive matrix compile",
    "Synaptic grid alignment",
    "Predictive engine warm",
    "Data stream synced",
    "Holographic interface up",
    "Security handshake done",
]

BOOT_MSGS = [
    (0.04, "INITIALIZING POWER CORE"),
    (0.14, "LOADING NEURAL MATRICES"),
    (0.26, "CALIBRATING REPULSORS"),
    (0.38, "ESTABLISHING JARVIS LINK"),
    (0.50, "THREAT ASSESSMENT ONLINE"),
    (0.62, "HOLOGRAPHIC INTERFACE UP"),
    (0.73, "WEAPONS SAFETY CONFIRMED"),
    (0.84, "SUIT INTEGRITY: 100%"),
    (0.93, "AUXILIARY SYSTEMS GO"),
    (0.98, "STARK — I AM READY, SIR."),
]

# ═══════════════════════════════════════════════════════════════════════════════
#  LOW-LEVEL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def lerp(a, b, t):          return a + (b - a) * t
def clamp(v, lo, hi):       return max(lo, min(hi, v))
def lerp_col(c1, c2, t):    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def hexagon_pts(cx, cy, r, rot=0.0):
    return [(int(cx + math.cos(math.radians(60*i + rot)) * r),
             int(cy + math.sin(math.radians(60*i + rot)) * r))
            for i in range(6)]

def circle_glow(surf, cx, cy, r, color, layers=6, alpha_start=80):
    for i in range(layers, 0, -1):
        alpha  = int(alpha_start * (i / layers) ** 2)
        radius = r + (layers - i) * 6
        gs = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*color, alpha), (radius+2, radius+2), radius)
        surf.blit(gs, (cx-radius-2, cy-radius-2), special_flags=pygame.BLEND_RGBA_ADD)

def draw_glow_line(surf, p1, p2, color, width=2, glow_alpha=60):
    w = abs(p2[0]-p1[0]) + 20
    h = abs(p2[1]-p1[1]) + 20
    if w < 1 or h < 1:
        return
    gl     = pygame.Surface((w, h), pygame.SRCALPHA)
    offset = (min(p1[0],p2[0])-10, min(p1[1],p2[1])-10)
    lp1    = (p1[0]-offset[0], p1[1]-offset[1])
    lp2    = (p2[0]-offset[0], p2[1]-offset[1])
    pygame.draw.line(gl, (*color, glow_alpha), lp1, lp2, width+4)
    pygame.draw.line(gl, (*color, 200),        lp1, lp2, width)
    surf.blit(gl, offset, special_flags=pygame.BLEND_RGBA_ADD)

def truncate(text, font, max_w):
    if font.size(text)[0] <= max_w:
        return text
    while len(text) > 1 and font.size(text + "…")[0] > max_w:
        text = text[:-1]
    return text + "…"

def wrap_lines(text, font, max_w, max_lines=None):
    words      = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
        if max_lines and len(lines) >= max_lines:
            break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines:
        lines[-1] = truncate(lines[-1], font, max_w)
    return lines

# ═══════════════════════════════════════════════════════════════════════════════
#  PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','size','color']
    def __init__(self, x, y, vx, vy, life, size, color):
        self.x, self.y          = float(x), float(y)
        self.vx, self.vy        = vx, vy
        self.life = self.max_life = life
        self.size, self.color   = size, color

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.035
        self.vx *= 0.992
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        t     = self.life / self.max_life
        alpha = int(255 * t)
        r     = max(1, int(self.size * t))
        s     = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r+1, r+1), r)
        surf.blit(s, (int(self.x)-r-1, int(self.y)-r-1),
                  special_flags=pygame.BLEND_RGBA_ADD)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, speed, color,
             life_range=(20,60), size=3, spread=360):
        for _ in range(count):
            ang  = math.radians(random.uniform(0, spread))
            spd  = random.uniform(speed*0.4, speed)
            vx   = math.cos(ang)*spd + random.gauss(0, 0.3)
            vy   = math.sin(ang)*spd + random.gauss(0, 0.3)
            life = random.randint(*life_range)
            self.particles.append(Particle(x, y, vx, vy, life, size, color))

    def emit_ring(self, cx, cy, radius, count, speed, color, life=40, size=2):
        for i in range(count):
            ang = math.radians(360*i/count)
            x   = cx + math.cos(ang)*radius
            y   = cy + math.sin(ang)*radius
            self.particles.append(
                Particle(x, y, math.cos(ang)*speed, math.sin(ang)*speed, life, size, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA STREAM  (Matrix-style falling columns)
# ═══════════════════════════════════════════════════════════════════════════════
_STREAM_CHARS = list("01ABCDEF█▓▒░▪■◆◇⬛⬜▸▾▴▲")

class DataStream:
    def __init__(self, x, y, h, color, speed=2.0, char_size=12):
        self.x, self.y   = x, y
        self.h           = h
        self.color       = color
        self.speed       = speed
        self.char_size   = char_size
        n                = h // char_size + 2
        self.chars       = [random.choice(_STREAM_CHARS) for _ in range(n)]
        self.head_pos    = random.uniform(0, h)
        self.refresh     = 0

    def update(self):
        self.head_pos = (self.head_pos + self.speed) % (self.h + self.char_size*4)
        self.refresh += 1
        if self.refresh > 4:
            self.refresh = 0
            self.chars[random.randint(0, len(self.chars)-1)] = random.choice(_STREAM_CHARS)

    def draw(self, surf, font):
        for i, ch in enumerate(self.chars):
            cy = self.y + i*self.char_size - int(self.head_pos)
            if not (self.y <= cy <= self.y + self.h):
                continue
            dist = abs(cy - (self.y + self.head_pos - self.char_size*2))
            if dist < self.char_size*3:
                col = lerp_col(self.color, C_WHITE, (1 - dist/(self.char_size*3))*0.6)
            else:
                fade = max(0, 1 - dist/(self.char_size*8))
                if fade < 0.08:
                    continue
                col = lerp_col(C_BLACK, self.color, fade*0.55)
            try:
                surf.blit(font.render(ch, True, col), (self.x, cy))
            except Exception:
                pass

# ═══════════════════════════════════════════════════════════════════════════════
#  ARC REACTOR
# ═══════════════════════════════════════════════════════════════════════════════
class ArcReactor:
    def __init__(self, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r
        self.rot        = 0.0
        self.rot2       = 0.0
        self.rot3       = 0.0
        self.pulse      = 1.0
        self.pulse_dir  = 1
        self.charge     = 1.0
        self.particles  = ParticleSystem()
        self.bolts      = []
        self.bolt_timer = 0
        self.ring_phase = [random.uniform(0, math.tau) for _ in range(5)]
        self.flare_timer = 0
        self.flare_active = False
        self.flare_alpha  = 0

    def update(self, t):
        c = self.charge
        self.rot  = (self.rot  + 1.10) % 360
        self.rot2 = (self.rot2 - 0.65) % 360
        self.rot3 = (self.rot3 + 0.30) % 360

        self.pulse += self.pulse_dir * 0.018
        if self.pulse > 1.16 or self.pulse < 0.84:
            self.pulse_dir *= -1

        for i in range(5):
            self.ring_phase[i] += 0.025 + i*0.008

        if c >= 1.0 and random.random() < 0.40:
            ang = math.radians(random.uniform(0, 360))
            x   = self.cx + math.cos(ang)*self.r*0.88
            y   = self.cy + math.sin(ang)*self.r*0.88
            col = random.choice([C_CYAN, C_GOLD, C_PLASMA, C_WHITE])
            self.particles.emit(x, y, 1, random.uniform(1.2, 3.0),
                                col, life_range=(22,55), size=random.randint(1,3))

        self.bolt_timer += 1
        if self.bolt_timer > 16 and c >= 1.0:
            self.bolt_timer = 0
            if random.random() < 0.65:
                a1  = math.radians(random.uniform(0, 360))
                a2  = a1 + math.radians(random.uniform(55, 175))
                ri  = self.r*0.28
                ro  = self.r*0.82
                self.bolts.append({
                    'p1'   : (self.cx + math.cos(a1)*ri, self.cy + math.sin(a1)*ri),
                    'p2'   : (self.cx + math.cos(a2)*ro, self.cy + math.sin(a2)*ro),
                    'life' : random.randint(3, 9),
                    'color': random.choice([C_CYAN, C_GOLD, (200,255,255), C_PLASMA])
                })
        self.bolts = [b for b in self.bolts if b['life'] > 0]
        for b in self.bolts:
            b['life'] -= 1

        self.flare_timer += 1
        if self.flare_timer > random.randint(80, 200):
            self.flare_timer  = 0
            self.flare_active = True
            self.flare_alpha  = 160
        if self.flare_active:
            self.flare_alpha -= 8
            if self.flare_alpha <= 0:
                self.flare_active = False
                self.flare_alpha  = 0

        self.particles.update()

    def draw(self, surf, t):
        cx, cy, r = self.cx, self.cy, self.r
        c         = self.charge

        if self.flare_active and self.flare_alpha > 0:
            flare_r = int(r * 1.8)
            fs = pygame.Surface((flare_r*2+4, flare_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(fs, (*C_CYAN, self.flare_alpha//4), (flare_r+2, flare_r+2), flare_r)
            surf.blit(fs, (cx-flare_r-2, cy-flare_r-2), special_flags=pygame.BLEND_RGBA_ADD)

        halo_r = int(r * 1.42 * self.pulse)
        circle_glow(surf, cx, cy, halo_r, C_CYAN, layers=9, alpha_start=55)

        for i in range(48):
            a1 = math.radians(360/48*i + self.rot)
            a2 = math.radians(360/48*i + 6.5 + self.rot)
            rr = int(r*1.28)
            x1 = cx + math.cos(a1)*rr;       y1 = cy + math.sin(a1)*rr
            x2 = cx + math.cos(a2)*(rr+8);   y2 = cy + math.sin(a2)*(rr+8)
            bright = (math.sin(a1*3 + t*2) + 1)/2
            col = lerp_col(C_CYAN_DIM, C_CYAN, bright*c)
            if sum(col) > 20:
                pygame.draw.line(surf, col, (int(x1),int(y1)), (int(x2),int(y2)), 2)

        for i in range(24):
            a  = math.radians(360/24*i + self.rot2)
            r2 = int(r*1.18)
            x  = cx + math.cos(a)*r2
            y  = cy + math.sin(a)*r2
            br = (math.sin(a*4 - t*3) + 1)/2
            col = lerp_col(C_GOLD_DIM, C_GOLD, br*c)
            sz = 4 if br > 0.6 else 2
            pygame.draw.circle(surf, col, (int(x), int(y)), sz)

        for layer in range(3):
            rr      = int(r*(0.78 + layer*0.115))
            phase   = self.ring_phase[layer]
            alpha   = int(190 * (0.5 + 0.5*math.sin(phase)) * c)
            pts     = hexagon_pts(cx, cy, rr, self.rot3 * 0.4 + layer*20)
            col     = C_CYAN if layer % 2 == 0 else C_GOLD
            ps      = pygame.Surface((rr*2+4, rr*2+4), pygame.SRCALPHA)
            ppts    = [(p[0]-cx+rr+2, p[1]-cy+rr+2) for p in pts]
            pygame.draw.polygon(ps, (*col, alpha), ppts, 2)
            surf.blit(ps, (cx-rr-2, cy-rr-2), special_flags=pygame.BLEND_RGBA_ADD)

        rr2   = int(r*1.10)
        pts2  = hexagon_pts(cx, cy, rr2, -self.rot3*0.22)
        ps2   = pygame.Surface((rr2*2+4, rr2*2+4), pygame.SRCALPHA)
        ppts2 = [(p[0]-cx+rr2+2, p[1]-cy+rr2+2) for p in pts2]
        alpha2 = int(90 * c)
        pygame.draw.polygon(ps2, (*C_CYAN_DIM, alpha2), ppts2, 1)
        surf.blit(ps2, (cx-rr2-2, cy-rr2-2), special_flags=pygame.BLEND_RGBA_ADD)

        body_r = int(r*0.72)
        pygame.draw.circle(surf, (5, 16, 30), (cx, cy), body_r)
        pygame.draw.circle(surf, C_CYAN,       (cx, cy), body_r, 2)
        circle_glow(surf, cx, cy, body_r, C_CYAN, layers=4, alpha_start=38)

        tri_r = int(body_r*0.58)
        for i in range(3):
            a1  = math.radians(120*i  + self.rot*0.7 - 30)
            a2  = math.radians(120*(i+1) + self.rot*0.7 - 30)
            mid_a = (a1 + a2)/2
            p1  = (cx + math.cos(a1)*tri_r,    cy + math.sin(a1)*tri_r)
            p2  = (cx + math.cos(a2)*tri_r,    cy + math.sin(a2)*tri_r)
            pc  = (cx + math.cos(mid_a)*tri_r*0.42, cy + math.sin(mid_a)*tri_r*0.42)
            br  = (math.sin(t*2 + i*2.094) + 1)/2
            col = lerp_col(C_CYAN_DIM, C_CYAN, br)
            draw_glow_line(surf, (int(p1[0]),int(p1[1])),
                           (int(p2[0]),int(p2[1])), col, 2, 55)
            draw_glow_line(surf, (int(p1[0]),int(p1[1])),
                           (int(pc[0]),int(pc[1])), col, 1, 30)
            draw_glow_line(surf, (int(p2[0]),int(p2[1])),
                           (int(pc[0]),int(pc[1])), col, 1, 30)

        for i in range(12):
            a   = math.radians(360/12*i + self.rot*1.3)
            rsi = int(body_r*0.22)
            rso = int(body_r*0.62)
            x1  = cx + math.cos(a)*rsi;  y1 = cy + math.sin(a)*rsi
            x2  = cx + math.cos(a)*rso;  y2 = cy + math.sin(a)*rso
            br  = (math.sin(a*2 - t*3) + 1)/2
            col = lerp_col((0,55,85), C_CYAN, br*c)
            pygame.draw.line(surf, col, (int(x1),int(y1)), (int(x2),int(y2)), 1)

        for i in range(8):
            a   = math.radians(360/8*i - self.rot*0.8)
            rsi = int(body_r*0.30)
            rso = int(body_r*0.52)
            x1  = cx + math.cos(a)*rsi;  y1 = cy + math.sin(a)*rsi
            x2  = cx + math.cos(a)*rso;  y2 = cy + math.sin(a)*rso
            col = lerp_col(C_GOLD_DIM, C_GOLD,
                           (math.sin(a*3 + t*2) + 1)/2 * c)
            pygame.draw.line(surf, col, (int(x1),int(y1)), (int(x2),int(y2)), 1)

        for b in self.bolts:
            lt  = b['life'] / 9
            col = lerp_col(C_WHITE, b['color'], 1 - lt)
            p1, p2 = b['p1'], b['p2']
            prev = p1
            for s in range(1, 7):
                tt   = s/6
                mx   = lerp(p1[0], p2[0], tt) + random.gauss(0, 5*(1-tt))
                my   = lerp(p1[1], p2[1], tt) + random.gauss(0, 5*(1-tt))
                draw_glow_line(surf, (int(prev[0]),int(prev[1])),
                               (int(mx),int(my)), col, 1, 45)
                prev = (mx, my)

        core_r = int(body_r*0.22 * self.pulse)
        circle_glow(surf, cx, cy, core_r, C_GOLD, layers=5, alpha_start=130)
        pygame.draw.circle(surf, C_GOLD,  (cx, cy), core_r)
        pygame.draw.circle(surf, C_WHITE, (cx, cy), max(2, core_r//3))

        self.particles.draw(surf)

# ═══════════════════════════════════════════════════════════════════════════════
#  HUD PANEL
# ═══════════════════════════════════════════════════════════════════════════════
class HUDPanel:
    def __init__(self, rect, sentences, idx):
        self.rect          = rect
        self.sentences     = sentences
        self.idx           = idx
        self.scan_offset   = random.uniform(0, 1)
        self.glitch_timer  = random.randint(60, 240)
        self.glitch_on     = False
        self.glitch_cd     = 0
        self.blink         = True
        self.blink_timer   = random.randint(20, 60)
        self.data_val      = random.randint(20, 95)
        self.data_timer    = 0
        self.data_sparkline = [random.randint(20,80) for _ in range(16)]
        self.spark_timer   = 0

    def update(self, t):
        self.scan_offset = (self.scan_offset + 0.007) % 1.0
        self.data_timer += 1
        if self.data_timer > 28:
            self.data_timer = 0
            self.data_val = clamp(self.data_val + random.randint(-6,6), 5, 98)

        self.spark_timer += 1
        if self.spark_timer > 14:
            self.spark_timer = 0
            self.data_sparkline.append(self.data_val + random.randint(-8,8))
            if len(self.data_sparkline) > 16:
                self.data_sparkline.pop(0)

        self.glitch_timer -= 1
        if self.glitch_timer <= 0:
            self.glitch_on    = True
            self.glitch_cd    = random.randint(2, 7)
            self.glitch_timer = random.randint(90, 320)
        if self.glitch_on:
            self.glitch_cd -= 1
            if self.glitch_cd <= 0:
                self.glitch_on = False

        self.blink_timer -= 1
        if self.blink_timer <= 0:
            self.blink       = not self.blink
            self.blink_timer = random.randint(18, 50)

    def draw(self, surf, font, sfont, t):
        rect = self.rect
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        pygame.draw.rect(surf, (5, 11, 19), rect, border_radius=4)

        scan_y = int(rect.top + self.scan_offset * rect.height)
        for dy in range(-8, 9):
            ly = scan_y + dy
            if rect.top < ly < rect.bottom:
                alpha = max(0, 75 - abs(dy)*8)
                sl = pygame.Surface((rect.width-4, 1), pygame.SRCALPHA)
                sl.fill((0, 200, 255, alpha))
                surf.blit(sl, (rect.left+2, ly), special_flags=pygame.BLEND_RGBA_ADD)

        if self.glitch_on:
            offx = random.randint(-5, 5)
            offy = random.randint(-2, 2)
            gs   = pygame.Surface((rect.width, rect.height//3), pygame.SRCALPHA)
            pygame.draw.rect(gs, (0, 200, 255, 28), (0,0,rect.width,rect.height//3))
            surf.blit(gs, (rect.x+offx, rect.y+offy), special_flags=pygame.BLEND_RGBA_ADD)

        bdr_col  = C_RED if self.glitch_on else C_PANEL_BDR
        cl       = min(13, w//5, h//4)

        def corner(px, py, dx, dy):
            pygame.draw.line(surf, bdr_col, (px, py), (px+dx*cl, py),      2)
            pygame.draw.line(surf, bdr_col, (px, py), (px,        py+dy*cl), 2)

        corner(x,     y,     +1, +1)
        corner(x+w-1, y,     -1, +1)
        corner(x,     y+h-1, +1, -1)
        corner(x+w-1, y+h-1, -1, -1)
        pygame.draw.rect(surf, (0, 55, 78), rect, 1, border_radius=4)

        inner = rect.inflate(-10, -8)

        sent  = self.sentences[self.idx % len(self.sentences)]
        lines = wrap_lines(sent, font, inner.width-4, max_lines=2)
        for i, ln in enumerate(lines):
            col = lerp_col(C_CYAN_DIM, C_CYAN, 0.55 + 0.45*math.sin(t + self.idx*0.7))
            surf.blit(font.render(ln, True, col),
                      (inner.left+2, inner.top+2 + i*(font.get_height()+1)))

        spark_y = inner.bottom - 16
        spark_w = inner.width - 4
        n       = len(self.data_sparkline)
        if n > 1:
            mn, mx_v = min(self.data_sparkline), max(self.data_sparkline)
            span     = max(1, mx_v - mn)
            pts      = []
            for si, sv in enumerate(self.data_sparkline):
                sx = inner.left + 2 + int(si*(spark_w-4)/(n-1))
                sy = spark_y - int((sv-mn)/span * 10)
                pts.append((sx, sy))
            if len(pts) > 1:
                pygame.draw.lines(surf, C_CYAN_DIM, False, pts, 1)
                pygame.draw.circle(surf, C_CYAN, pts[-1], 2)

        bar_y  = inner.bottom - 5
        bar_fw = inner.width - 4
        bar_fi = int(bar_fw * self.data_val / 100)
        pygame.draw.rect(surf, (10,28,40), (inner.left+2, bar_y-3, bar_fw, 3), border_radius=1)
        bar_col = C_RED if self.data_val > 85 else (C_GOLD if self.data_val > 65 else C_GREEN)
        pygame.draw.rect(surf, bar_col, (inner.left+2, bar_y-3, bar_fi, 3), border_radius=1)

        dot_col = C_GREEN if self.blink else C_GREEN_DIM
        pygame.draw.circle(surf, dot_col, (inner.right-8, inner.top+8), 4)
        val_s   = sfont.render(f"{self.data_val:02d}%", True, C_GOLD)
        surf.blit(val_s, (inner.right - val_s.get_width()-2, inner.top+2))

# ═══════════════════════════════════════════════════════════════════════════════
#  LAYOUT COMPUTATION - UPGRADED TO CENTERED
# ═══════════════════════════════════════════════════════════════════════════════
def compute_layout(w, h):
    margin  = max(16, int(min(w, h)*0.03))
    
    # 1. ARC REACTOR TO THE DEAD CENTER
    core_r  = max(90, min(int(min(w,h)*0.22), 260))
    core_cx = w // 2
    core_cy = h // 2

    # 2. PANELS AROUND IT (Left & Right Split)
    panel_w = max(180, int(w * 0.20))
    panel_h = max(60, int(h * 0.10))
    gap_y   = max(10, int(h * 0.02))

    panels = []
    start_y = margin + 110 # Push down to make room for titles

    # Left Side Panels (2 panels)
    left_gx = margin
    for i in range(2):
        pr = pygame.Rect(left_gx, start_y + i*(panel_h+gap_y), panel_w, panel_h)
        panels.append(pr)

    # Right Side Panels (3 panels)
    right_gx = w - margin - panel_w
    for i in range(3):
        pr = pygame.Rect(right_gx, start_y + i*(panel_h+gap_y), panel_w, panel_h)
        panels.append(pr)

    title_fs = max(24, min(int(core_r*0.4), 50))
    body_fs  = max(12, min(int(core_r*0.15), 18))
    small_fs = max(10, min(int(core_r*0.12), 14))

    return dict(
        margin=margin, core_cx=core_cx, core_cy=core_cy,
        core_radius=core_r, panels=panels,
        title_fs=title_fs, body_fs=body_fs, small_fs=small_fs,
        w=w, h=h, panel_w=panel_w
    )

def make_fonts(lay):
    tf = pygame.font.SysFont("Consolas", lay['title_fs'], bold=True)
    bf = pygame.font.SysFont("Consolas", lay['body_fs'])
    sf = pygame.font.SysFont("Consolas", lay['small_fs'])
    return tf, bf, sf

# ═══════════════════════════════════════════════════════════════════════════════
#  BOOT SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════
def draw_startup(surf, progress, t, lay, font, sfont, tfont, boot_particles):
    w, h    = lay['w'], lay['h']
    cx, cy  = lay['core_cx'], lay['core_cy']
    r       = lay['core_radius']
    margin  = lay['margin']

    surf.fill(C_BLACK)

    grid_alpha = int(28 * progress)
    if grid_alpha > 0:
        gs  = pygame.Surface((w, h), pygame.SRCALPHA)
        gsz = 36
        for gx in range(0, w, gsz):
            pygame.draw.line(gs, (0, 80, 120, grid_alpha), (gx, 0), (gx, h), 1)
        for gy in range(0, h, gsz):
            pygame.draw.line(gs, (0, 80, 120, grid_alpha), (0, gy), (w, gy), 1)
        surf.blit(gs, (0,0))

    if progress < 0.96:
        bar_y = int(h * progress)
        for dy in range(-4, 5):
            ly = bar_y + dy
            if 0 <= ly < h:
                al = max(0, 110 - abs(dy)*22)
                sl = pygame.Surface((w, 1), pygame.SRCALPHA)
                sl.fill((0, 240, 255, al))
                surf.blit(sl, (0, ly), special_flags=pygame.BLEND_RGBA_ADD)

    circle_glow(surf, cx, cy, int(r*1.4), lerp_col(C_CYAN_DIM, C_CYAN, progress), layers=6, alpha_start=int(75*progress))

    for i in range(36):
        a1 = math.radians(360/36*i + t*110)
        a2 = math.radians(360/36*i + 7.5 + t*110)
        rr = int(r*1.26)
        x1 = cx + math.cos(a1)*rr;       y1 = cy + math.sin(a1)*rr
        x2 = cx + math.cos(a2)*(rr+9);   y2 = cy + math.sin(a2)*(rr+9)
        if (i/36) <= progress:
            br  = (math.sin(a1*3 + t*4)+1)/2
            col = lerp_col(C_CYAN_DIM, C_CYAN, br)
            pygame.draw.line(surf, col, (int(x1),int(y1)), (int(x2),int(y2)), 2)

    if progress > 0.08:
        p2     = clamp((progress-0.08)/0.92, 0, 1)
        body_r = int(r*0.70*p2)
        pygame.draw.circle(surf, (4, 12, 22), (cx, cy), body_r)
        pygame.draw.circle(surf, lerp_col(C_CYAN_DIM, C_CYAN, p2), (cx, cy), body_r, 2)

    if progress > 0.32:
        p3    = clamp((progress-0.32)/0.68, 0, 1)
        tri_r = int(r*0.70*0.58*p3)
        for i in range(3):
            a1   = math.radians(120*i  + t*65 - 30)
            a2   = math.radians(120*(i+1) + t*65 - 30)
            mid_a= (a1+a2)/2
            p1c  = (cx + math.cos(a1)*tri_r, cy + math.sin(a1)*tri_r)
            p2c  = (cx + math.cos(a2)*tri_r, cy + math.sin(a2)*tri_r)
            pcc  = (cx + math.cos(mid_a)*tri_r*0.42, cy + math.sin(mid_a)*tri_r*0.42)
            col  = lerp_col(C_CYAN_DIM, C_CYAN, p3)
            draw_glow_line(surf,(int(p1c[0]),int(p1c[1])),(int(p2c[0]),int(p2c[1])),col,2,int(55*p3))
            draw_glow_line(surf,(int(p1c[0]),int(p1c[1])),(int(pcc[0]),int(pcc[1])),col,1,int(30*p3))
            draw_glow_line(surf,(int(p2c[0]),int(p2c[1])),(int(pcc[0]),int(pcc[1])),col,1,int(30*p3))

    if progress > 0.58:
        p4     = clamp((progress-0.58)/0.42, 0, 1)
        core_r = int(r*0.70*0.22 * p4 * (0.9 + 0.1*math.sin(t*8)))
        circle_glow(surf, cx, cy, core_r, C_GOLD, layers=4, alpha_start=int(125*p4))
        pygame.draw.circle(surf, lerp_col(C_GOLD_DIM, C_GOLD, p4), (cx, cy), max(1, core_r))

    if progress > 0.86 and random.random() < 0.45:
        ang = math.radians(random.uniform(0, 360))
        boot_particles.emit(
            cx + math.cos(ang)*r, cy + math.sin(ang)*r,
            2, random.uniform(1.5, 3.5),
            random.choice([C_CYAN, C_GOLD, C_PLASMA]),
            life_range=(20,52), size=2)

    boot_particles.update()
    boot_particles.draw(surf)

    n = len(lay['panels'])
    for idx, rect in enumerate(lay['panels']):
        pp = clamp((progress - idx/n*0.65) / 0.50, 0, 1)
        if pp <= 0:
            continue
        bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg, (5,13,23, int(200*pp)), (0,0,rect.width,rect.height), border_radius=4)
        surf.blit(bg, rect.topleft)

        cl  = min(rect.width, rect.height)//4
        aln = int(cl*pp)
        bs  = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bdc = (*C_PANEL_BDR, int(220*pp))
        for (px,py,dx,dy) in [(0,0,1,0),(0,0,0,1),
                               (rect.width-1,0,-1,0),(rect.width-1,0,0,1),
                               (0,rect.height-1,1,0),(0,rect.height-1,0,-1),
                               (rect.width-1,rect.height-1,-1,0),(rect.width-1,rect.height-1,0,-1)]:
            pygame.draw.line(bs, bdc, (px,py), (px+dx*aln, py+dy*aln), 2)
        surf.blit(bs, rect.topleft)

        wipe_w = int(rect.width*pp)
        if wipe_w > 0:
            inner  = rect.inflate(-8,-6)
            wipe   = pygame.Surface((wipe_w, inner.height), pygame.SRCALPHA)
            for sdy in range(0, inner.height, 3):
                sal = int(22 + 14*math.sin(sdy*0.3 + t*5))
                pygame.draw.line(wipe, (0,200,255,sal), (0,sdy), (wipe_w,sdy), 1)
            surf.blit(wipe, inner.topleft)

        if pp > 0.5:
            ta    = int(255*(pp-0.5)/0.5)
            inner = rect.inflate(-10,-8)
            sent  = TECH_SENTENCES[idx % len(TECH_SENTENCES)]
            lns   = wrap_lines(sent, font, inner.width-4, max_lines=2)
            for li, ln in enumerate(lns):
                s2 = font.render(ln, True, C_CYAN)
                s2.set_alpha(ta)
                surf.blit(s2, (inner.left+2, inner.top+2+li*(font.get_height()+2)))

    active_msg = ""
    for thresh, msg in BOOT_MSGS:
        if progress >= thresh:
            active_msg = msg
    if active_msg:
        bs = font.render(f"// {active_msg}", True, C_CYAN)
        surf.blit(bs, (cx - bs.get_width()//2, h - margin - 80))

    # Fix: Titles moved up to not overlap with reactor
    a_t = int(255*clamp(progress*3, 0, 1))
    js  = tfont.render("J A R V I S", True, C_CYAN)
    js.set_alpha(a_t)
    jr  = js.get_rect(center=(cx, margin + 40))
    surf.blit(js, jr)

    if progress > 0.38:
        sub = sfont.render("STARK INDUSTRIES  //  MARK VII  //  CLASSIFIED", True, C_GREY)
        sr  = sub.get_rect(center=(cx, margin + 70))
        surf.blit(sub, sr)

    pct = sfont.render(f"{int(progress*100):3d}%", True, C_GOLD)
    surf.blit(pct, (cx - pct.get_width()//2, cy + r + 20))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN HUD DRAW
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hud(surf, reactor, panels, lay, font, sfont, tfont,
             data_streams, output_lines, input_text, t, thinking):
    w, h    = lay['w'], lay['h']
    cx, cy  = lay['core_cx'], lay['core_cy']
    r       = lay['core_radius']
    margin  = lay['margin']

    surf.fill(C_DARK)

    # ── background grid ──
    gs = pygame.Surface((w, h), pygame.SRCALPHA)
    for gx in range(0, w, 40):
        pygame.draw.line(gs, (0, 50, 80, 10), (gx, 0), (gx, h), 1)
    for gy in range(0, h, 40):
        pygame.draw.line(gs, (0, 50, 80, 10), (0, gy), (w, gy), 1)
    surf.blit(gs, (0, 0))

    # ── data streams ──
    for ds in data_streams:
        ds.update()
        ds.draw(surf, sfont)

    # ── arc reactor (Centered) ──
    reactor.update(t)
    reactor.draw(surf, t)

    # ── JARVIS label (Top Center, No Overlap) ──
    jcol = lerp_col(C_CYAN_DIM, C_CYAN, 0.6 + 0.4*math.sin(t*1.2))
    js   = tfont.render("J A R V I S", True, jcol)
    jr   = js.get_rect(center=(cx, margin + 40))
    surf.blit(js, jr)

    sub_str = "STARK TECH  //  ONLINE  //  SECURE"
    if thinking:
        dots = "." * (1 + int(t*2) % 3)
        sub_str = f"JARVIS PROCESSING{dots}"
    sub = sfont.render(sub_str, True, lerp_col(C_GREY, C_CYAN_DIM, 0.4+0.3*math.sin(t*0.8)))
    sr  = sub.get_rect(center=(cx, margin + 70))
    surf.blit(sub, sr)

    if thinking:
        for i in range(6):
            a   = math.radians(60*i + t*180)
            rr  = int(r*1.50)
            dot_x = cx + int(math.cos(a)*rr)
            dot_y = cy + int(math.sin(a)*rr)
            alpha = int(180 * (math.sin(t*4 + i*1.05)+1)/2)
            ds2   = pygame.Surface((12,12), pygame.SRCALPHA)
            pygame.draw.circle(ds2, (*C_GOLD, alpha), (6,6), 5)
            surf.blit(ds2, (dot_x-6, dot_y-6), special_flags=pygame.BLEND_RGBA_ADD)

    # ── HUD panels ──
    for panel in panels:
        panel.update(t)
        panel.draw(surf, font, sfont, t)

    # ── log area (Now on the bottom left, clear of panels) ──
    # The left panels end at margin + 110 + 2*(60+10). So we start below them.
    log_x = margin
    log_y = margin + 110 + 2 * (max(60, int(h * 0.10)) + max(10, int(h * 0.02))) + 20
    log_w = lay['panel_w']
    bar_h = max(24, int(h*0.032))
    log_h = h - log_y - bar_h - 20

    if log_h > 40: # Only draw if there's space
        lb    = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
        pygame.draw.rect(lb, (3, 9, 16, 155), (0, 0, log_w, log_h), border_radius=4)
        pygame.draw.rect(lb, (0, 60, 80, 100), (0, 0, log_w, log_h), 1, border_radius=4)
        surf.blit(lb, (log_x, log_y))

        lh   = font.get_height() + 3
        rows = max(1, log_h // lh) - 1
        for li, line in enumerate(output_lines[-rows:]):
            col = (C_GREEN  if line.startswith("JARVIS>") else
                   C_RED    if "[ERROR]" in line else
                   C_GOLD   if "[SYSTEM]" in line else
                   C_ORANGE if line.startswith("YOU>") else
                   C_CYAN_DIM)
            tl  = truncate(line, font, log_w - 8)
            s2  = font.render(tl, True, col)
            surf.blit(s2, (log_x+4, log_y+4 + li*lh))

    # ── bottom status bar ──
    bb    = pygame.Surface((w, bar_h), pygame.SRCALPHA)
    pygame.draw.rect(bb, (0, 28, 48, 185), (0, 0, w, bar_h))
    surf.blit(bb, (0, h-bar_h))
    pygame.draw.line(surf, C_CYAN_DIM, (0, h-bar_h), (w, h-bar_h), 1)

    items = [
        f"SYS: ONLINE",
        f"PWR: {int(85+10*math.sin(t*0.7)):3d}%",
        f"TEMP: {int(22+4*math.sin(t*0.5))}°C",
        f"SEC: LVL-5",
        f"AI: {'THINKING' if thinking else 'READY'}",
    ]
    sx = 12
    for item in items:
        s2 = sfont.render(item, True, C_GOLD if "THINKING" in item else C_CYAN_DIM)
        if sx + s2.get_width() < w - 20:
            surf.blit(s2, (sx, h-bar_h + (bar_h-s2.get_height())//2))
            sx += s2.get_width() + 28

    # ── NEW: Wide Centered High-Tech Input Console ──
    input_w = int(w * 0.55) # 55% of screen width
    input_h = max(45, font.get_height() + 20)
    ix = w // 2 - input_w // 2
    iy = h - bar_h - input_h - 20 # Anchor just above the bottom bar
    ire = pygame.Rect(ix, iy, input_w, input_h)

    pygame.draw.rect(surf, (3, 10, 20, 220), ire)
    bdr_col = C_GOLD if thinking else C_CYAN_DIM

    # Draw intricate tech bracket corners
    cl = 20
    pygame.draw.line(surf, bdr_col, (ix, iy), (ix+cl, iy), 3)
    pygame.draw.line(surf, bdr_col, (ix, iy), (ix, iy+cl), 3)
    pygame.draw.line(surf, bdr_col, (ix+input_w-cl, iy), (ix+input_w, iy), 3)
    pygame.draw.line(surf, bdr_col, (ix+input_w, iy), (ix+input_w, iy+cl), 3)
    pygame.draw.line(surf, bdr_col, (ix, iy+input_h), (ix+cl, iy+input_h), 3)
    pygame.draw.line(surf, bdr_col, (ix, iy+input_h-cl), (ix, iy+input_h), 3)
    pygame.draw.line(surf, bdr_col, (ix+input_w-cl, iy+input_h), (ix+input_w, iy+input_h), 3)
    pygame.draw.line(surf, bdr_col, (ix+input_w, iy+input_h-cl), (ix+input_w, iy+input_h), 3)
    pygame.draw.rect(surf, (0, 55, 78), ire, 1)

    # Scanline background inside input
    for sdy in range(0, input_h, 4):
        al  = int(14 + 9*math.sin(sdy*0.5 + t*4))
        sl  = pygame.Surface((input_w-4, 1), pygame.SRCALPHA)
        sl.fill((0, 200, 255, al))
        surf.blit(sl, (ire.left+2, ire.top+sdy))

    disp = truncate("> " + input_text, font, input_w-30)
    ts   = font.render(disp, True, C_GREEN)
    surf.blit(ts, (ire.left+15, ire.top+(input_h-ts.get_height())//2))

    # Blinking block cursor
    if int(t*2) % 2 == 0:
        cx2 = ire.left + 15 + font.size(disp)[0] + 2
        cy2 = ire.top + (input_h-font.get_height())//2
        pygame.draw.rect(surf, C_GREEN, (cx2, cy2, 6, font.get_height()))

    # Input instructions centered above or below the box
    hint = sfont.render("ENTER to transmit  |  ESC to exit", True, C_GREY)
    surf.blit(hint, (w//2 - hint.get_width()//2, iy - hint.get_height() - 4))

    # ── radial sweep from core ──
    sweep_a = math.radians(t*44 % 360)
    gl_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for da in range(0, 50, 6):
        a    = sweep_a + math.radians(da)
        fade = max(0, 1 - da/50)
        if fade <= 0:
            break
        ex = cx + math.cos(a)*r*3.5
        ey = cy + math.sin(a)*r*3.5
        al = int(9*fade)
        pygame.draw.line(gl_surf, (*C_CYAN, al), (cx, cy), (int(ex), int(ey)), 1)
    surf.blit(gl_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

# ═══════════════════════════════════════════════════════════════════════════════
#  AI CORE
# ═══════════════════════════════════════════════════════════════════════════════
def choose_model(prompt: str) -> str:
    lower = prompt.lower()
    if any(w in lower for w in ["project","framework","backend","frontend",
                                 "multi-file","complex","algorithm","system","database"]):
        return MODEL_CODE_BIG
    if "code" in lower or any(w in lower for w in ["snippet","example","basic",
                                                     "simple","small","quick","short"]):
        return MODEL_CODE_FAST
    if any(w in lower for w in ["image","picture","photo","see","vision"]):
        return MODEL_VISION
    return MODEL_DEFAULT

def speak(text: str):
    def _do():
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or "male" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception:
            pass
    threading.Thread(target=_do, daemon=True).start()

def ask_ai(prompt: str, output_lines: list, history: list, thinking_flag: list):
    def worker():
        thinking_flag[0] = True
        model = choose_model(prompt)
        output_lines.append(f"[SYSTEM] Model: {model}")

        messages = [{"role": "system", "content": JARVIS_SYSTEM}] + history

        try:
            response = ollama.chat(model=model, messages=messages)
            answer   = response["message"]["content"]

            history.append({"role": "assistant", "content": answer})

            for line in answer.split("\n"):
                if line.strip():
                    output_lines.append("JARVIS> " + line)

            first_sentence = answer.split(".")[0].strip()
            if len(first_sentence) > 5:
                speak(first_sentence[:300])

            if "```" in answer:
                try:
                    code_block = answer.split("```")[1]
                    if code_block.startswith(("\n","python","js","bash","cpp","c\n")):
                        code_block = "\n".join(code_block.split("\n")[1:])
                    pyperclip.copy(code_block.strip())
                    output_lines.append("[SYSTEM] Code copied to clipboard.")
                except Exception:
                    pass

        except ollama.ResponseError as e:
            output_lines.append(f"[ERROR] Ollama: {e.error}")
            output_lines.append("[ERROR] Is the model pulled? Run: ollama pull " + model)
        except Exception as e:
            output_lines.append(f"[ERROR] {type(e).__name__}: {e}")

        thinking_flag[0] = False

    threading.Thread(target=worker, daemon=True).start()

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def run():
    global WIDTH, HEIGHT

    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("JARVIS  //  STARK INDUSTRIES  //  MARK VII")

    boot_duration = 6.0
    if os.path.isfile(BOOT_SOUND_PATH):
        try:
            boot_snd    = pygame.mixer.Sound(BOOT_SOUND_PATH)
            boot_duration = boot_snd.get_length()
            boot_snd.play()
        except Exception:
            boot_duration = 6.0

    layout = compute_layout(WIDTH, HEIGHT)
    tfont, font, sfont = make_fonts(layout)

    boot_particles = ParticleSystem()
    reactor = ArcReactor(layout['core_cx'], layout['core_cy'], layout['core_radius'])
    
    hud_panels = [HUDPanel(rect, TECH_SENTENCES, i)
                  for i, rect in enumerate(layout['panels'])]

    # Data streams now distribute across the entire screen background width
    def make_streams(lay, sf):
        streams = []
        count = max(5, lay['w'] // 100)
        for si in range(count):
            streams.append(DataStream(
                random.randint(0, lay['w']),
                lay['margin'],
                lay['h'] - lay['margin']*2,
                random.choice([C_CYAN, C_PLASMA, C_GOLD]),
                speed=random.uniform(1.2, 2.6),
                char_size=sf.get_height()
            ))
        return streams

    data_streams = make_streams(layout, sfont)

    conversation_history = []
    output_lines         = []
    input_text           = ""
    thinking_flag        = [False]
    boot_done            = False
    boot_start           = pygame.time.get_ticks()
    clock                = pygame.time.Clock()

    while True:
        clock.tick(TARGET_FPS)
        now_ms  = pygame.time.get_ticks()
        t       = now_ms / 1000.0
        elapsed = (now_ms - boot_start) / 1000.0
        progress = min(1.0, elapsed / max(0.001, boot_duration))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen        = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                layout        = compute_layout(WIDTH, HEIGHT)
                tfont, font, sfont = make_fonts(layout)
                reactor       = ArcReactor(layout['core_cx'], layout['core_cy'],
                                           layout['core_radius'])
                hud_panels    = [HUDPanel(rect, TECH_SENTENCES, i)
                                 for i, rect in enumerate(layout['panels'])]
                data_streams  = make_streams(layout, sfont)

            elif event.type == pygame.KEYDOWN and boot_done:
                if event.key == pygame.K_RETURN:
                    txt = input_text.strip()
                    if txt and not thinking_flag[0]:
                        output_lines.append(f"YOU> {txt}")
                        conversation_history.append({"role":"user","content":txt})
                        ask_ai(txt, output_lines, conversation_history, thinking_flag)
                        input_text = ""

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

                else:
                    if event.unicode and ord(event.unicode) >= 32:
                        input_text += event.unicode

        if not boot_done:
            draw_startup(screen, progress, t, layout,
                         font, sfont, tfont, boot_particles)
            if progress >= 1.0:
                boot_done = True
                output_lines.append("[SYSTEM] Arc reactor online. Power at 100%.")
                output_lines.append("[SYSTEM] All systems nominal, sir.")
                output_lines.append("[SYSTEM] JARVIS standing by.")
        else:
            reactor.charge = 1.0
            draw_hud(screen, reactor, hud_panels, layout,
                     font, sfont, tfont, data_streams,
                     output_lines, input_text, t, thinking_flag[0])

        pygame.display.flip()

if __name__ == "__main__":
    run()