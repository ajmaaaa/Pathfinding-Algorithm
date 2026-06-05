import pygame
import math
from config import C, RIBBON_H
from src.ui.hud import get_font

def draw_vector_icon(surf, name, cx, cy, color):
    if name == 'generate':
        pygame.draw.arc(surf, color, (cx-8, cy-8, 16, 16), math.radians(40), math.radians(320), 2)
        pygame.draw.polygon(surf, color, [(cx+5, cy-4), (cx+10, cy-1), (cx+5, cy+3)])
    elif name == 'acak':
        pygame.draw.polygon(surf, color, [(cx, cy-6), (cx+7, cy-3), (cx, cy), (cx-7, cy-3)], 1)
        pygame.draw.polygon(surf, color, [(cx-7, cy-3), (cx, cy), (cx, cy+6), (cx-7, cy+3)], 1)
        pygame.draw.polygon(surf, color, [(cx, cy), (cx+7, cy-3), (cx+7, cy+3), (cx, cy+6)], 1)
        pygame.draw.circle(surf, color, (int(cx), int(cy-3)), 1.5)
    elif name == 'graph':
        n1 = (cx - 6, cy + 4)
        n2 = (cx + 6, cy + 4)
        n3 = (cx, cy - 6)
        pygame.draw.line(surf, color, n1, n2, 1)
        pygame.draw.line(surf, color, n1, n3, 1)
        pygame.draw.line(surf, color, n2, n3, 1)
        pygame.draw.circle(surf, color, n1, 3)
        pygame.draw.circle(surf, color, n2, 3)
        pygame.draw.circle(surf, color, n3, 3)
        pygame.draw.circle(surf, (255, 255, 255), n1, 1)
        pygame.draw.circle(surf, (255, 255, 255), n2, 1)
        pygame.draw.circle(surf, (255, 255, 255), n3, 1)
    elif name == 'start':
        pygame.draw.circle(surf, color, (cx, cy), 8, 2)
        pygame.draw.circle(surf, color, (cx, cy), 3)
    elif name == 'end':
        pygame.draw.circle(surf, color, (cx, cy), 8, 2)
        pygame.draw.circle(surf, color, (cx, cy), 3)
    elif name == 'play':
        pygame.draw.polygon(surf, color, [(cx-4, cy-7), (cx+8, cy), (cx-4, cy+7)])
    elif name == 'pause':
        pygame.draw.rect(surf, color, (cx-5, cy-7, 3, 14), border_radius=1)
        pygame.draw.rect(surf, color, (cx+2, cy-7, 3, 14), border_radius=1)
    elif name == 'reset':
        pygame.draw.arc(surf, color, (cx-8, cy-8, 16, 16), math.radians(135), math.radians(45), 2)
        pygame.draw.polygon(surf, color, [(cx-5, cy-3), (cx-10, cy-6), (cx-4, cy-9)])
    elif name == 'prev':
        pygame.draw.line(surf, color, (cx+3, cy-6), (cx-3, cy), 2)
        pygame.draw.line(surf, color, (cx-3, cy), (cx+3, cy+6), 2)
    elif name == 'next':
        pygame.draw.line(surf, color, (cx-3, cy-6), (cx+3, cy), 2)
        pygame.draw.line(surf, color, (cx+3, cy), (cx-3, cy+6), 2)
    elif name == 'edit':
        pygame.draw.line(surf, color, (cx-6, cy+6), (cx+3, cy-3), 2)
        pygame.draw.polygon(surf, color, [(cx-6, cy+6), (cx-8, cy+8), (cx-5, cy+8)])
        pygame.draw.circle(surf, color, (cx+5, cy-5), 2)


