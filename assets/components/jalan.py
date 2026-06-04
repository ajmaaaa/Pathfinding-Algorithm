import pygame
import math

def screen_to_grid(x, y, origin_x=2400, origin_y=600):
    """Mengonversi koordinat layar (un-offset) ke koordinat kisi isometrik (c, r)."""
    dx = (x - origin_x) / 200
    dy = (y - origin_y) / 100
    c = (dy + dx) / 2
    r = (dy - dx) / 2
    return c, r

def grid_to_screen(c, r, origin_x=2400, origin_y=600):
    """Mengonversi koordinat kisi isometrik (c, r) kembali ke koordinat layar (un-offset)."""
    return origin_x + (c - r) * 200, origin_y + (c + r) * 100

class RoadSegment:
    def __init__(self, x1, y1, x2, y2, bend_amount=0.0, nodes=None, bends=None):
        if nodes is not None:
            self.nodes = [list(n) for n in nodes]
        else:
            self.nodes = [[x1, y1], [x2, y2]]
            
        if bends is not None:
            self.bends = list(bends)
        else:
            self.bends = [bend_amount]
            
        # Pastikan jumlah bends sesuai dengan jumlah segmen (jumlah nodes - 1)
        while len(self.bends) < len(self.nodes) - 1:
            self.bends.append(0.0)
            
        self.active_segment = 0
        self.selected = False
        self.active_node = None  # Indeks berbasis 1 (1, 2, ..., len(nodes))
        self.update_center()

    @property
    def x1(self):
        return self.nodes[0][0]
    @x1.setter
    def x1(self, val):
        self.nodes[0][0] = val
        
    @property
    def y1(self):
        return self.nodes[0][1]
    @y1.setter
    def y1(self, val):
        self.nodes[0][1] = val
        
    @property
    def x2(self):
        return self.nodes[-1][0]
    @x2.setter
    def x2(self, val):
        self.nodes[-1][0] = val
        
    @property
    def y2(self):
        return self.nodes[-1][1]
    @y2.setter
    def y2(self, val):
        self.nodes[-1][1] = val

    @property
    def bend_amount(self):
        seg_idx = getattr(self, "active_segment", 0)
        if seg_idx is None or seg_idx < 0 or seg_idx >= len(self.bends):
            seg_idx = 0
        return self.bends[seg_idx]

    @bend_amount.setter
    def bend_amount(self, val):
        seg_idx = getattr(self, "active_segment", 0)
        if seg_idx is None or seg_idx < 0 or seg_idx >= len(self.bends):
            seg_idx = 0
        self.bends[seg_idx] = val

    def update_center(self):
        xs = [n[0] for n in self.nodes]
        ys = [n[1] for n in self.nodes]
        self.x = sum(xs) / len(xs)
        self.y = sum(ys) / len(ys)

    def get_segment_points(self, idx):
        """Mengembalikan list titik untuk sub-segmen tertentu"""
        x1, y1 = self.nodes[idx]
        x2, y2 = self.nodes[idx+1]
        bend_amount = self.bends[idx]
        
        p1 = (x1, y1)
        p2 = (x2, y2)
        
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return [p1, p2]
            
        num_steps = max(5, int(dist / 10))
        
        if abs(bend_amount) < 0.01:
            pts = []
            for i in range(num_steps):
                t = i / (num_steps - 1)
                pts.append((x1 + t * dx, y1 + t * dy))
            return pts
            
        # Melengkung (Bezier kuadratik)
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        
        nx = -dy / dist
        ny = dx / dist
        
        bend_factor = dist * 0.8 * bend_amount
        cx = mx + nx * bend_factor
        cy = my + ny * bend_factor
        
        pts = []
        for i in range(num_steps):
            t = i / (num_steps - 1)
            x = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
            y = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
            pts.append((x, y))
        return pts

    def get_points(self):
        """Mengembalikan list titik centerline dari seluruh segmen jalan"""
        all_pts = []
        for i in range(len(self.nodes) - 1):
            pts = self.get_segment_points(i)
            if i > 0:
                all_pts.extend(pts[1:])
            else:
                all_pts.extend(pts)
        if not all_pts:
            return []
        return all_pts

    def render(self, screen, offset_x=0, offset_y=0, camera_x=0, camera_y=0, zoom=1.0):
        ROAD_COLOR = (80, 85, 90)
        BORDER_COLOR = (50, 52, 55)
        LINE_COLOR = (245, 245, 245)
        ROAD_WIDTH = 5 * zoom
        if ROAD_WIDTH < 1: ROAD_WIDTH = 1
        
        pts = self.get_points()
        if len(pts) < 2:
            return
            
        poly_left = []
        poly_right = []
        
        for i in range(len(pts)):
            x, y = pts[i]
            scr_x = (x - camera_x) * zoom + offset_x
            scr_y = (y - camera_y) * zoom + offset_y
            
            if i < len(pts) - 1:
                dx = pts[i+1][0] - x
                dy = pts[i+1][1] - y
            else:
                dx = x - pts[i-1][0]
                dy = y - pts[i-1][1]
                
            length = math.hypot(dx, dy)
            if length == 0:
                nx, ny = 0, 0
            else:
                nx = -dy / length
                ny = dx / length
                
            # Snapping normal vector at the endpoints to the secondary isometric axis
            if i == 0 or i == len(pts) - 1:
                if length > 0:
                    tx = dx / length
                    ty = dy / length
                    
                    inv_sqrt5 = 1.0 / math.sqrt(5)
                    ax_A_x = 2.0 * inv_sqrt5
                    ax_A_y = 1.0 * inv_sqrt5
                    ax_B_x = -2.0 * inv_sqrt5
                    ax_B_y = 1.0 * inv_sqrt5
                    
                    cos_A = abs(tx * ax_A_x + ty * ax_A_y)
                    cos_B = abs(tx * ax_B_x + ty * ax_B_y)
                    
                    if cos_A > cos_B:
                        # Road is closer to Axis A -> cut parallel to Axis B
                        dot = nx * ax_B_x + ny * ax_B_y
                        if abs(dot) > 0.01:
                            k = 1.0 / dot
                            nx, ny = k * ax_B_x, k * ax_B_y
                    else:
                        # Road is closer to Axis B -> cut parallel to Axis A
                        dot = nx * ax_A_x + ny * ax_A_y
                        if abs(dot) > 0.01:
                            k = 1.0 / dot
                            nx, ny = k * ax_A_x, k * ax_A_y
                            
            poly_left.append((scr_x + nx * ROAD_WIDTH, scr_y + ny * ROAD_WIDTH))
            poly_right.insert(0, (scr_x - nx * ROAD_WIDTH, scr_y - ny * ROAD_WIDTH))
            
        full_poly = poly_left + poly_right
        
        # Gambar aspal jalan
        pygame.draw.polygon(screen, ROAD_COLOR, full_poly)
        pygame.draw.aalines(screen, BORDER_COLOR, False, poly_left)
        pygame.draw.aalines(screen, BORDER_COLOR, False, poly_right)
        
        # Gambar garis marka putih putus-putus centerline secara rapi
        dash_state = True
        dash_counter = 0
        for i in range(len(pts) - 1):
            if dash_state:
                p1_scr = ((pts[i][0] - camera_x) * zoom + offset_x, (pts[i][1] - camera_y) * zoom + offset_y)
                p2_scr = ((pts[i+1][0] - camera_x) * zoom + offset_x, (pts[i+1][1] - camera_y) * zoom + offset_y)
                pygame.draw.line(screen, LINE_COLOR, p1_scr, p2_scr, max(1, int(3 * zoom)))
            dash_counter += 1
            if dash_counter >= 2: # 2 segmen line (20px), 2 segmen gap (20px)
                dash_state = not dash_state
                dash_counter = 0

    def check_node_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y):
        """Memeriksa apakah salah satu node di-klik menggunakan koordinat screen space"""
        for idx, (nx, ny) in enumerate(self.nodes):
            scr_x = (nx - camera_x) * zoom + offset_x
            scr_y = (ny - camera_y) * zoom + offset_y
            if math.hypot(mouse_pos[0] - scr_x, mouse_pos[1] - scr_y) <= 15:
                return idx + 1
        return None

    def is_point_near_road(self, pt):
        """Memeriksa apakah titik berada dekat dengan badan jalan"""
        pts = self.get_points()
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            
            l2 = (x2 - x1)**2 + (y2 - y1)**2
            if l2 == 0:
                dist = math.hypot(pt[0] - x1, pt[1] - y1)
            else:
                t = max(0, min(1, ((pt[0] - x1) * (x2 - x1) + (pt[1] - y1) * (y2 - y1)) / l2))
                proj_x = x1 + t * (x2 - x1)
                proj_y = y1 + t * (y2 - y1)
                dist = math.hypot(pt[0] - proj_x, pt[1] - proj_y)
                
            if dist <= 25:  
                return True
        return False

    def check_road_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y, threshold=20):
        """Memeriksa apakah posisi mouse di layar dekat dengan badan jalan (kembalikan segment_idx)"""
        best_seg = None
        min_dist = float('inf')
        
        for seg_idx in range(len(self.nodes) - 1):
            pts = self.get_segment_points(seg_idx)
            for i in range(len(pts) - 1):
                # Konversi titik jalan ke screen space
                x1 = (pts[i][0] - camera_x) * zoom + offset_x
                y1 = (pts[i][1] - camera_y) * zoom + offset_y
                x2 = (pts[i+1][0] - camera_x) * zoom + offset_x
                y2 = (pts[i+1][1] - camera_y) * zoom + offset_y
                
                l2 = (x2 - x1)**2 + (y2 - y1)**2
                if l2 == 0:
                    dist = math.hypot(mouse_pos[0] - x1, mouse_pos[1] - y1)
                else:
                    t = max(0, min(1, ((mouse_pos[0] - x1) * (x2 - x1) + (mouse_pos[1] - y1) * (y2 - y1)) / l2))
                    proj_x = x1 + t * (x2 - x1)
                    proj_y = y1 + t * (y2 - y1)
                    dist = math.hypot(mouse_pos[0] - proj_x, mouse_pos[1] - proj_y)
                
                if dist < min_dist:
                    min_dist = dist
                    best_seg = seg_idx
                    
        road_half_width_scr = 20 * zoom
        max_dist = max(threshold, road_half_width_scr)
        if min_dist <= max_dist:
            return True, best_seg
        return False, None

    def get_length(self):
        """Menghitung panjang total jalan raya dalam satuan piksel"""
        pts = self.get_points()
        length = 0.0
        for i in range(len(pts) - 1):
            length += math.hypot(pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1])
        return length

    def cycle_segment_bend(self, seg_idx):
        if seg_idx < 0 or seg_idx >= len(self.bends):
            return
        b = self.bends[seg_idx]
        if abs(b) < 0.05:
            self.bends[seg_idx] = 0.5
        elif abs(b - 0.5) < 0.05:
            self.bends[seg_idx] = 1.0
        elif abs(b - 1.0) < 0.05:
            self.bends[seg_idx] = -0.5
        elif abs(b - (-0.5)) < 0.05:
            self.bends[seg_idx] = -1.0
        else:
            self.bends[seg_idx] = 0.0

    def cycle_bend(self):
        self.cycle_segment_bend(getattr(self, "active_segment", 0))

    def handle_double_click(self, node_num):
        """Menangani klik ganda pada node handle"""
        idx = node_num - 1
        if 0 < idx < len(self.nodes) - 1:
            # Node tengah -> Snap siku-siku 90° di isometrik!
            A = self.nodes[idx - 1]
            B = self.nodes[idx + 1]
            c_A, r_A = screen_to_grid(A[0], A[1])
            c_B, r_B = screen_to_grid(B[0], B[1])
            
            # Pilihan sudut isometrik
            c1_x, c1_y = grid_to_screen(c_A, r_B)
            c2_x, c2_y = grid_to_screen(c_B, r_A)
            
            curr = self.nodes[idx]
            d1 = math.hypot(curr[0] - c1_x, curr[1] - c1_y)
            d2 = math.hypot(curr[0] - c2_x, curr[1] - c2_y)
            
            best_c = [c1_x, c1_y] if d1 < d2 else [c2_x, c2_y]
            self.nodes[idx] = [round(best_c[0] / 20) * 20, round(best_c[1] / 20) * 20]
            
            # Luruskan kelengkungan segmen adjacent agar siku
            self.bends[idx - 1] = 0.0
            self.bends[idx] = 0.0
            self.update_center()
        else:
            # Node ujung -> Putar kelengkungan segmen terdekat
            seg_idx = 0 if idx == 0 else len(self.bends) - 1
            self.cycle_segment_bend(seg_idx)
            self.update_center()

    def insert_node(self, seg_idx, x, y):
        """Menyisipkan node baru pada sub-segmen tertentu"""
        self.nodes.insert(seg_idx + 1, [x, y])
        self.bends.insert(seg_idx + 1, 0.0)
        self.bends[seg_idx] = 0.0
        self.update_center()

    def snap_node(self, node_num, all_roads, snap_dist=25):
        """Mendekatkan node ke node jalan lain jika berada di dalam jarak snap"""
        idx = node_num - 1
        target_x, target_y = self.nodes[idx]
        
        best_snap = None
        min_d = snap_dist
        
        for road in all_roads:
            if road == self:
                continue
            for r_node in road.nodes:
                d = math.hypot(target_x - r_node[0], target_y - r_node[1])
                if d < min_d:
                    min_d = d
                    best_snap = (r_node[0], r_node[1])
                    
        if best_snap:
            self.nodes[idx] = [best_snap[0], best_snap[1]]
            self.update_center()
            return True
        return False

