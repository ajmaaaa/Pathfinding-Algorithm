import pygame
import math
from config import C, RIBBON_H, RW
from src.core.geometry import get_smooth_path_coord

class DynamicRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self.car_angle = 0.0
        self.car_last_prog = 0.0

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def draw_car(self, x, y, angle):
        sc = self.cam.zoom
        if sc < 0.08: return
        sx, sy = self._ws(x, y)
        length = RW * 1.3 * sc
        width = RW * 0.7 * sc
        cos_a = math.cos(angle); sin_a = math.sin(angle)

        def get_pt(ox, oy, off_x=0, off_y=0): 
            px = sx + ox * cos_a - oy * sin_a + off_x
            py = sy + ox * sin_a + oy * cos_a + off_y
            return (px, py)

        hl, hw = length / 2, width / 2

        sh_off = max(1, 3 * sc)
        sh_pts = [get_pt(hl, hw, sh_off, sh_off), 
                  get_pt(hl, -hw, sh_off, sh_off), 
                  get_pt(-hl, -hw, sh_off, sh_off), 
                  get_pt(-hl, hw, sh_off, sh_off)]
        pygame.draw.polygon(self.screen, (0, 0, 0, 80), sh_pts) 

        pts = [get_pt(hl, hw), get_pt(hl, -hw), get_pt(-hl, -hw), get_pt(-hl, hw)]
        pygame.draw.polygon(self.screen, (225, 29, 72), pts) 

        roof_pts = [get_pt(hl*0.3, hw*0.7), get_pt(hl*0.3, -hw*0.7), get_pt(-hl*0.5, -hw*0.7), get_pt(-hl*0.5, hw*0.7)]
        pygame.draw.polygon(self.screen, (159, 18, 57), roof_pts)
        
        ws_pts = [get_pt(hl*0.4, hw*0.6), get_pt(hl*0.4, -hw*0.6), get_pt(hl*0.2, -hw*0.6), get_pt(hl*0.2, hw*0.6)]
        pygame.draw.polygon(self.screen, (186, 230, 253), ws_pts)
        
        rad = max(1.5, 2.5*sc)
        h1 = get_pt(hl, hw*0.6); h2 = get_pt(hl, -hw*0.6)
        pygame.draw.circle(self.screen, (253, 224, 71), (int(h1[0]), int(h1[1])), int(rad))
        pygame.draw.circle(self.screen, (253, 224, 71), (int(h2[0]), int(h2[1])), int(rad))

    def get_car_transform(self, path_edges, progress):
        if not path_edges or progress <= 0:
            self.car_last_prog = 0.0
            return None, None, None
            
        car_x, car_y = get_smooth_path_coord(path_edges, progress)
        nx, ny = get_smooth_path_coord(path_edges, progress + 0.1) 
        
        if car_x is not None and nx is not None:
            target_angle = math.atan2(ny - car_y, nx - car_x)
            if self.car_last_prog == 0.0: 
                self.car_angle = target_angle 
            else:
                diff = (target_angle - self.car_angle + math.pi) % (math.pi * 2) - math.pi
                self.car_angle += diff * 0.45
                    
        self.car_last_prog = progress
        return car_x, car_y, self.car_angle

    def draw_anim_layer_ground(self, nodes, search_edges, path_edges, progress):
        sc = self.cam.zoom
        ov = pygame.Surface((self.W, self.H + RIBBON_H), pygame.SRCALPHA)
        
        for se in search_edges:
            if progress >= se['start']:
                p = (progress - se['start']) / (se['end'] - se['start'])
                p = max(0, min(1, p))
                cur_x = se['from'].x + (se['to'].x - se['from'].x) * p
                cur_y = se['from'].y + (se['to'].y - se['from'].y) * p
                is_eval = progress >= se['target'].eval_step
                if se['is_optimal']:
                    color = (59, 130, 246, 178) if is_eval else (46, 204, 113, 153)
                    lw = max(2, int(RW * 0.4 * sc))
                else:
                    color = (239, 68, 68, 102); lw = max(1, int(RW * 0.25 * sc))
                
                p1 = self._ws(se['from'].x, se['from'].y); p2 = self._ws(cur_x, cur_y)
                pygame.draw.line(ov, color, p1, p2, lw)
                if p > 0:
                    pygame.draw.circle(ov, color, p1, lw // 2)
                    pygame.draw.circle(ov, color, p2, lw // 2)

        for n in nodes:
            is_eval = n.eval_step <= progress; is_disc = n.disc_step <= progress
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < RIBBON_H or sy > self.H + RIBBON_H: continue
            if is_eval: pygame.draw.circle(ov, (59, 130, 246, 230), (sx, sy), max(2, int(RW*.35*sc)))
            elif is_disc:
                p = (progress - n.disc_step) / 0.5; p = max(0, min(1, p))
                if p > 0: pygame.draw.circle(ov, (46, 204, 113, 230), (sx, sy), max(2, int(RW*.4*p*sc)))

        for pe in path_edges:
            if progress >= pe['start']:
                p = (progress - pe['start']) / (pe['end'] - pe['start'])
                p = max(0, min(1, p))
                cur_x = pe['from'].x + (pe['to'].x - pe['from'].x) * p
                cur_y = pe['from'].y + (pe['to'].y - pe['from'].y) * p
                p1 = self._ws(pe['from'].x, pe['from'].y); p2 = self._ws(cur_x, cur_y)
                
                w1 = max(4, int(RW*.9*sc)); w2 = max(3, int(RW*.55*sc)); w3 = max(2, int(RW*.38*sc))
                
                pygame.draw.line(ov, (251, 191, 36, 64), p1, p2, w1)
                pygame.draw.line(ov, (0, 0, 0, 64), p1, p2, w2)
                pygame.draw.line(self.screen, (246, 173, 85), p1, p2, w3)
                pygame.draw.line(ov, (255, 255, 255, 140), p1, p2, max(1, int(RW*.09*sc)))
                
                if p > 0:
                    pygame.draw.circle(ov, (251, 191, 36, 64), p1, w1 // 2)
                    pygame.draw.circle(ov, (251, 191, 36, 64), p2, w1 // 2)
                    pygame.draw.circle(ov, (0, 0, 0, 64), p1, w2 // 2)
                    pygame.draw.circle(ov, (0, 0, 0, 64), p2, w2 // 2)
                    pygame.draw.circle(self.screen, (246, 173, 85), p1, w3 // 2)
                    pygame.draw.circle(self.screen, (246, 173, 85), p2, w3 // 2)

        self.screen.blit(ov, (0, 0))