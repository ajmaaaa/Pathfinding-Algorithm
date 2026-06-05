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