class Roundabout:
    def __init__(self, c, r, origin_x=2400, origin_y=600):
        self.c = c
        self.r = r
        self.x, self.y = grid_to_screen(c, r, origin_x, origin_y)
        self.selected = False
        self.group_id = None
        self.depth_offset = 0
        
    def render(self, screen, offset_x=0, offset_y=0, camera_x=0, camera_y=0, zoom=1.0):
        ROAD_COLOR = (80, 85, 90)
        BORDER_COLOR = (50, 52, 55)
        C_GRASS = (130, 200, 100)
        
        cx_scr = (self.x - camera_x) * zoom + offset_x
        cy_scr = (self.y - camera_y) * zoom + offset_y
        
        rx_out = int(200 * zoom)
        ry_out = int(100 * zoom)
        if rx_out < 1: rx_out = 1
        if ry_out < 1: ry_out = 1
        
        # Gambar bundaran sebagai belah ketupat (diamond) agar sejajar dengan arah diagonal jalan isometrik
        pts_outer = [
            (cx_scr, cy_scr - ry_out),
            (cx_scr + rx_out, cy_scr),
            (cx_scr, cy_scr + ry_out),
            (cx_scr - rx_out, cy_scr)
        ]
        pygame.draw.polygon(screen, ROAD_COLOR, pts_outer)
        pygame.draw.polygon(screen, BORDER_COLOR, pts_outer, max(1, int(2 * zoom)))
        
        rx_in = int(140 * zoom)
        ry_in = int(70 * zoom)
        if rx_in < 1: rx_in = 1
        if ry_in < 1: ry_in = 1
        pts_inner = [
            (cx_scr, cy_scr - ry_in),
            (cx_scr + rx_in, cy_scr),
            (cx_scr, cy_scr + ry_in),
            (cx_scr - rx_in, cy_scr)
        ]
        pygame.draw.polygon(screen, C_GRASS, pts_inner)
        pygame.draw.polygon(screen, BORDER_COLOR, pts_inner, max(1, int(2 * zoom)))
        
        # Dashed centerline berbentuk diamond
        rx_mid = int(170 * zoom)
        ry_mid = int(85 * zoom)
        pts_mid = [
            (cx_scr, cy_scr - ry_mid),
            (cx_scr + rx_mid, cy_scr),
            (cx_scr, cy_scr + ry_mid),
            (cx_scr - rx_mid, cy_scr)
        ]
        
        # Fungsi pembantu untuk interpolasi garis
        def draw_dashed_line(surface, color, p1, p2, width, dash_len=15, gap_len=15):
            import math
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.hypot(dx, dy)
            if dist == 0: return
            nx = dx / dist
            ny = dy / dist
            
            d = 0
            while d < dist:
                d_end = min(d + dash_len, dist)
                start_pt = (p1[0] + nx * d, p1[1] + ny * d)
                end_pt = (p1[0] + nx * d_end, p1[1] + ny * d_end)
                pygame.draw.line(surface, color, start_pt, end_pt, width)
                d += dash_len + gap_len

        line_width = max(1, int(2 * zoom))
        for i in range(4):
            p1 = pts_mid[i]
            p2 = pts_mid[(i+1)%4]
            draw_dashed_line(screen, (245, 245, 245), p1, p2, line_width, dash_len=15*zoom, gap_len=15*zoom)
            
        if self.selected:
            pygame.draw.ellipse(screen, (0, 255, 255), rect_outer, 2)

    def check_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y):
        scr_x = (self.x - camera_x) * zoom + offset_x
        scr_y = (self.y - camera_y) * zoom + offset_y
        rx = 220 * zoom
        ry = 110 * zoom
        if rx == 0 or ry == 0:
            return False
        return ((mouse_pos[0] - scr_x) / rx) ** 2 + ((mouse_pos[1] - scr_y) / ry) ** 2 <= 1.0


