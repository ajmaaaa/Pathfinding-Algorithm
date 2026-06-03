import pygame
import math
import time
from config import C, RIBBON_H, RW
from src.core.geometry import get_smooth_path_coord, point_on_polyline

class DynamicRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self.car_angle = 0.0
        self.car_smooth_angle = 0.0
        self.car_target_angle = 0.0
        self.car_last_prog = 0.0
        self.car_last_x = None
        self.car_last_y = None
        self._angle_initialized = False

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)
    
    def _curve_until(self, curve, p):
        if not curve:
            return []
        p = max(0.0, min(1.0, p))
        if p <= 0:
            return [curve[0]]
        if p >= 1.0:
            return curve[:]
            
        total_len = 0.0
        for i in range(1, len(curve)):
            p0 = curve[i - 1]
            p1 = curve[i]
            total_len += math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            
        target = total_len * p
        walked = 0.0
        pts = [curve[0]]
        
        for i in range(1, len(curve)):
            p0 = curve[i - 1]
            p1 = curve[i]
            seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if walked + seg >= target:
                local_t = (target - walked) / max(0.0001, seg)
                end = (
                    p0[0] + (p1[0] - p0[0]) * local_t,
                    p0[1] + (p1[1] - p0[1]) * local_t
                )
                if end != pts[-1]:
                    pts.append(end)
                break
            else:
                if p1 != pts[-1]:
                    pts.append(p1)
                walked += seg
                
        return pts    

 def _draw_curve(self, surface, curve, color, width):
        if len(curve) < 2:
            return
    def _draw_curve(self, surface, curve, color, width):
        if len(curve) < 2: return
        pts = [self._ws(x, y) for x, y in curve]
        w = max(1, int(width))
        r = max(1, w // 2)
        
        min_x = min(p[0] for p in pts) - r - 2
        max_x = max(p[0] for p in pts) + r + 2
        min_y = min(p[1] for p in pts) - r - 2
        max_y = max(p[1] for p in pts) + r + 2
        
        bw = int(max_x - min_x)
        bh = int(max_y - min_y)
        if bw <= 0 or bh <= 0: return
        
        temp = pygame.Surface((bw, bh), pygame.SRCALPHA)
        opaque_color = (color[0], color[1], color[2], 255)
        
        step = max(1.0, r * 0.15)
        walked = 0.0
        
        pygame.draw.circle(temp, opaque_color, (int(pts[0][0] - min_x), int(pts[0][1] - min_y)), r)
        
        for i in range(1, len(pts)):
            p0 = pts[i-1]
            p1 = pts[i]
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            dist = math.hypot(dx, dy)
            if dist == 0: continue
            used = 0.0
            while used < dist:
                take = min(step - walked, dist - used)
                walked += take
                used += take
                if walked >= step:
                    t = used / dist
                    cx = p0[0] + dx * t - min_x
                    cy = p0[1] + dy * t - min_y
                    pygame.draw.circle(temp, opaque_color, (int(cx), int(cy)), r)
                    walked = 0.0
        pygame.draw.circle(temp, opaque_color, (int(pts[-1][0] - min_x), int(pts[-1][1] - min_y)), r)
        
        alpha = color[3] if len(color) > 3 else 255
        if alpha < 255:
            temp.set_alpha(alpha)
        surface.blit(temp, (int(min_x), int(min_y)))




            self._draw_curve(ov, curve, (251, 191, 36, 64), w1)
            self._draw_curve(ov, curve, (0, 0, 0, 64), w2)
            self._draw_curve(self.screen, curve, (246, 173, 85), w3)
            self._draw_curve(ov, curve, (255, 255, 255, 140), max(1, int(RW*.09*sc)))