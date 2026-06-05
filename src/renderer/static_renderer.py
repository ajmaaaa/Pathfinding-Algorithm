import pygame
import math
from config import C, RIBBON_H, RW, LP
from src.core.geometry import _clip_polyline, get_roundabout_clip_distance

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
        ribbon_h = self.screen.get_height() - self.H
        pygame.draw.rect(self.screen, C['bg'], (0, ribbon_h, self.W, self.H))

    def _screen_curve(self, edge, edge_curves):
        pts = edge_curves.get(id(edge)) if edge_curves else None
        if not pts:
            pts = [(edge[0].x, edge[0].y), (edge[1].x, edge[1].y)]
        return [self._ws(x, y) for x, y in pts]

    def _draw_polyline_round(self, surface, pts, color, width, cap_start=True, cap_end=True):
        if len(pts) < 2: return
        w = max(1, int(width))
        r = max(1, w // 2)
        step = max(1.0, r * 0.15)
        
        if cap_start:
            pygame.draw.circle(surface, color, (int(pts[0][0]), int(pts[0][1])), r)
        walked = 0.0
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
                    cx = p0[0] + dx * t
                    cy = p0[1] + dy * t
                    pygame.draw.circle(surface, color, (int(cx), int(cy)), r)
                    walked = 0.0
        if cap_end:
            pygame.draw.circle(surface, color, (int(pts[-1][0]), int(pts[-1][1])), r)

    def _draw_dashed_polyline(self, pts, color, width, clip_start, clip_end, dash_len=None):
        if len(pts) < 2:
            return

        if dash_len is None:
            dash_len = max(4.0, RW * 0.4 * self.cam.zoom)
        remain = dash_len
        drawing = True

        total_len = 0.0
        for i in range(1, len(pts)):
            total_len += math.hypot(pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1])
            
        walked_total = 0.0

        w = max(1, int(width))
        r_dash = max(1, w // 2)
        step = max(1.0, r_dash * 0.2)
        walked_circle = 0.0

        for i in range(1, len(pts)):
            p0 = pts[i - 1]
            p1 = pts[i]
            dx_seg = p1[0] - p0[0]
            dy_seg = p1[1] - p0[1]
            seg_len = math.hypot(dx_seg, dy_seg)
            if seg_len < 1:
                continue
            
            used = 0.0
            while used < seg_len:
                take = min(remain, seg_len - used)
                mid_dist = walked_total + used + take / 2.0
                
                if drawing and clip_start < mid_dist < (total_len - clip_end):
                    c_used = 0.0
                    while c_used < take:
                        c_take = min(step - walked_circle, take - c_used)
                        walked_circle += c_take
                        c_used += c_take
                        if walked_circle >= step:
                            t = (used + c_used) / max(0.0001, seg_len)
                            cx = p0[0] + dx_seg * t
                            cy = p0[1] + dy_seg * t
                            pygame.draw.circle(self.screen, color, (int(cx), int(cy)), r_dash)
                            walked_circle = 0.0
                            
                used += take
                remain -= take
                if remain <= 0:
                    remain = dash_len
                    drawing = not drawing
                    if drawing and clip_start < (walked_total + used) < (total_len - clip_end):
                        t = used / max(0.0001, seg_len)
                        pygame.draw.circle(self.screen, color, (int(p0[0] + dx_seg * t), int(p0[1] + dy_seg * t)), r_dash)
                        walked_circle = 0.0
                        
            walked_total += seg_len

    def _clip_pts_by_ellipse(self, pts, rb0_node, rb1_node, rx_val=None):
        if not pts:
            return pts
        sc = self.cam.zoom
        rx = rx_val if rx_val is not None else RW * 2.25 * sc
        ry = rx * 0.5

        def get_ellipse_intersection(p_in, p_out, cx, cy):
            x0, y0 = p_in
            x1, y1 = p_out
            u0 = (x0 - cx) / rx
            v0 = (y0 - cy) / ry
            du = (x1 - x0) / rx
            dv = (y1 - y0) / ry
            a = du*du + dv*dv
            if a < 1e-9:
                return p_out
            b = 2.0 * (u0*du + v0*dv)
            c = u0*u0 + v0*v0 - 1.0
            discriminant = b*b - 4*a*c
            if discriminant < 0:
                return p_out
            t = (-b + math.sqrt(discriminant)) / (2.0 * a)
            t = max(0.0, min(1.0, t))
            return (x0 + t * (x1 - x0), y0 + t * (y1 - y0))

        result = pts[:]

        # Clip start of polyline if rb0_node is a roundabout
        if rb0_node:
            cx, cy = self._ws(rb0_node.x, rb0_node.y)
            # Find where we exit the ellipse
            idx = 0
            while idx < len(result):
                x, y = result[idx]
                u = (x - cx) / rx
                v = (y - cy) / ry
                if u*u + v*v < 1.0:
                    idx += 1
                else:
                    break
            
            if idx >= len(result):
                return []
            elif idx > 0:
                intersection = get_ellipse_intersection(result[idx-1], result[idx], cx, cy)
                result = [intersection] + result[idx:]

        # Clip end of polyline if rb1_node is a roundabout
        if rb1_node:
            cx, cy = self._ws(rb1_node.x, rb1_node.y)
            # Find where we exit the ellipse walking backwards
            idx = len(result) - 1
            while idx >= 0:
                x, y = result[idx]
                u = (x - cx) / rx
                v = (y - cy) / ry
                if u*u + v*v < 1.0:
                    idx -= 1
                else:
                    break
            
            if idx < 0:
                return []
            elif idx < len(result) - 1:
                intersection = get_ellipse_intersection(result[idx+1], result[idx], cx, cy)
                result = result[:idx+1] + [intersection]

        return result

    def draw_edges_layer(self, edges, color, width, dash=False, hidden_edges=None, edge_curves=None, rx_val=None, roundabouts=None):
        ribbon_h = self.screen.get_height() - self.H
        sc = self.cam.zoom
        w = max(1, int(width)); r = max(1, w // 2); drawn_nodes = set()
        for e in edges:
            if hidden_edges and id(e) in hidden_edges: continue
            pts = self._screen_curve(e, edge_curves)
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if (max(xs) < -r*2 or min(xs) > self.W + r*2 or
                max(ys) < ribbon_h - r*2 or min(ys) > self.H+ribbon_h + r*2): continue

            # Determine if either endpoint is a roundabout OR close to one (<180px)
            rb0_node = None
            if getattr(e[0], 'is_roundabout', False):
                rb0_node = e[0]
            elif roundabouts:
                for rb in roundabouts:
                    if math.hypot(e[0].x - rb.x, e[0].y - rb.y) < 180.0:
                        rb0_node = rb
                        break

            rb1_node = None
            if getattr(e[1], 'is_roundabout', False):
                rb1_node = e[1]
            elif roundabouts:
                for rb in roundabouts:
                    if math.hypot(e[1].x - rb.x, e[1].y - rb.y) < 180.0:
                        rb1_node = rb
                        break

            if dash:
                # Clip garis putih menggunakan elips bundaran
                clipped = self._clip_pts_by_ellipse(pts, rb0_node, rb1_node, rx_val=rx_val)
                if clipped and len(clipped) >= 2:
                    self._draw_dashed_polyline(clipped, color, w, 0, 0)
            else:
                # Clip solid road menggunakan elips bundaran
                clipped = self._clip_pts_by_ellipse(pts, rb0_node, rb1_node, rx_val=rx_val)
                if not clipped or len(clipped) < 2:
                    continue
                # Gambar titik endpoint HANYA untuk node yang bukan pusat bundaran
                # Suppress cap at roundabout boundary to avoid pinching artefact
                draw_cap_start = not rb0_node
                draw_cap_end = not rb1_node
                if draw_cap_start and id(e[0]) not in drawn_nodes:
                    pygame.draw.circle(self.screen, color, (int(clipped[0][0]), int(clipped[0][1])), r)
                    drawn_nodes.add(id(e[0]))
                if draw_cap_end and id(e[1]) not in drawn_nodes:
                    pygame.draw.circle(self.screen, color, (int(clipped[-1][0]), int(clipped[-1][1])), r)
                    drawn_nodes.add(id(e[1]))
                self._draw_polyline_round(self.screen, clipped, color, w,
                                          cap_start=draw_cap_start,
                                          cap_end=draw_cap_end)

    def draw_map(self, city):
        ribbon_h = self.screen.get_height() - self.H
        sc = self.cam.zoom
        
        editor_bg = city.get('editor_bg_entities')
        if editor_bg is not None:
            def platform_depth(e):
                name = e.__class__.__name__
                if name == 'BasePlatform':
                    return e.render_y - 4000
                elif name == 'Pulau':
                    return e.render_y - 6000
                return e.y
            
            sorted_bg = sorted(editor_bg, key=platform_depth)
            offset_x = self.cam.sw // 2
            offset_y = self.cam.sh // 2 + ribbon_h
            for e in sorted_bg:
                name = e.__class__.__name__
                if name == "BasePlatform":
                    orig_x, orig_ry = e.x, e.render_y
                    orig_rc, orig_rr = e.rad_c, e.rad_r
                    e.x = (e.x - self.cam.cam_x) * sc + offset_x
                    e.render_y = (e.render_y - self.cam.cam_y) * sc + offset_y
                    e.rad_c = int(e.rad_c * sc)
                    e.rad_r = int(e.rad_r * sc)
                    e.render(self.screen)
                    e.x, e.render_y = orig_x, orig_ry
                    e.rad_c, e.rad_r = orig_rc, orig_rr
                elif name == "Pulau":
                    e.render(self.screen, offset_x, offset_y, self.cam.cam_x, self.cam.cam_y, sc)
        else:
            outline = city.get('island_outline')
            if outline:
                sand = [self._ws(x * 1.07, y * 1.07) for x, y in outline]
                grass = [self._ws(x, y) for x, y in outline]
                if len(sand) >= 3:
                    pygame.draw.polygon(self.screen, C['sand'], sand)
                    pygame.draw.polygon(self.screen, C['grass'], grass)
            else:
                cx, cy = self._ws(0, 0)
                sand_r = int(2100 * sc)
                grass_r = int(1900 * sc)
                if sand_r > 0:
                    pygame.draw.circle(self.screen, C['sand'], (cx, cy), sand_r)
                    pygame.draw.circle(self.screen, C['grass'], (cx, cy), grass_r)

        editor_roads = city.get('editor_roads')
        if editor_roads is not None:
            offset_x = self.cam.sw // 2
            offset_y = self.cam.sh // 2 + ribbon_h
            for e in editor_roads:
                e.render(self.screen, offset_x, offset_y, self.cam.cam_x, self.cam.cam_y, sc)
        else:
            edges = city['edges']; rbs = city['roundabouts']; hidden = city.get('hidden_edges', set())
            edge_curves = city.get('edge_curves', {})
            
            # Layer-specific clipping radii and matched roundabout outer/shadow dimensions
            self.draw_edges_layer(edges, C.get('road_shadow', C['road_outer']), RW*1.95*sc, hidden_edges=hidden, edge_curves=edge_curves, rx_val=RW*1.75*sc, roundabouts=rbs)
            self.draw_edges_layer(edges, C['road_outer'], RW*1.62*sc, hidden_edges=hidden, edge_curves=edge_curves, rx_val=RW*1.75*sc, roundabouts=rbs)
            for rb in rbs:
                sx, sy = self._ws(rb.x, rb.y)
                rx_out = RW * 2.25 * sc
                if rx_out >= 2:
                    sh_x = rx_out + max(1.0, RW * 0.48 * sc)
                    sh_y = sh_x * 0.5
                    ob_x = rx_out + max(1.0, RW * 0.31 * sc)
                    ob_y = ob_x * 0.5
                    pygame.draw.ellipse(self.screen, C.get('road_shadow', C['road_outer']), (int(sx - sh_x), int(sy - sh_y), int(2 * sh_x), int(2 * sh_y)))
                    pygame.draw.ellipse(self.screen, C['road_outer'], (int(sx - ob_x), int(sy - ob_y), int(2 * ob_x), int(2 * ob_y)))
                
            self.draw_edges_layer(edges, C['road_inner'], RW*sc, hidden_edges=hidden, edge_curves=edge_curves, rx_val=RW*2.05*sc, roundabouts=rbs)
            for rb in rbs:
                sx, sy = self._ws(rb.x, rb.y)
                rx_out = RW * 2.25 * sc
                ry_out = rx_out * 0.5
                rx_in = RW * 1.05 * sc
                ry_in = rx_in * 0.5
                if rx_out >= 2:
                    pygame.draw.ellipse(self.screen, C['road_inner'], (int(sx - rx_out), int(sy - ry_out), int(2 * rx_out), int(2 * ry_out)))
                    pygame.draw.ellipse(self.screen, C['rb_grass'], (int(sx - rx_in), int(sy - ry_in), int(2 * rx_in), int(2 * ry_in)))
                    pygame.draw.ellipse(self.screen, C['road_outer'], (int(sx - rx_in), int(sy - ry_in), int(2 * rx_in), int(2 * ry_in)), max(1, int(3 * sc)))
                
                if sc > 0.06:
                    rc_x = (rx_out + rx_in) / 2.0
                    rc_y = rc_x * 0.5
                    h_val = ((rc_x - rc_y)**2) / ((rc_x + rc_y)**2) if (rc_x + rc_y) > 0 else 0
                    circ = math.pi * (rc_x + rc_y) * (1 + 3*h_val / (10 + math.sqrt(4 - 3*h_val)))
                    num_dashes = max(1, int(circ / (RW * 0.4 * sc * 2)))
                    dl = circ / (num_dashes * 2)
                    pts = []
                    for i in range(37):
                        a = i * math.pi * 2 / 36
                        pts.append((sx + math.cos(a) * rc_x, sy + math.sin(a) * rc_y))
                    self._draw_dashed_polyline(pts, C['road_line'], max(1, RW*0.075*sc), 0, 0, dl)
                
            if sc > 0.06: self.draw_edges_layer(edges, C['road_line'], max(1, RW*0.075*sc), dash=True, hidden_edges=hidden, edge_curves=edge_curves, rx_val=RW*2.25*sc, roundabouts=rbs)

    def draw_graph(self, nodes, edges, edge_curves=None):
        ribbon_h = self.screen.get_height() - self.H
        sc = self.cam.zoom
        ov = pygame.Surface((self.W, self.H + ribbon_h), pygame.SRCALPHA)
        
        rbs = [n for n in nodes if getattr(n, 'is_roundabout', False)]
        
        # Hubungkan pintu masuk/keluar bundaran (virtual junction nodes) menjadi satu ring melingkar di graf
        # Radius ring bundaran di dunia (sama dengan yang dipakai di pathfinder)
        RB_RING_RADIUS = 140.25
        
        for n in rbs:
            junctions = []
            for e in n.edges:
                nb = e[1] if e[0] is n else e[0]
                pts = edge_curves.get(id(e)) if edge_curves else None
                if not pts:
                    pts = [(e[0].x, e[0].y), (e[1].x, e[1].y)]
                if e[0] is n:
                    pts = list(reversed(pts))
                r_end = get_roundabout_clip_distance(n, nb)
                clipped = _clip_polyline(pts, 0.0, r_end)
                if clipped:
                    jx, jy = clipped[-1]
                    # Hitung sudut "isometrik" yang benar: dy dibagi 0.5 karena ellipse isometrik
                    ang = math.atan2((jy - n.y) / 0.5, jx - n.x)
                    junctions.append((ang, jx, jy))
            
            # Sort berdasarkan sudut isometrik agar urut CCW (counter-clockwise)
            junctions.sort(key=lambda x: x[0])
            
            if len(junctions) >= 2:
                # Gambar arc ring CCW antar junction berurutan
                for i in range(len(junctions)):
                    ang1, jx1, jy1 = junctions[i]
                    ang2, jx2, jy2 = junctions[(i + 1) % len(junctions)]
                    
                    # Pastikan bergerak CCW: ang2 selalu lebih kecil (CCW = delta negatif)
                    if ang2 >= ang1:
                        ang2_ccw = ang2 - math.pi * 2
                    else:
                        ang2_ccw = ang2
                        
                    arc_pts = []
                    steps = 18
                    for step in range(steps + 1):
                        t = step / steps
                        a = ang1 + (ang2_ccw - ang1) * t
                        # Snap ke ring bundaran (isometrik ellipse)
                        wx = n.x + math.cos(a) * RB_RING_RADIUS
                        wy = n.y + math.sin(a) * RB_RING_RADIUS * 0.5
                        sx, sy = self._ws(wx, wy)
                        arc_pts.append((sx, sy))
                    
                    if len(arc_pts) >= 2:
                        pygame.draw.lines(ov, (34, 211, 238, 95), False, arc_pts, max(1, int(4 * sc)))
                    
        for e in edges:
            pts = self._screen_curve(e, edge_curves or {})
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if (max(xs) < 0 or min(xs) > self.W or max(ys) < ribbon_h or min(ys) > self.H+ribbon_h): continue
            
            rb0_node = e[0] if getattr(e[0], 'is_roundabout', False) else None
            if not rb0_node:
                for rb in rbs:
                    if math.hypot(e[0].x - rb.x, e[0].y - rb.y) < 180.0:
                        rb0_node = rb
                        break
            rb1_node = e[1] if getattr(e[1], 'is_roundabout', False) else None
            if not rb1_node:
                for rb in rbs:
                    if math.hypot(e[1].x - rb.x, e[1].y - rb.y) < 180.0:
                        rb1_node = rb
                        break
            
            clipped = self._clip_pts_by_ellipse(pts, rb0_node, rb1_node, rx_val=RW * 2.25 * sc)
            if clipped and len(clipped) >= 2:
                pygame.draw.lines(ov, (34, 211, 238, 95), False, clipped, max(1, int(4*sc)))
            
        for n in nodes:
            if getattr(n, 'is_roundabout', False):
                # Gambar node junction di tepi bundaran (posisi snap ke ring ellipse)
                for e in n.edges:
                    nb = e[1] if e[0] is n else e[0]
                    pts = edge_curves.get(id(e)) if edge_curves else None
                    if not pts:
                        pts = [(e[0].x, e[0].y), (e[1].x, e[1].y)]
                    if e[0] is n:
                        pts = list(reversed(pts))
                    r_end = get_roundabout_clip_distance(n, nb)
                    clipped = _clip_polyline(pts, 0.0, r_end)
                    if clipped:
                        jx, jy = clipped[-1]
                        # Snap node junction ke ring bundaran
                        ang = math.atan2((jy - n.y) / 0.5, jx - n.x)
                        snap_x = n.x + math.cos(ang) * RB_RING_RADIUS
                        snap_y = n.y + math.sin(ang) * RB_RING_RADIUS * 0.5
                        sx, sy = self._ws(snap_x, snap_y)
                        if sx < 0 or sx > self.W or sy < ribbon_h or sy > self.H+ribbon_h: continue
                        pygame.draw.circle(ov, (239, 68, 68, 135), (sx, sy), max(3, int(12*sc)))
                        pygame.draw.circle(ov, C['white'] + (150,), (sx, sy), max(3, int(12*sc)), max(1, int(3*sc)))
                continue
            is_too_close_to_roundabout = False
            for e in n.edges:
                nb = e[1] if e[0] is n else e[0]
                if getattr(nb, 'is_roundabout', False):
                    if math.hypot(n.x - nb.x, n.y - nb.y) < 180.0:
                        is_too_close_to_roundabout = True
                        break
            if is_too_close_to_roundabout:
                continue
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < ribbon_h or sy > self.H+ribbon_h: continue
            pygame.draw.circle(ov, (239, 68, 68, 135), (sx, sy), max(3, int(12*sc)))
            pygame.draw.circle(ov, C['white'] + (150,), (sx, sy), max(3, int(12*sc)), max(1, int(3*sc)))
        self.screen.blit(ov, (0, 0))