class RoadCorner90:
    def __init__(self, c, r, direction=0, origin_x=2400, origin_y=600):
        self.c = c
        self.r = r
        self.direction = direction  # 0: Top, 1: Right, 2: Bottom, 3: Left
        self.x, self.y = grid_to_screen(c, r, origin_x, origin_y)
        self.selected = False
        self.group_id = None
        self.depth_offset = 0
        
    def get_points(self):
        cx, cy = self.x, self.y
        import math
        inv_sqrt5 = 1.0 / math.sqrt(5)
        
        # Vectors based on direction
        if self.direction == 0:  # Top corner
            u1 = (-2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, -1 * inv_sqrt5)
        elif self.direction == 1:  # Right corner
            u1 = (2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, 1 * inv_sqrt5)
        elif self.direction == 2:  # Bottom corner
            u1 = (-2 * inv_sqrt5, 1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, 1 * inv_sqrt5)
        else:  # 3: Left corner
            u1 = (-2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (-2 * inv_sqrt5, 1 * inv_sqrt5)
            
        R_curve = 85 if self.direction in (1, 3) else 60
        L = 100
        
        pts = []
        # 1. Straight segment 1
        for i in range(6):
            t = i / 5.0
            dist = L - t * (L - R_curve)
            pts.append((cx + dist * u1[0], cy + dist * u1[1]))
            
        # 2. Bezier curve
        B0 = (cx + R_curve * u1[0], cy + R_curve * u1[1])
        B1 = (cx, cy)
        B2 = (cx + R_curve * u2[0], cy + R_curve * u2[1])
        N_curve = 20
        for i in range(1, N_curve + 1):
            t = i / float(N_curve)
            omt = 1.0 - t
            px = omt*omt * B0[0] + 2.0*omt*t * B1[0] + t*t * B2[0]
            py = omt*omt * B0[1] + 2.0*omt*t * B1[1] + t*t * B2[1]
            pts.append((px, py))
            
        # 3. Straight segment 2
        for i in range(1, 6):
            t = i / 5.0
            dist = R_curve + t * (L - R_curve)
            pts.append((cx + dist * u2[0], cy + dist * u2[1]))
            
        return pts

    def render(self, screen, offset_x=0, offset_y=0, camera_x=0, camera_y=0, zoom=1.0):
        ROAD_COLOR = (80, 85, 90)
        BORDER_COLOR = (50, 52, 55)
        LINE_COLOR = (245, 245, 245)
        ROAD_WIDTH = 5
        L = 100
        R_curve = 85 if self.direction in (1, 3) else 60
        
        cx, cy = self.x, self.y
        
        import math
        inv_sqrt5 = 1.0 / math.sqrt(5)
        
        if self.direction == 0:  # Top corner
            u1 = (-2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, -1 * inv_sqrt5)
        elif self.direction == 1:  # Right corner
            u1 = (2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, 1 * inv_sqrt5)
        elif self.direction == 2:  # Bottom corner
            u1 = (-2 * inv_sqrt5, 1 * inv_sqrt5)
            u2 = (2 * inv_sqrt5, 1 * inv_sqrt5)
        else:  # 3: Left corner
            u1 = (-2 * inv_sqrt5, -1 * inv_sqrt5)
            u2 = (-2 * inv_sqrt5, 1 * inv_sqrt5)
            
        # Generate the points with tangents
        pts_with_tangents = []
        
        # 1. Straight segment 1
        T1 = (-u1[0], -u1[1])
        T1_len = math.hypot(T1[0], T1[1])
        T1 = (T1[0]/T1_len, T1[1]/T1_len)
        for i in range(6):
            t = i / 5.0
            dist = L - t * (L - R_curve)
            pt = (cx + dist * u1[0], cy + dist * u1[1])
            pts_with_tangents.append((pt, T1))
            
        # 2. Bezier curve
        B0 = (cx + R_curve * u1[0], cy + R_curve * u1[1])
        B1 = (cx, cy)
        B2 = (cx + R_curve * u2[0], cy + R_curve * u2[1])
        N_curve = 20
        for i in range(1, N_curve + 1):
            t = i / float(N_curve)
            omt = 1.0 - t
            px = omt*omt * B0[0] + 2.0*omt*t * B1[0] + t*t * B2[0]
            py = omt*omt * B0[1] + 2.0*omt*t * B1[1] + t*t * B2[1]
            pt = (px, py)
            
            tx = 2.0 * ((1.0 - t) * (B1[0] - B0[0]) + t * (B2[0] - B1[0]))
            ty = 2.0 * ((1.0 - t) * (B1[1] - B0[1]) + t * (B2[1] - B1[1]))
            t_len = math.hypot(tx, ty)
            if t_len > 0:
                T = (tx/t_len, ty/t_len)
            else:
                T = T1
            pts_with_tangents.append((pt, T))
            
        # 3. Straight segment 2
        T2 = (u2[0], u2[1])
        T2_len = math.hypot(T2[0], T2[1])
        T2 = (T2[0]/T2_len, T2[1]/T2_len)
        for i in range(1, 6):
            t = i / 5.0
            dist = R_curve + t * (L - R_curve)
            pt = (cx + dist * u2[0], cy + dist * u2[1])
            pts_with_tangents.append((pt, T2))
            
        # Snapped normal for Segment 1
        T1 = (-u1[0], -u1[1])
        T1_len = math.hypot(T1[0], T1[1])
        T1 = (T1[0]/T1_len, T1[1]/T1_len)
        nx1, ny1 = -T1[1], T1[0]
        cos_A1 = abs(T1[0] * (2.0 * inv_sqrt5) + T1[1] * (1.0 * inv_sqrt5))
        cos_B1 = abs(T1[0] * (-2.0 * inv_sqrt5) + T1[1] * (1.0 * inv_sqrt5))
        if cos_A1 > cos_B1:
            dot = nx1 * (-2.0 * inv_sqrt5) + ny1 * (1.0 * inv_sqrt5)
            N1_snapped = ((-2.0 * inv_sqrt5) / dot, (1.0 * inv_sqrt5) / dot) if abs(dot) > 0.01 else (nx1, ny1)
        else:
            dot = nx1 * (2.0 * inv_sqrt5) + ny1 * (1.0 * inv_sqrt5)
            N1_snapped = ((2.0 * inv_sqrt5) / dot, (1.0 * inv_sqrt5) / dot) if abs(dot) > 0.01 else (nx1, ny1)
            
        # Snapped normal for Segment 2
        T2 = (u2[0], u2[1])
        T2_len = math.hypot(T2[0], T2[1])
        T2 = (T2[0]/T2_len, T2[1]/T2_len)
        nx2, ny2 = -T2[1], T2[0]
        cos_A2 = abs(T2[0] * (2.0 * inv_sqrt5) + T2[1] * (1.0 * inv_sqrt5))
        cos_B2 = abs(T2[0] * (-2.0 * inv_sqrt5) + T2[1] * (1.0 * inv_sqrt5))
        if cos_A2 > cos_B2:
            dot = nx2 * (-2.0 * inv_sqrt5) + ny2 * (1.0 * inv_sqrt5)
            N2_snapped = ((-2.0 * inv_sqrt5) / dot, (1.0 * inv_sqrt5) / dot) if abs(dot) > 0.01 else (nx2, ny2)
        else:
            dot = nx2 * (2.0 * inv_sqrt5) + ny2 * (1.0 * inv_sqrt5)
            N2_snapped = ((2.0 * inv_sqrt5) / dot, (1.0 * inv_sqrt5) / dot) if abs(dot) > 0.01 else (nx2, ny2)
            
        # Offset to get borders
        inner_pts = []
        outer_pts = []
        total_pts = len(pts_with_tangents)
        for idx in range(total_pts):
            pt, T = pts_with_tangents[idx]
            if idx <= 5:
                nx, ny = N1_snapped
            elif idx >= 26:
                nx, ny = N2_snapped
            else:
                t_ratio = (idx - 5) / 21.0
                nx_raw = (1.0 - t_ratio) * N1_snapped[0] + t_ratio * N2_snapped[0]
                ny_raw = (1.0 - t_ratio) * N1_snapped[1] + t_ratio * N2_snapped[1]
                h = math.hypot(nx_raw, ny_raw)
                if h > 0.001:
                    nx_unit = nx_raw / h
                    ny_unit = ny_raw / h
                else:
                    nx_unit, ny_unit = nx_raw, ny_raw
                    
                L1 = math.hypot(N1_snapped[0], N1_snapped[1])
                L2 = math.hypot(N2_snapped[0], N2_snapped[1])
                if t_ratio < 0.5:
                    u = t_ratio / 0.5
                    s = (1.0 - u) * L1 + u * 1.0
                else:
                    u = (t_ratio - 0.5) / 0.5
                    s = (1.0 - u) * 1.0 + u * L2
                    
                nx = nx_unit * s
                ny = ny_unit * s
            
            scr_pt_x = (pt[0] - camera_x) * zoom + offset_x
            scr_pt_y = (pt[1] - camera_y) * zoom + offset_y
            road_w_scaled = ROAD_WIDTH * zoom
            inner_pts.append((scr_pt_x - road_w_scaled * nx, scr_pt_y - road_w_scaled * ny))
            outer_pts.append((scr_pt_x + road_w_scaled * nx, scr_pt_y + road_w_scaled * ny))
            
        full_poly = inner_pts + list(reversed(outer_pts))
        
        # Render road surface
        pygame.draw.polygon(screen, ROAD_COLOR, full_poly)
        pygame.draw.aalines(screen, BORDER_COLOR, False, inner_pts)
        pygame.draw.aalines(screen, BORDER_COLOR, False, outer_pts)
        
        # Draw dashed centerline along the curve
        centerline_pts = [pt for pt, T in pts_with_tangents]
        dists = [0.0]
        for i in range(1, len(centerline_pts)):
            p1 = centerline_pts[i-1]
            p2 = centerline_pts[i]
            dists.append(dists[-1] + math.hypot(p2[0]-p1[0], p2[1]-p1[1]))
            
        total_len = dists[-1]
        dash_len = 15 * zoom
        gap_len = 15 * zoom
        period = dash_len + gap_len
        
        def get_pt_at_dist(target_d):
            if target_d <= 0:
                return centerline_pts[0]
            if target_d >= total_len:
                return centerline_pts[-1]
            for idx in range(len(dists) - 1):
                if dists[idx] <= target_d <= dists[idx+1]:
                    t_ratio = (target_d - dists[idx]) / (dists[idx+1] - dists[idx])
                    x = centerline_pts[idx][0] + t_ratio * (centerline_pts[idx+1][0] - centerline_pts[idx][0])
                    y = centerline_pts[idx][1] + t_ratio * (centerline_pts[idx+1][1] - centerline_pts[idx][1])
                    return (x, y)
            return centerline_pts[-1]
            
        num_dashes = int(total_len / period) + 1
        for i in range(num_dashes):
            d_start = i * period
            d_end = min(d_start + dash_len, total_len)
            if d_start < total_len:
                p1 = get_pt_at_dist(d_start)
                p2 = get_pt_at_dist(d_end)
                p1_scr = ((p1[0] - camera_x) * zoom + offset_x, (p1[1] - camera_y) * zoom + offset_y)
                p2_scr = ((p2[0] - camera_x) * zoom + offset_x, (p2[1] - camera_y) * zoom + offset_y)
                pygame.draw.line(screen, LINE_COLOR, p1_scr, p2_scr, max(1, int(3 * zoom)))
                
        if self.selected:
            pygame.draw.polygon(screen, (0, 255, 255), full_poly, 2)

    def check_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y):
        scr_x = (self.x - camera_x) * zoom + offset_x
        scr_y = (self.y - camera_y) * zoom + offset_y
        rx = 100 * zoom  # Approx road corner radius click range
        ry = 50 * zoom
        return ((mouse_pos[0] - scr_x) / rx) ** 2 + ((mouse_pos[1] - scr_y) / ry) ** 2 <= 1.00
