import pygame
import math
from config import C, RIBBON_H
from src.ui.hud import get_font

def draw_vector_icon(surf, name, cx, cy, color):
    if name == 'generate':
        pygame.draw.arc(surf, color, (cx-10, cy-11, 20, 20), math.radians(45), math.radians(315), 3)
        pygame.draw.polygon(surf, color, [(cx+6, cy-6), (cx+15, cy-4), (cx+10, cy+3)])
    elif name == 'acak':
        s = 8
        pygame.draw.polygon(surf, (167, 139, 250), [(cx, cy-s), (cx+s, cy-s/2), (cx, cy), (cx-s, cy-s/2)])
        pygame.draw.polygon(surf, (139, 92, 246), [(cx-s, cy-s/2), (cx, cy), (cx, cy+s), (cx-s, cy+s/2)])
        pygame.draw.polygon(surf, (124, 58, 237), [(cx, cy), (cx+s, cy-s/2), (cx+s, cy+s/2), (cx, cy+s)])
        c_white = (255, 255, 255)
        pygame.draw.circle(surf, c_white, (int(cx), int(cy-s/2)), 1.5)
        pygame.draw.circle(surf, c_white, (int(cx-s/2), int(cy+s/4)), 1.5)
        pygame.draw.circle(surf, c_white, (int(cx+s/2), int(cy+s/4)), 1.5)
    elif name == 'graph':
        col = (156, 163, 175)
        for r in [4, 8, 12]:
            pts = [(cx + math.cos(a)*r, cy + math.sin(a)*r) for a in [i*math.pi/3 for i in range(6)]]
            pygame.draw.polygon(surf, col, pts, 1)
        for i in range(6):
            a = i*math.pi/3
            pygame.draw.line(surf, col, (cx, cy), (cx + math.cos(a)*12, cy + math.sin(a)*12), 1)
    elif name == 'start':
        for r in range(12, 0, -1):
            f = r/12; base_col = (34, 197, 94)
            c = (min(255, int(base_col[0] + (255-base_col[0])*(1-f))), min(255, int(base_col[1] + (255-base_col[1])*(1-f))), min(255, int(base_col[2] + (255-base_col[2])*(1-f))))
            pygame.draw.circle(surf, c, (cx - (12-r)*0.3, cy - (12-r)*0.3), r)
    elif name == 'end':
        for r in range(12, 0, -1):
            f = r/12; base_col = (239, 68, 68)
            c = (min(255, int(base_col[0] + (255-base_col[0])*(1-f))), min(255, int(base_col[1] + (255-base_col[1])*(1-f))), min(255, int(base_col[2] + (255-base_col[2])*(1-f))))
            pygame.draw.circle(surf, c, (cx - (12-r)*0.3, cy - (12-r)*0.3), r)
    elif name == 'play': pygame.draw.polygon(surf, color, [(cx-5, cy-8), (cx+10, cy), (cx-5, cy+8)])
    elif name == 'pause':
        pygame.draw.rect(surf, color, (cx-6, cy-8, 4, 16), border_radius=1)
        pygame.draw.rect(surf, color, (cx+2, cy-8, 4, 16), border_radius=1)
    elif name == 'reset':
        col = (107, 114, 128)
        pygame.draw.arc(surf, col, (cx-10, cy-11, 20, 20), math.radians(225), math.radians(135), 3)
        pygame.draw.polygon(surf, col, [(cx-6, cy-6), (cx-15, cy-4), (cx-10, cy+3)])
    elif name == 'prev':
        col = (156, 163, 175)
        pygame.draw.rect(surf, col, (cx-8, cy-5, 2, 10))
        pygame.draw.polygon(surf, col, [(cx-2, cy-5), (cx-8, cy), (cx-2, cy+5)])
        pygame.draw.polygon(surf, col, [(cx+4, cy-5), (cx-2, cy), (cx+4, cy+5)])
    elif name == 'next':
        col = (156, 163, 175)
        pygame.draw.polygon(surf, col, [(cx-6, cy-5), (cx, cy), (cx-6, cy+5)])
        pygame.draw.polygon(surf, col, [(cx, cy-5), (cx+6, cy), (cx, cy+5)])
        pygame.draw.rect(surf, col, (cx+6, cy-5, 2, 10))


