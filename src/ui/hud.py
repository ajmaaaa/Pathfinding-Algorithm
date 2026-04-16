import pygame
import pygame.freetype
from config import RIBBON_H

_font_cache: dict = {}

class SafeFont:
    def __init__(self, size, bold=False):
        if not pygame.freetype.was_init(): pygame.freetype.init()
        sz = max(8, int(size * 1.2))
        try: self.font = pygame.freetype.SysFont('arial, segoeui, sans-serif', sz)
        except:
            try: self.font = pygame.freetype.Font(pygame.font.get_default_font(), sz)
            except: self.font = None
        if self.font and bold: self.font.strong = True

    def render(self, text, antialias, color, background=None):
        if not self.font: return pygame.Surface((1, 1), pygame.SRCALPHA)
        try:
            surf, _ = self.font.render(str(text), color)
            if surf is None or surf.get_width() == 0 or surf.get_height() == 0:
                return pygame.Surface((1, 1), pygame.SRCALPHA)
            return surf
        except: return pygame.Surface((1, 1), pygame.SRCALPHA)

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache: _font_cache[key] = SafeFont(size, bold)
    return _font_cache[key]

def draw_badge(surf, text, W):
    if not text: return
    f   = get_font(12, bold=True); t = f.render(text, True, (146, 64, 14))
    pw  = t.get_width() + 40; ph = 30
    px  = W // 2 - pw // 2;  py = RIBBON_H + 14
    s   = pygame.Surface((pw, ph), pygame.SRCALPHA); s.fill((255, 251, 235, 240)); surf.blit(s, (px, py))
    pygame.draw.rect(surf, (251, 191, 36), (px, py, pw, ph), 2, border_radius=15)
    surf.blit(t, (px + 20, py + ph//2 - t.get_height()//2))

def draw_tooltip(screen, text, mx, my):
    fnt = get_font(12, bold=True)
    txt_surf = fnt.render(text, True, (248, 250, 252))
    pad = 12; w = txt_surf.get_width() + pad*2; h = 26
    bx = mx - w//2; by = my - h - 15
    pygame.draw.rect(screen, (30, 41, 59), (bx, by, w, h), border_radius=6)
    pygame.draw.rect(screen, (71, 85, 105), (bx, by, w, h), 1, border_radius=6)
    screen.blit(txt_surf, (bx + pad, by + h//2 - txt_surf.get_height()//2))