class RibbonButton:
    def __init__(self, x, y, w, h, icon, label, accent=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.icon_name = icon     
        self.label = label
        self.accent = accent
        self.hov = False; self.active = False; self.disabled = False

    def draw(self, surf, theme='dark'):
        r = 12
        if self.disabled:
            if theme == 'dark':
                bg, brd, txt_col, ico_col = (30, 41, 59), (51, 65, 85), (100, 116, 139), (100, 116, 139)
            else:
                bg, brd, txt_col, ico_col = (248, 250, 252), (241, 245, 249), (203, 213, 225), (203, 213, 225)
        else:
            if self.icon_name == 'start':
                if self.active:
                    bg, brd, txt_col, ico_col = ((20, 83, 45), (34, 197, 94), (240, 253, 244), (74, 222, 128)) if theme == 'dark' else ((220, 252, 231), (134, 239, 172), (21, 128, 61), (22, 163, 74))
                elif self.hov:
                    bg, brd, txt_col, ico_col = ((22, 101, 52), (34, 139, 74), (220, 252, 231), (74, 222, 128)) if theme == 'dark' else ((240, 253, 244), (187, 247, 208), (22, 101, 52), (22, 163, 74))
                else:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (51, 65, 85), (241, 245, 249), (74, 222, 128)) if theme == 'dark' else ((255, 255, 255), (226, 232, 240), (51, 65, 85), (22, 163, 74))
            elif self.icon_name == 'end':
                if self.active:
                    bg, brd, txt_col, ico_col = ((127, 29, 29), (239, 68, 68), (254, 242, 242), (248, 113, 113)) if theme == 'dark' else ((254, 226, 226), (252, 165, 165), (185, 28, 28), (220, 38, 38))
                elif self.hov:
                    bg, brd, txt_col, ico_col = ((153, 27, 27), (185, 28, 28), (254, 226, 226), (248, 113, 113)) if theme == 'dark' else ((254, 242, 242), (254, 202, 202), (153, 27, 27), (220, 38, 38))
                else:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (51, 65, 85), (241, 245, 249), (248, 113, 113)) if theme == 'dark' else ((255, 255, 255), (226, 232, 240), (51, 65, 85), (220, 38, 38))
            elif self.icon_name in ('play', 'pause'):
                if self.active:
                    bg, brd, txt_col, ico_col = ((120, 53, 4), (217, 119, 6), (254, 243, 199), (251, 191, 36)) if theme == 'dark' else ((254, 243, 199), (252, 211, 77), (180, 83, 9), (217, 119, 6))
                elif self.hov:
                    bg, brd, txt_col, ico_col = ((146, 64, 14), (217, 119, 6), (255, 251, 235), (251, 191, 36)) if theme == 'dark' else ((255, 251, 235), (253, 230, 138), (146, 64, 14), (217, 119, 6))
                else:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (51, 65, 85), (241, 245, 249), (251, 191, 36)) if theme == 'dark' else ((255, 255, 255), (226, 232, 240), (51, 65, 85), (217, 119, 6))
            elif self.accent == (37, 99, 235):
                if self.active:
                    bg, brd, txt_col, ico_col = ((30, 58, 138), (59, 130, 246), (239, 246, 255), (96, 165, 250)) if theme == 'dark' else ((219, 234, 254), (147, 197, 253), (29, 78, 216), (37, 99, 235))
                elif self.hov:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (59, 130, 246), (241, 245, 249), (96, 165, 250)) if theme == 'dark' else ((239, 246, 255), (191, 219, 254), (30, 64, 175), (37, 99, 235))
                else:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (51, 65, 85), (241, 245, 249), (96, 165, 250)) if theme == 'dark' else ((255, 255, 255), (226, 232, 240), (51, 65, 85), (37, 99, 235))
            else:
                if self.active:
                    bg, brd, txt_col, ico_col = ((15, 23, 42), (30, 41, 59), (241, 245, 249), (148, 163, 184)) if theme == 'dark' else ((226, 232, 240), (203, 213, 225), (30, 41, 59), (71, 85, 105))
                elif self.hov:
                    bg, brd, txt_col, ico_col = ((51, 65, 85), (71, 85, 105), (255, 255, 255), (226, 232, 240)) if theme == 'dark' else ((241, 245, 249), (226, 232, 240), (51, 65, 85), (71, 85, 105))
                else:
                    bg, brd, txt_col, ico_col = ((30, 41, 59), (51, 65, 85), (226, 232, 240), (148, 163, 184)) if theme == 'dark' else ((255, 255, 255), (241, 245, 249), (71, 85, 105), (100, 116, 139))

        if not self.disabled and (self.hov or self.active):
            glow_color = (*ico_col, 20)
            glow_surf = pygame.Surface((self.rect.w + 6, self.rect.h + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_color, (0, 0, self.rect.w + 6, self.rect.h + 6), border_radius=r + 3)
            surf.blit(glow_surf, (self.rect.x - 3, self.rect.y - 3))

        pygame.draw.rect(surf, bg, self.rect, border_radius=r)
        pygame.draw.rect(surf, brd, self.rect, 1, border_radius=r)

        fl = get_font(10, bold=True)
        tl = fl.render(self.label, True, txt_col)
        cx = self.rect.x + self.rect.w // 2
        total_h = 24 + 4 + tl.get_height()
        sy = self.rect.y + (self.rect.h - total_h) // 2

        draw_vector_icon(surf, self.icon_name, cx, sy + 11, ico_col)
        surf.blit(tl, (cx - tl.get_width()//2, sy + 24 + 2))


class MiniButton:
    def __init__(self, x, y, w, h, icon):
        self.rect = pygame.Rect(x, y, w, h)
        self.icon_name = icon
        self.hov = False; self.disabled = False

    def draw(self, surf, theme='dark'):
        r = 10
        if self.disabled:
            if theme == 'dark':
                bg, brd, txt = (30, 41, 59), (51, 65, 85), (100, 116, 139)
            else:
                bg, brd, txt = (248, 250, 252), (241, 245, 249), (203, 213, 225)
        elif self.hov:
            if theme == 'dark':
                bg, brd, txt = (51, 65, 85), (71, 85, 105), (96, 165, 250)
            else:
                bg, brd, txt = (239, 246, 255), (191, 219, 254), (37, 99, 235)
        else:
            if theme == 'dark':
                bg, brd, txt = (30, 41, 59), (51, 65, 85), (148, 163, 184)
            else:
                bg, brd, txt = (255, 255, 255), (241, 245, 249), (71, 85, 105)

        pygame.draw.rect(surf, bg, self.rect, border_radius=r)
        pygame.draw.rect(surf, brd, self.rect, 1, border_radius=r)

        cx = self.rect.x + self.rect.w // 2; cy = self.rect.y + self.rect.h // 2
        draw_vector_icon(surf, self.icon_name, cx, cy, txt)

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
        self.visible = True
        self.toggle_hov = False
        
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

    def get_toggle_rect(self):
        h = RIBBON_H if self.visible else 0
        return pygame.Rect(self.W - 120, h, 100, 20)

    def draw(self, surf, theme='dark'):
        if theme == 'dark':
            bg_color = (15, 23, 42)        # Slate 900
            sep_color = (30, 41, 59)       # Slate 800
            shadow_color = (0, 0, 0)
            brand_text = (241, 245, 249)
            brand_subtext = (148, 163, 184)
            divider_col = (30, 41, 59)
            tab_bg = (30, 41, 59)
            tab_border = (51, 65, 85)
            tab_text = (148, 163, 184)
            tab_text_hov = (96, 165, 250)
        else:
            bg_color = (252, 253, 255)      
            sep_color = (226, 232, 240)    
            shadow_color = (0, 0, 0)
            brand_text = (15, 23, 42)
            brand_subtext = (100, 116, 139)
            divider_col = (241, 245, 249)
            tab_bg = (255, 255, 255)
            tab_border = (226, 232, 240)
            tab_text = (100, 116, 139)
            tab_text_hov = (37, 99, 235)

        if not self.visible:
            # Draw expand floating tab at top right of screen
            toggle_r = self.get_toggle_rect()
            for i in range(3):
                sh_surf = pygame.Surface((toggle_r.w + i*2, toggle_r.h + i), pygame.SRCALPHA)
                pygame.draw.rect(sh_surf, (0, 0, 0, 6 - i*2), (0, 0, toggle_r.w + i*2, toggle_r.h + i), border_bottom_left_radius=10, border_bottom_right_radius=10)
                surf.blit(sh_surf, (toggle_r.x - i, toggle_r.y))
                
            tab_color = tab_bg
            if self.toggle_hov:
                tab_color = (51, 65, 85) if theme == 'dark' else (241, 245, 249)
                
            pygame.draw.rect(surf, tab_color, toggle_r, border_bottom_left_radius=10, border_bottom_right_radius=10)
            pygame.draw.rect(surf, tab_border, toggle_r, 1, border_bottom_left_radius=10, border_bottom_right_radius=10)
            
            f = get_font(9, bold=True)
            txt_col = tab_text_hov if self.toggle_hov else tab_text
            txt = f.render("SHOW MENU ▼", True, txt_col)
            surf.blit(txt, (toggle_r.x + toggle_r.w // 2 - txt.get_width() // 2, toggle_r.y + 5))
            return

        # Draw full Ribbon
        pygame.draw.rect(surf, bg_color, (0, 0, self.W, RIBBON_H))
        
        # Soft drop shadow
        pygame.draw.line(surf, sep_color, (0, RIBBON_H - 1), (self.W, RIBBON_H - 1))
        for sh in range(4):
            shadow_surf = pygame.Surface((self.W, 1), pygame.SRCALPHA)
            shadow_surf.fill((*shadow_color, 8 - sh * 2))
            surf.blit(shadow_surf, (0, RIBBON_H + sh))

        # Premium brand header logo
        lx, ly = 20, 34
        glow_s = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (59, 130, 246, 35) if theme == 'dark' else (59, 130, 246, 20), (22, 22), 22)
        surf.blit(glow_s, (lx - 2, ly - 22))
        
        logo_accent1 = (59, 130, 246) if theme == 'dark' else (37, 99, 235)
        logo_accent2 = (147, 197, 253) if theme == 'dark' else (96, 165, 250)
        
        pygame.draw.polygon(surf, logo_accent1,  [(lx,     ly-7), (lx+9,  ly-9), (lx+9,  ly+7), (lx,    ly+9)])
        pygame.draw.polygon(surf, logo_accent2, [(lx+9,  ly-9), (lx+18, ly-7), (lx+18, ly+9), (lx+9,  ly+7)])
        pygame.draw.polygon(surf, logo_accent1,  [(lx+18, ly-7), (lx+27, ly-9), (lx+27, ly+7), (lx+18, ly+9)])
        pygame.draw.circle(surf, (255, 255, 255), (lx + 5,  ly - 1), 2)
        pygame.draw.circle(surf, (255, 255, 255), (lx + 21, ly + 1), 2)
        pygame.draw.line(surf, (186, 230, 253), (lx + 5, ly - 1), (lx + 21, ly + 1), 1)

        fb = get_font(18, bold=True); fs = get_font(10, bold=False)
        t1 = fb.render('Map Pathfinding', True, brand_text)
        t2 = fs.render('A* Algorithm Visualizer', True, brand_subtext)
        surf.blit(t1, (lx + 32, 18))
        surf.blit(t2, (lx + 32, 18 + t1.get_height() + 3))

        pygame.draw.line(surf, divider_col, (self.sep_x, 8), (self.sep_x, RIBBON_H - 20))

        # Buttons & Controllers
        for b in self.btns.values(): b.draw(surf, theme=theme)
        self.btn_prev.draw(surf, theme=theme)
        self.slider.draw(surf, theme=theme)
        self.btn_next.draw(surf, theme=theme)

        # Labels & Dividers
        fl = get_font(9, bold=True)
        def draw_gl(text, start_x, end_x):
            pygame.draw.line(surf, divider_col, (start_x + 4, RIBBON_H - 18), (end_x - 4, RIBBON_H - 18))
            t = fl.render(text.upper(), True, brand_subtext)
            surf.blit(t, (start_x + (end_x - start_x) // 2 - t.get_width() // 2, RIBBON_H - 15))
            pygame.draw.line(surf, divider_col, (end_x, 8), (end_x, RIBBON_H - 20))

        draw_gl("Peta", self.sep_x, self.g1_end)
        draw_gl("Titik Target", self.g1_end, self.g2_end)
        draw_gl("Animasi & Kontrol", self.g2_end, self.g3_end)

        ts = fl.render("LANGKAH PER LANGKAH", True, brand_subtext)
        surf.blit(ts, (self.slider.rect.x + self.slider.rect.w // 2 - ts.get_width() // 2, RIBBON_H - 38))

        # Statistics badges
        fl_stat = get_font(9, bold=True); fv_stat = get_font(19, bold=True)
        
        if theme == 'dark':
            stat_colors = {
                'Node Jalur': {
                    'bg': (30, 41, 59),
                    'border': (59, 130, 246, 100),
                    'label': (148, 163, 184),
                    'value': (96, 165, 250)
                },
                'Edge Jalur': {
                    'bg': (30, 41, 59),
                    'border': (139, 92, 246, 100),
                    'label': (148, 163, 184),
                    'value': (167, 139, 250)
                },
                'Jarak Rute': {
                    'bg': (30, 41, 59),
                    'border': (16, 185, 129, 100),
                    'label': (148, 163, 184),
                    'value': (52, 211, 153)
                },
                'Waktu Cari': {
                    'bg': (30, 41, 59),
                    'border': (245, 158, 11, 100),
                    'label': (148, 163, 184),
                    'value': (251, 191, 36)
                },
                'Dikunjungi': {
                    'bg': (30, 41, 59),
                    'border': (244, 63, 94, 100),
                    'label': (148, 163, 184),
                    'value': (251, 113, 133)
                }
            }
        else:
            stat_colors = {
                'Node Jalur': {
                    'bg': (239, 246, 255),
                    'border': (219, 234, 254),
                    'label': (30, 64, 175),
                    'value': (29, 78, 216)
                },
                'Edge Jalur': {
                    'bg': (245, 243, 255),
                    'border': (237, 233, 254),
                    'label': (91, 33, 182),
                    'value': (109, 40, 217)
                },
                'Jarak Rute': {
                    'bg': (236, 253, 245),
                    'border': (209, 250, 229),
                    'label': (6, 95, 70),
                    'value': (4, 120, 87)
                },
                'Waktu Cari': {
                    'bg': (255, 251, 235),
                    'border': (254, 243, 199),
                    'label': (146, 64, 14),
                    'value': (217, 119, 6)
                },
                'Dikunjungi': {
                    'bg': (255, 241, 242),
                    'border': (255, 228, 230),
                    'label': (159, 18, 57),
                    'value': (225, 29, 72)
                }
            }

        sx = self.stats_x
        for lbl, (val, _) in self.stats.items():
            colors = stat_colors.get(lbl, stat_colors['Node Jalur'])
            tl = fl_stat.render(lbl.upper(), True, colors['label'])
            tv = fv_stat.render(str(val), True, colors['value'])
            chip_w = max(tl.get_width(), tv.get_width()) + 20
            chip_h = RIBBON_H - 20
            
            chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
            bg_c = colors['bg']
            if len(bg_c) == 3:
                bg_c = (*bg_c, 240)
            brd_c = colors['border']
            if len(brd_c) == 3:
                brd_c = (*brd_c, 255)
                
            pygame.draw.rect(chip_surf, bg_c, (0, 0, chip_w, chip_h), border_radius=12)
            pygame.draw.rect(chip_surf, brd_c, (0, 0, chip_w, chip_h), 1, border_radius=12)
            
            if val != '—' and val != '0':
                shadow_surf = pygame.Surface((chip_w + 4, chip_h + 4), pygame.SRCALPHA)
                glow_val_col = colors['value']
                pygame.draw.rect(shadow_surf, (*glow_val_col, 15), (0, 0, chip_w + 4, chip_h + 4), border_radius=14)
                surf.blit(shadow_surf, (sx - 2, 6))

            surf.blit(chip_surf, (sx, 8))
            surf.blit(tl, (sx + (chip_w - tl.get_width()) // 2, 16))
            surf.blit(tv, (sx + (chip_w - tv.get_width()) // 2, 34))
            sx += chip_w + 8

        # Collapse/Expand floating tab at bottom of Ribbon (now at the right)
        toggle_r = self.get_toggle_rect()
        for i in range(3):
            sh_surf = pygame.Surface((toggle_r.w + i*2, toggle_r.h + i), pygame.SRCALPHA)
            pygame.draw.rect(sh_surf, (0, 0, 0, 6 - i*2), (0, 0, toggle_r.w + i*2, toggle_r.h + i), border_bottom_left_radius=10, border_bottom_right_radius=10)
            surf.blit(sh_surf, (toggle_r.x - i, toggle_r.y))
            
        tab_color = tab_bg
        if self.toggle_hov:
            tab_color = (51, 65, 85) if theme == 'dark' else (241, 245, 249)
            
        pygame.draw.rect(surf, tab_color, toggle_r, border_bottom_left_radius=10, border_bottom_right_radius=10)
        pygame.draw.rect(surf, tab_border, toggle_r, 1, border_bottom_left_radius=10, border_bottom_right_radius=10)
        
        f = get_font(9, bold=True)
        txt_col = tab_text_hov if self.toggle_hov else tab_text
        txt = f.render("HIDE MENU ▲", True, txt_col)
        surf.blit(txt, (toggle_r.x + toggle_r.w // 2 - txt.get_width() // 2, toggle_r.y + 4))

    def update(self, mx, my):
        toggle_r = self.get_toggle_rect()
        self.toggle_hov = toggle_r.collidepoint(mx, my)
        if not self.visible:
            return
        for b in self.btns.values(): b.hov = b.rect.collidepoint(mx, my) and not b.disabled
        self.btn_prev.hov = self.btn_prev.rect.collidepoint(mx, my) and not self.btn_prev.disabled
        self.btn_next.hov = self.btn_next.rect.collidepoint(mx, my) and not self.btn_next.disabled

    def check_click(self, mx, my):
        if not self.visible:
            return None
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

    def draw(self, surf, zoom, theme='dark'):
        bg_col = (30, 41, 59, 245) if theme == 'dark' else (255, 255, 255, 245)
        border_col = (51, 65, 85, 255) if theme == 'dark' else (226, 232, 240, 255)
        text_col = (96, 165, 250) if theme == 'dark' else (37, 99, 235)
        pct_col = (148, 163, 184) if theme == 'dark' else (100, 116, 139)
        sep_col = (51, 65, 85) if theme == 'dark' else (226, 232, 240)
        
        bg = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(bg, bg_col, (0, 0, self.w, self.h), border_radius=14)
        pygame.draw.rect(bg, border_col, (0, 0, self.w, self.h), 1, border_radius=14)
        surf.blit(bg, (self.x, self.y))
        
        pygame.draw.line(surf, sep_col, (self.x + 8, self.y + 35), (self.x + self.w - 8, self.y + 35))
        pygame.draw.line(surf, sep_col, (self.x + 8, self.y + 69), (self.x + self.w - 8, self.y + 69))
        
        f_icon = get_font(20, bold=True)
        t_in  = f_icon.render('+', True, text_col)
        surf.blit(t_in,  (self.btn_in.x  + self.w // 2 - t_in.get_width()  // 2, self.btn_in.y  + 17 - t_in.get_height()  // 2 - 2))
        t_out = f_icon.render('−', True, text_col)
        surf.blit(t_out, (self.btn_out.x + self.w // 2 - t_out.get_width() // 2, self.btn_out.y + 17 - t_out.get_height() // 2 - 2))
        
        f_pct = get_font(10, bold=True)
        t_pct = f_pct.render(f'{int(zoom*100)}%', True, pct_col)
        surf.blit(t_pct, (self.btn_pct.x + self.w // 2 - t_pct.get_width() // 2, self.btn_pct.y + 17 - t_pct.get_height() // 2))

    def click(self, mx, my):
        if self.btn_in.collidepoint(mx, my):  return 'in'
        if self.btn_out.collidepoint(mx, my): return 'out'
        return None