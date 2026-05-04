import pygame
import math
from config import C, RIBBON_H, RW, LP

class StaticRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self.show_graph = False

    def _ws(self, wx, wy): 
        return self.cam.world_to_screen(wx, wy)

    def draw_bg(self): 
        pygame.draw.rect(self.screen, C['bg'], (0, RIBBON_H, self.W, self.H))

    def draw_edges_layer(self, edges, color, width, dash=False, hidden_edges=None):
        w = max(1, int(width))
        # PERBAIKAN 1: Tidak lagi memaksa radius minimal 1. Jika w=1, maka r=0 (menghindari blob/titik raksasa)
        r = w // 2 
        
        for e in edges:
            if hidden_edges and id(e) in hidden_edges: continue
            
            pts = [{'x': e[0].x, 'y': e[0].y}]
            if len(e) > 2:
                pts.extend(e[2])
            pts.append({'x': e[1].x, 'y': e[1].y})
            
            p_start = self._ws(pts[0]['x'], pts[0]['y'])
            p_end = self._ws(pts[-1]['x'], pts[-1]['y'])
            margin = r * 2 + max(100, int(200 * self.cam.zoom))
            if (max(p_start[0], p_end[0]) < -margin or min(p_start[0], p_end[0]) > self.W + margin or
                max(p_start[1], p_end[1]) < RIBBON_H - margin or min(p_start[1], p_end[1]) > self.H + RIBBON_H + margin):
                continue
            
            if dash:
                dash_len = max(2, int(RW * 0.6 * self.cam.zoom))
                pos = 0
                drawing = True
                
                for i in range(len(pts) - 1):
                    sp1 = self._ws(pts[i]['x'], pts[i]['y'])
                    sp2 = self._ws(pts[i+1]['x'], pts[i+1]['y'])
                    
                    seg_dx = sp2[0] - sp1[0]; seg_dy = sp2[1] - sp1[1]
                    seg_len = math.hypot(seg_dx, seg_dy)
                    if seg_len < 0.1: continue
                    
                    udx = seg_dx / seg_len; udy = seg_dy / seg_len
                    seg_pos = 0
                    
                    while seg_pos < seg_len:
                        rem = dash_len - pos
                        step = min(rem, seg_len - seg_pos)
                        
                        if drawing:
                            x1 = sp1[0] + udx * seg_pos; y1 = sp1[1] + udy * seg_pos
                            x2 = x1 + udx * step; y2 = y1 + udy * step
                            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), w)
                            
                            # Gambar Round Caps HANYA jika garis tersebut cukup tebal (saat zoom in)
                            if r > 0:
                                pygame.draw.circle(self.screen, color, (int(x1), int(y1)), r)
                                pygame.draw.circle(self.screen, color, (int(x2), int(y2)), r)
                        
                        seg_pos += step
                        pos += step
                        if pos >= dash_len:
                            pos = 0; drawing = not drawing
            else:
                for i in range(len(pts) - 1):
                    sp1 = self._ws(pts[i]['x'], pts[i]['y'])
                    sp2 = self._ws(pts[i+1]['x'], pts[i+1]['y'])
                    
                    if r > 0:
                        pygame.draw.circle(self.screen, color, (int(sp1[0]), int(sp1[1])), r)
                        if i == len(pts) - 2: 
                            pygame.draw.circle(self.screen, color, (int(sp2[0]), int(sp2[1])), r)

                    if sp1 != sp2:
                        if r > 0:
                            angle = math.atan2(sp2[1] - sp1[1], sp2[0] - sp1[0])
                            dx = r * math.sin(angle); dy = r * -math.cos(angle)
                            p1_a = (sp1[0] + dx, sp1[1] + dy); p1_b = (sp1[0] - dx, sp1[1] - dy)
                            p2_a = (sp2[0] + dx, sp2[1] + dy); p2_b = (sp2[0] - dx, sp2[1] - dy)
                            pygame.draw.polygon(self.screen, color, [p1_a, p2_a, p2_b, p1_b])
                        else:
                            # Jika ketebalan poligon = 0, cukup tarik garis 1px (anti menghilang)
                            pygame.draw.line(self.screen, color, sp1, sp2, 1)

    def draw_map(self, city):
        sc = self.cam.zoom
        edges = city['edges']; rbs = city['roundabouts']; hidden = city.get('hidden_edges', set())
        self.draw_edges_layer(edges, C['grass'], LP*sc, hidden_edges=hidden)
        self.draw_edges_layer(edges, C['road_outer'], RW*1.6*sc, hidden_edges=hidden)
        
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y); ro = int(RW*1.5*sc)
            if ro >= 2: pygame.draw.circle(self.screen, C['road_outer'], (sx,sy), ro + max(1,int(RW*0.2*sc)))
            
        self.draw_edges_layer(edges, C['road_inner'], RW*sc, hidden_edges=hidden)
        
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y); ro = int(RW*1.5*sc); ri = int(RW*0.7*sc)
            if ro >= 2:
                pygame.draw.circle(self.screen, C['road_inner'], (sx,sy), ro)
                pygame.draw.circle(self.screen, C['rb_grass'], (sx,sy), ri)
                pygame.draw.circle(self.screen, C['road_outer'], (sx,sy), ri, max(1,int(3*sc)))
            
        # PERBAIKAN 2: Sembunyikan garis putus-putus jika peta terlampau Zoom Out (sc < 0.12)
        # Ini membersihkan tampilan kota jika dilihat dari satelit/awan.
        if sc > 0.12: 
            self.draw_edges_layer(edges, C['road_line'], max(1, RW*0.08*sc), dash=True, hidden_edges=hidden)

    def draw_graph(self, nodes, edges):
        sc = self.cam.zoom
        for e in edges:
            p1 = self._ws(e[0].x, e[0].y); p2 = self._ws(e[1].x, e[1].y)
            if (max(p1[0],p2[0]) < 0 or min(p1[0],p2[0]) > self.W or max(p1[1],p2[1]) < RIBBON_H or min(p1[1],p2[1]) > self.H+RIBBON_H): continue
            
            line_w = max(1, int(12*sc))
            pygame.draw.line(self.screen, (0, 255, 255), p1, p2, line_w)
            
            cap_r = line_w // 2
            if cap_r > 0:
                pygame.draw.circle(self.screen, (0, 255, 255), p1, cap_r)
                pygame.draw.circle(self.screen, (0, 255, 255), p2, cap_r)
            
        for n in nodes:
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < RIBBON_H or sy > self.H+RIBBON_H: continue
            
            cr1 = max(1, int(16*sc))
            cr2 = max(0, int(4*sc))
            pygame.draw.circle(self.screen, (255, 42, 42), (sx, sy), cr1)
            if cr2 > 0:
                pygame.draw.circle(self.screen, C['white'], (sx, sy), cr1, cr2)
