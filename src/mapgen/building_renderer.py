import pygame
from config import C, RIBBON_H

class BuildingRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def draw_building(self, b):
        sc  = self.cam.zoom * b['scale']
        if sc < 0.055: return
        sx, sy = self._ws(b['x'], b['y'])
        margin = max(int(200 * sc), 100)
        if sx < -margin or sx > self.W + margin: return
        if sy < RIBBON_H - margin or sy > self.H + RIBBON_H + margin: return

        tp = b['type']; col = b['color']; scr = self.screen
        def dwin(ox, oy, w, h):
            px = sx + ox * sc; py = sy + oy * sc
            pw = max(2, w * sc); ph = max(2, h * sc)
            if pw < 2 or ph < 2: return
            pygame.draw.rect(scr, C['win_dark'], (px, py, pw, ph))
            kw = max(1, pw - 2); kh = max(1, ph - 2)
            pygame.draw.rect(scr, C['win_light'], (px+1, py+1, kw, kh))
            if kw > 2 and kh > 2: pygame.draw.line(scr, (220, 240, 255), (px+1, py+ph-2), (px+pw-2, py+1), 1)

        shw_w = max(2, int(160 * sc)); shw_h = max(2, int(40 * sc))
        shw = pygame.Surface((shw_w, shw_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shw, (0, 0, 0, 38), (0, 0, shw_w, shw_h)); scr.blit(shw, (sx - shw_w//2, sy - shw_h//2))

        if tp == 'tree':
            tw = max(2, int(10 * sc)); th = max(2, int(25 * sc))
            pygame.draw.rect(scr, C['tree_trunk'], (sx - tw//2, sy - th, tw, th))
            r1 = max(3, int(30 * sc)); r2 = max(2, int(18 * sc))
            pygame.draw.circle(scr, C['tree_top'], (sx, sy - int(35 * sc)), r1)
            pygame.draw.circle(scr, (130, 224, 170), (sx - int(6 * sc), sy - int(40 * sc)), r2)
            
        elif tp == 't1':
            w = 150; h = 80; bw = max(2, int(w * sc)); bh = max(2, int(h * 0.7 * sc))
            pygame.draw.rect(scr, C['brick'], (sx - bw//2, sy - bh, bw, bh))
            for i in range(2):
                dwin(-w/2+10, -h*0.6+i*30, 16, 16); dwin(-w/2+32, -h*0.6+i*30, 16, 16)
                dwin(w/2-26, -h*0.6+i*30, 16, 16); dwin(w/2-48, -h*0.6+i*30, 16, 16)
            mw = max(2, int(70 * sc)); mh = max(2, int(h * sc))
            pygame.draw.rect(scr, (169, 50, 38), (sx - int(35 * sc), sy - mh, mw, mh))
            dw = max(2, int(50 * sc)); dh = max(2, int(h * 0.3 * sc))
            pygame.draw.rect(scr, C['conc'], (sx - int(25 * sc), sy - dh, dw, dh))
            dw2 = max(2, int(20 * sc)); dh2 = max(2, int(h * 0.25 * sc))
            pygame.draw.rect(scr, (92, 42, 22), (sx - int(10 * sc), sy - dh2, dw2, dh2))
            dwin(-18, -h*0.7, 14, 14); dwin(4, -h*0.7, 14, 14)
            roof1 = [(sx - int(40*sc), sy - mh), (sx, sy - mh - int(35*sc)), (sx + int(40*sc), sy - mh)]
            pygame.draw.polygon(scr, C['conc'], roof1)
            roof2 = [(sx - int(30*sc), sy - mh), (sx, sy - mh - int(28*sc)), (sx + int(30*sc), sy - mh)]
            pygame.draw.polygon(scr, C['roof'], roof2)
            
        elif tp == 't2':
            w = 100; h = 120; bw = max(2, int(w * sc)); bh = max(2, int(h * sc)); bx = sx - bw//2; by = sy - bh
            pygame.draw.rect(scr, col, (bx, by, bw, bh))
            for i in range(1, 4):
                fy = by + int((i*30 - 4)*sc); fh = max(1, int(4*sc))
                dc = (max(0, col[0]-20), max(0, col[1]-20), max(0, col[2]-20))
                pygame.draw.rect(scr, dc, (bx, fy, bw, fh))
            ew = max(2, int(30 * sc)); eh = max(2, int(25 * sc))
            pygame.draw.rect(scr, (44, 62, 80), (sx - int(15 * sc), sy - eh, ew, eh))
            for r in range(3):
                for c in range(3):
                    if r == 2 and c == 1: continue
                    dwin(-w/2+10+c*30, -h+10+r*35, 18, 18)
            pw = bw + int(10 * sc); ph = max(1, int(8 * sc))
            pygame.draw.rect(scr, (127, 140, 141), (bx - int(5*sc), by - int(8*sc), pw, ph))
            
        elif tp == 't3':
            w = 80; h = 150; bw = max(2, int(w * sc)); bh = max(2, int(h * sc)); bx = sx - bw//2; by = sy - bh
            pygame.draw.rect(scr, (205, 211, 216), (bx, by, bw, bh))
            gw = max(1, bw - int(12 * sc)); gh = max(1, bh - int(12 * sc)); gx = bx + int(6 * sc); gy = by + int(6 * sc)
            if gw > 2 and gh > 2:
                pygame.draw.rect(scr, (93, 173, 226), (gx, gy, gw, gh))
                if sc > 0.15:
                    for i in range(1, 3):
                        lx = gx + int(i * gw / 3); pygame.draw.line(scr, (41, 128, 185), (lx, gy), (lx, gy + gh), max(1, int(1.5*sc)))
                    for i in range(1, 8):
                        ly = gy + int(i * gh / 8); pygame.draw.line(scr, (41, 128, 185), (gx, ly), (gx + gw, ly), max(1, int(1.5*sc)))
            ew = max(2, int(24 * sc)); eh = max(2, int(25 * sc))
            pygame.draw.rect(scr, (44, 62, 80), (sx - int(12 * sc), sy - eh, ew, eh))