class RibbonButton:
    def __init__(self, x, y, w, h, icon, label, accent=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.icon_name = icon     
        self.label = label
        self.accent = accent
        self.hov = False; self.active = False; self.disabled = False

    def draw(self, surf):
        bg = C['ribbon_bg']; brd = None
        if not self.disabled:
            if self.active: bg = C['btn_act']; brd = C['btn_border']
            elif self.hov: bg = C['btn_hov']; brd = C['btn_border']

        pygame.draw.rect(surf, bg, self.rect, border_radius=5)
        if brd: pygame.draw.rect(surf, brd, self.rect, 1, border_radius=5)

        ico_col = self.accent if (self.accent and not self.disabled) else C['txt_dim']
        if self.disabled: txt_col = C['txt_dim']
        elif self.active: txt_col = C['stat_blue']
        else: txt_col = C['txt_dark']

        fl = get_font(10, bold=True)
        tl = fl.render(self.label, True, txt_col)
        cx = self.rect.x + self.rect.w // 2
        total_h = 24 + 4 + tl.get_height() 
        sy = self.rect.y + (self.rect.h - total_h) // 2
        
        draw_vector_icon(surf, self.icon_name, cx, sy + 12, ico_col)
        surf.blit(tl, (cx - tl.get_width()//2, sy + 24 + 4))


class MiniButton:
    def __init__(self, x, y, w, h, icon):
        self.rect = pygame.Rect(x, y, w, h)
        self.icon_name = icon
        self.hov = False; self.disabled = False
        
    def draw(self, surf):
        bg = C['white']; brd = C['ribbon_sep']; txt = C['txt_dark']
        if self.disabled: bg = C['ribbon_bg']; txt = C['txt_dim']
        elif self.hov: bg = C['btn_hov']; brd = C['btn_border']; txt = C['stat_blue']
            
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        pygame.draw.rect(surf, brd, self.rect, 1, border_radius=6)
        
        cx = self.rect.x + self.rect.w // 2; cy = self.rect.y + self.rect.h // 2
        draw_vector_icon(surf, self.icon_name, cx, cy, txt)


class Slider:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.disabled = True
        self.val = 0.0; self.max_val = 100.0; self.dragging = False

    def draw(self, surf):
        ty = self.rect.y + self.rect.h//2 - 2
        pygame.draw.rect(surf, C['ribbon_sep'], (self.rect.x, ty, self.rect.w, 4), border_radius=2)
        pct = 0 if self.max_val == 0 else min(1.0, max(0.0, self.val / self.max_val))
        tx = self.rect.x + int(pct * self.rect.w)
        
        col = C['txt_dim'] if self.disabled else (217, 119, 6)
        pygame.draw.circle(surf, col, (tx, ty+2), 8)
        if not self.disabled:
            pygame.draw.circle(surf, (0,0,0,60), (tx, ty+4), 8)
            pygame.draw.circle(surf, col, (tx, ty+2), 8)
            pygame.draw.circle(surf, (0, 0, 0), (tx, ty+2), 2.5)

    def handle_mouse(self, mx, my, ev_type):
        if self.disabled: return False
        ty = self.rect.y + self.rect.h//2
        pct = 0 if self.max_val == 0 else self.val / self.max_val
        tx = self.rect.x + int(pct * self.rect.w)
        if ev_type == 'down':
            if math.hypot(mx - tx, my - ty) < 14 or self.rect.collidepoint(mx, my):
                self.dragging = True; self._update_val(mx); return True
        elif ev_type == 'up': self.dragging = False
        elif ev_type == 'move' and self.dragging: self._update_val(mx); return True
        return False
        
    def _update_val(self, mx):
        dx = mx - self.rect.x
        pct = max(0.0, min(1.0, dx / self.rect.w))
        self.val = pct * self.max_val


class Ribbon:
    def __init__(self, W):
        self.W = W
        self.btns = {}
        
        if not pygame.freetype.was_init(): pygame.freetype.init()
        fb = get_font(18, bold=True) 
        t_surf = fb.render('Map Pathfinding', True, (0,0,0))
        title_w = t_surf.get_width()
        base_x = 65 + title_w + 25 
        
        self.sep_x = base_x - 12
        x = base_x
        y = 6; h = 56
        
        self.btns['gen']   = RibbonButton(x, y, 60, h, 'generate', 'Generate', (37, 99, 235))
        x += 60 + 6
        self.btns['acak']  = RibbonButton(x, y, 48, h, 'acak', 'Acak', (37, 99, 235))
        x += 48 + 6
        self.btns['graph'] = RibbonButton(x, y, 48, h, 'graph', 'Graph', C['txt_dark'])
        x += 48 + 12
        self.g1_end = x
        x += 12
        
        self.btns['start'] = RibbonButton(x, y, 56, h, 'start', 'Set Start', (34, 197, 94))
        x += 56 + 6
        self.btns['end']   = RibbonButton(x, y, 56, h, 'end', 'Set End', (239, 68, 68))
        x += 56 + 12
        self.g2_end = x
        x += 12
        
        self.btns['play']  = RibbonButton(x, y, 48, h, 'play', 'Mulai', (217, 119, 6))
        x += 48 + 8
        self.btn_prev = MiniButton(x, y + 14, 24, 28, 'prev')
        x += 24 + 6
        self.slider = Slider(x, y + 14, 100, 28)
        x += 100 + 6
        self.btn_next = MiniButton(x, y + 14, 24, 28, 'next')
        x += 24 + 8
        self.btns['reset'] = RibbonButton(x, y, 48, h, 'reset', 'Reset', C['txt_dark'])
        x += 48 + 14
        self.g3_end = x

        self.stats_x = x + 10
        self.stats = {
            'Node Jalur': ('0', C['stat_blue']),
            'Edge Jalur': ('0', C['stat_purp']),
            'Jarak Rute': ('—', C['stat_teal']),
            'Waktu Cari': ('—', C['stat_amber']),
            'Dikunjungi': ('0', C['stat_rose']),
        }
        self.set_disabled(True)

    def set_disabled(self, v):
        for k in ['acak', 'start', 'end', 'play', 'reset', 'graph']: self.btns[k].disabled = v

    def draw(self, surf):
        pygame.draw.rect(surf, C['ribbon_bg'], (0, 0, self.W, RIBBON_H))
        pygame.draw.line(surf, C['ribbon_sep'], (0, RIBBON_H-1), (self.W, RIBBON_H-1))

        # Logo Kiri
        lx, ly = 25, 34
        pygame.draw.polygon(surf, (37, 99, 235), [(lx, ly-6), (lx+8, ly-8), (lx+8, ly+6), (lx, ly+8)])
        pygame.draw.polygon(surf, (96, 165, 250), [(lx+8, ly-8), (lx+16, ly-6), (lx+16, ly+8), (lx+8, ly+6)])
        pygame.draw.polygon(surf, (37, 99, 235), [(lx+16, ly-6), (lx+24, ly-8), (lx+24, ly+6), (lx+16, ly+8)])
        pygame.draw.circle(surf, (255, 255, 255), (lx+5, ly-1), 2)
        pygame.draw.circle(surf, (255, 255, 255), (lx+19, ly+1), 2)
        pygame.draw.line(surf, (255, 255, 255), (lx+5, ly-1), (lx+19, ly+1), 1)

        fb = get_font(18, bold=True); fs = get_font(11, bold=False)
        t1 = fb.render('Map Pathfinding', True, (29, 78, 216)); t2 = fs.render('A* Algorithm Visualizer', True, C['txt_dim'])
        surf.blit(t1, (65, 20)); surf.blit(t2, (65, 20 + t1.get_height() + 4))
        
        pygame.draw.line(surf, C['ribbon_sep'], (self.sep_x, 10), (self.sep_x, RIBBON_H-25))

        for b in self.btns.values(): b.draw(surf)
        self.btn_prev.draw(surf); self.slider.draw(surf); self.btn_next.draw(surf)
        
        fl = get_font(9, bold=True)
        def draw_gl(text, start_x, end_x):
            pygame.draw.line(surf, (240,242,244), (start_x+4, RIBBON_H-22), (end_x-4, RIBBON_H-22))
            t = fl.render(text.upper(), True, C['txt_label'])
            surf.blit(t, (start_x + (end_x-start_x)//2 - t.get_width()//2, RIBBON_H - 18))
            pygame.draw.line(surf, C['ribbon_sep'], (end_x, 10), (end_x, RIBBON_H-25))
            
        draw_gl("Peta", self.sep_x, self.g1_end)
        draw_gl("Titik Target", self.g1_end, self.g2_end)
        draw_gl("Animasi & Kontrol", self.g2_end, self.g3_end)
        
        ts = fl.render("LANGKAH PER LANGKAH", True, C['txt_label'])
        surf.blit(ts, (self.slider.rect.x + self.slider.rect.w//2 - ts.get_width()//2, RIBBON_H - 38))

        fl_stat = get_font(10, bold=True); fv_stat = get_font(20, bold=True)
        sx = self.stats_x
        for lbl, (val, col) in self.stats.items():
            tl = fl_stat.render(lbl.upper(), True, C['txt_label']); tv = fv_stat.render(str(val), True, col)
            surf.blit(tl, (sx, 18)); surf.blit(tv, (sx, 35))
            sx += max(tl.get_width(), tv.get_width()) + 14 
            pygame.draw.line(surf, (240,242,244), (sx - 7, 15), (sx - 7, RIBBON_H - 25))

    def update(self, mx, my):
        for b in self.btns.values(): b.hov = b.rect.collidepoint(mx, my) and not b.disabled
        self.btn_prev.hov = self.btn_prev.rect.collidepoint(mx, my) and not self.btn_prev.disabled
        self.btn_next.hov = self.btn_next.rect.collidepoint(mx, my) and not self.btn_next.disabled

    def check_click(self, mx, my):
        for k, b in self.btns.items():
            if b.hov: return k
        if self.btn_prev.hov: return 'prev'
        if self.btn_next.hov: return 'next'
        return None

    def set_stat(self, key, val, col=None):
        old_col = self.stats[key][1]
        self.stats[key] = (val, col or old_col)


class ZoomControls:
    def __init__(self, W, H):
        self.w = 42; self.h = 104
        self.x = W - self.w - 35; self.y = H - self.h - 35 
        self.btn_in  = pygame.Rect(self.x, self.y, self.w, 35)
        self.btn_pct = pygame.Rect(self.x, self.y+35, self.w, 34)
        self.btn_out = pygame.Rect(self.x, self.y+69, self.w, 35)

    def draw(self, surf, zoom):
        bg = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (255, 255, 255, 240), (0, 0, self.w, self.h), border_radius=21)
        pygame.draw.rect(bg, C['ribbon_sep'], (0, 0, self.w, self.h), 1, border_radius=21)
        surf.blit(bg, (self.x, self.y))
        pygame.draw.line(surf, C['ribbon_sep'], (self.x+10, self.y+34), (self.x+self.w-10, self.y+34))
        pygame.draw.line(surf, C['ribbon_sep'], (self.x+10, self.y+69), (self.x+self.w-10, self.y+69))
        f_icon = get_font(20, bold=True)
        t_in = f_icon.render('+', True, C['txt_dark'])
        surf.blit(t_in, (self.btn_in.x + self.w//2 - t_in.get_width()//2, self.btn_in.y + 17 - t_in.get_height()//2 - 2))
        t_out = f_icon.render('-', True, C['txt_dark'])
        surf.blit(t_out, (self.btn_out.x + self.w//2 - t_out.get_width()//2, self.btn_out.y + 17 - t_out.get_height()//2 - 2))
        f_pct = get_font(10, bold=True)
        t_pct = f_pct.render(f'{int(zoom*100)}%', True, C['txt_dim'])
        surf.blit(t_pct, (self.btn_pct.x + self.w//2 - t_pct.get_width()//2, self.btn_pct.y + 17 - t_pct.get_height()//2))

    def click(self, mx, my):
        if self.btn_in.collidepoint(mx, my):  return 'in'
        if self.btn_out.collidepoint(mx, my): return 'out'
        return None