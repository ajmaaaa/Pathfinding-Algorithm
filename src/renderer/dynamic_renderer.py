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

    def draw_car(self, x, y, angle):
        sc = self.cam.zoom
        if sc < 0.08: return
        sx, sy = self._ws(x, y)
        length = RW * 1.3 * sc
        width = RW * 0.7 * sc

        # Vektor maju (forward) dan kanan (right) yang ditransformasikan secara isometrik 3D
        cos_phi = math.cos(angle)
        sin_phi = math.sin(angle)
        
        fx_u = (cos_phi - sin_phi) * 1.6
        fy_u = (cos_phi + sin_phi) * 0.8
        rx_u = (-sin_phi - cos_phi) * 1.6
        ry_u = (-sin_phi + cos_phi) * 0.8
        
        # Gunakan divisor konstan (panjang proyeksi sumbu utama) agar proporsi 3D mobil
        # tetap konstan dan tidak terdistorsi (berubah bentuk/dimensi) saat berputar
        D = 1.788854  # math.sqrt(1.6**2 + 0.8**2)
        fx = fx_u / D
        fy = fy_u / D
        rx = rx_u / D
        ry = ry_u / D

        # Tinggi 3D dalam screen-space (ke atas = arah -y di layar)
        car_h = max(2, width * 0.55)      # tinggi badan mobil
        roof_h = max(1, width * 0.35)     # tambahan tinggi atap di atas badan

        def get_pt(ox, oy, off_x=0, off_y=0):
            px = sx + ox * fx + oy * rx + off_x
            py = sy + ox * fy + oy * ry + off_y
            return (px, py)

        def lift(pt, h):
            """Angkat titik ke atas (screen-space up) sebesar h piksel."""
            return (pt[0], pt[1] - h)

        def project_pt(lx, ly, lz):
            return lift(get_pt(lx, ly), lz)

        hl, hw = length / 2, width / 2

        # --- Bayangan Aerodinamis (Mengikuti bentuk bawah mobil yang melengkung) ---
        sh_off = max(1, 3 * sc)
        sh_pts = [
            get_pt(hl, hw * 0.55, sh_off, sh_off),
            get_pt(hl * 0.5, hw * 0.95, sh_off, sh_off),
            get_pt(0, hw, sh_off, sh_off),
            get_pt(-hl * 0.5, hw * 0.95, sh_off, sh_off),
            get_pt(-hl, hw * 0.6, sh_off, sh_off),
            get_pt(-hl, -hw * 0.6, sh_off, sh_off),
            get_pt(-hl * 0.5, -hw * 0.95, sh_off, sh_off),
            get_pt(0, -hw, sh_off, sh_off),
            get_pt(hl * 0.5, -hw * 0.95, sh_off, sh_off),
            get_pt(hl, -hw * 0.55, sh_off, sh_off)
        ]
        pygame.draw.polygon(self.screen, (0, 0, 0, 80), sh_pts)

        # === Model 3D Mobil Retro Coupe Sesuai Gambar ===
        # Ukuran ban ditetapkan lebih awal agar bisa dipakai untuk ride_h
        tire_r = max(2, int(hw * 0.35))
        # Ground clearance: bodi sedikit lebih tinggi dari roda
        ride_h = tire_r * 0.5

        # 1. Bumper Depan (Front Bumper) - lx = hl
        V_front_bl = (hl, hw, ride_h)
        V_front_br = (hl, -hw, ride_h)
        V_front_tl = (hl, hw, ride_h + car_h * 0.55)
        V_front_tr = (hl, -hw, ride_h + car_h * 0.55)
        
        # 2. Pangkal Kaca Depan (Windshield Base) - lx = hl * 0.3
        V_hood_l = (hl * 0.3, hw, ride_h + car_h)
        V_hood_r = (hl * 0.3, -hw, ride_h + car_h)
        
        # 3. Tengah Body (Mid Body) - lx = 0
        V_mid_bl = (0, hw, ride_h)
        V_mid_br = (0, -hw, ride_h)
        V_mid_tl = (0, hw, ride_h + car_h)
        V_mid_tr = (0, -hw, ride_h + car_h)
        
        # 4. Pangkal Kaca Belakang (Rear Window Base) - lx = -hl * 0.5
        V_trunk_l = (-hl * 0.5, hw, ride_h + car_h)
        V_trunk_r = (-hl * 0.5, -hw, ride_h + car_h)
        
        # 5. Bumper Belakang (Rear Bumper) - lx = -hl
        V_rear_bl = (-hl, hw, ride_h)
        V_rear_br = (-hl, -hw, ride_h)
        V_rear_tl = (-hl, hw, ride_h + car_h * 0.55)
        V_rear_tr = (-hl, -hw, ride_h + car_h * 0.55)
        
        # 6. Cabin base
        V_cb_fl = (hl * 0.3, hw * 0.8, ride_h + car_h)
        V_cb_fr = (hl * 0.3, -hw * 0.8, ride_h + car_h)
        V_cb_bl = (-hl * 0.5, hw * 0.8, ride_h + car_h)
        V_cb_br = (-hl * 0.5, -hw * 0.8, ride_h + car_h)
        
        # 7. Cabin top
        V_ct_fl = (hl * 0.1, hw * 0.7, ride_h + car_h + roof_h)
        V_ct_fr = (hl * 0.1, -hw * 0.7, ride_h + car_h + roof_h)
        V_ct_bl = (-hl * 0.35, hw * 0.7, ride_h + car_h + roof_h)
        V_ct_br = (-hl * 0.35, -hw * 0.7, ride_h + car_h + roof_h)

        # Warna dasar mobil (merah cerah cherry seperti gambar)
        C_BODY = (200, 20, 50)
        
        # List elemen renderable
        faces = []
        
        def add_body_face(pts, normal):
            faces.append({
                'type': 'poly',
                'pts': pts,
                'normal': normal,
                'base_color': C_BODY,
                'outline_color': (60, 0, 15)
            })
            
        def add_window_face(pts, normal):
            faces.append({
                'type': 'poly',
                'pts': pts,
                'normal': normal,
                'base_color': (145, 205, 230),
                'outline_color': (80, 140, 170)
            })

        # --- Mendefinisikan Sisi Body (Sesuai Gambar 1 & 2) ---
        # 1. Bumper Depan (Front Bumper Face)
        add_body_face([V_front_br, V_front_bl, V_front_tl, V_front_tr], (1.0, 0.0, 0.0))
        # 2. Kap Depan (Hood Face)
        add_body_face([V_front_tl, V_front_tr, V_hood_r, V_hood_l], (0.5, 0.0, 0.86))
        # 3. Bagian Atap Body (Mid Top)
        add_body_face([V_hood_l, V_hood_r, V_trunk_r, V_trunk_l], (0.0, 0.0, 1.0))
        # 4. Kap Belakang (Trunk Face)
        add_body_face([V_trunk_l, V_trunk_r, V_rear_tr, V_rear_tl], (-0.5, 0.0, 0.86))
        # 5. Bumper Belakang (Rear Bumper Face)
        add_body_face([V_rear_bl, V_rear_br, V_rear_tr, V_rear_tl], (-1.0, 0.0, 0.0))
        
        # --- Sisi Kiri Body (Terbagi 2 Panel dengan Garis Tengah Sesuai Gambar 1) ---
        add_body_face([V_front_bl, V_mid_bl, V_mid_tl, V_hood_l, V_front_tl], (0.0, 1.0, 0.0))
        add_body_face([V_mid_bl, V_rear_bl, V_rear_tl, V_trunk_l, V_mid_tl], (0.0, 1.0, 0.0))
        
        # --- Sisi Kanan Body (Terbagi 2 Panel) ---
        add_body_face([V_front_br, V_mid_br, V_mid_tr, V_hood_r, V_front_tr], (0.0, -1.0, 0.0))
        add_body_face([V_mid_br, V_rear_br, V_rear_tr, V_trunk_r, V_mid_tr], (0.0, -1.0, 0.0))
        
        # --- Kabin (Kaca/Windshield & Atap) ---
        # Windshield depan
        add_window_face([V_cb_fl, V_cb_fr, V_ct_fr, V_ct_fl], (0.6, 0.0, 0.8))
        # Kaca belakang
        add_window_face([V_cb_bl, V_cb_br, V_ct_br, V_ct_bl], (-0.6, 0.0, 0.8))
        # Kaca kiri
        add_window_face([V_cb_fl, V_cb_bl, V_ct_bl, V_ct_fl], (0.0, 1.0, 0.0))
        # Kaca kanan
        add_window_face([V_cb_fr, V_cb_br, V_ct_br, V_ct_fr], (0.0, -1.0, 0.0))
        # Atap kabin (warna bodi)
        add_body_face([V_ct_fl, V_ct_fr, V_ct_br, V_ct_bl], (0.0, 0.0, 1.0))

        # === Ruang Roda (Wheel Wells / Wheel Arches) ===
        # Setengah lingkaran gelap di sisi bodi sebagai cekungan tempat roda masuk
        def add_wheel_well(wx, wy, wz, normal):
            arch_r = tire_r * 1.2
            pts = []
            # Titik kiri bawah arch
            pts.append((wx + arch_r, wy, ride_h))
            # Titik-titik busur (setengah lingkaran dari kiri ke kanan, dari bawah ke atas)
            arch_steps = 6
            for k in range(arch_steps + 1):
                theta = math.pi * k / arch_steps
                ax = wx + arch_r * math.cos(theta)
                az = wz + arch_r * math.sin(theta)
                pts.append((ax, wy, az))
            # Titik kanan bawah arch
            pts.append((wx - arch_r, wy, ride_h))
            
            faces.append({
                'type': 'poly',
                'pts': pts,
                'normal': normal,
                'base_color': (20, 20, 20),
                'outline_color': (10, 10, 10)
            })

        # Wheel wells untuk keempat roda (kiri dan kanan)
        ww_lx_f  = hl * 0.5   # posisi depan
        ww_lx_r  = -hl * 0.5  # posisi belakang
        ww_wz    = tire_r * 0.95  # tinggi pusat roda
        add_wheel_well(ww_lx_f, hw,  ww_wz, (0.0, 1.0, 0.0))    # FL kiri
        add_wheel_well(ww_lx_f, -hw, ww_wz, (0.0, -1.0, 0.0))   # FR kanan
        add_wheel_well(ww_lx_r, hw,  ww_wz, (0.0, 1.0, 0.0))    # BL kiri
        add_wheel_well(ww_lx_r, -hw, ww_wz, (0.0, -1.0, 0.0))   # BR kanan

        # === Ban (Empat Sudut, Tersusun di Kedalaman yang Tepat) ===
        # tire_r sudah ditetapkan di awal
        tire_h = max(1, int(car_h * 0.45))
        
        def add_wheel(center, name):
            faces.append({
                'type': 'wheel',
                'center': center,
                'tire_r': tire_r,
                'tire_h': tire_h,
                'name': name
            })
            
        # Posisi roda seimbang menggelinding di tanah
        add_wheel((hl * 0.5, hw * 1.05, tire_r * 0.95), 'FL')
        add_wheel((hl * 0.5, -hw * 1.05, tire_r * 0.95), 'FR')
        add_wheel((-hl * 0.5, hw * 1.05, tire_r * 0.95), 'BL')
        add_wheel((-hl * 0.5, -hw * 1.05, tire_r * 0.95), 'BR')

        # === Lampu Depan & Belakang ===
        def add_light(center, color, name):
            faces.append({
                'type': 'light',
                'center': center,
                'color': color,
                'name': name
            })
            
        # Lampu Depan (Kuning) - digeser ride_h agar sejajar dengan bumper
        add_light((hl, hw * 0.52, ride_h + car_h * 0.28), (253, 224, 71), 'HL_L')
        add_light((hl, -hw * 0.52, ride_h + car_h * 0.28), (253, 224, 71), 'HL_R')
        # Lampu Belakang (Merah Bulat)
        add_light((-hl, hw * 0.55, ride_h + car_h * 0.28), (239, 68, 68), 'TL_L')
        add_light((-hl, -hw * 0.55, ride_h + car_h * 0.28), (239, 68, 68), 'TL_R')

        # === Perhitungan Pencahayaan Matahari Dinamis (3D Shading) ===
        l_len = math.hypot(0.5, math.hypot(-0.5, 0.8))
        lw_x, lw_y, lw_z = 0.5 / l_len, -0.5 / l_len, 0.8 / l_len
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        ll_x = lw_x * cos_a + lw_y * sin_a
        ll_y = -lw_x * sin_a + lw_y * cos_a
        ll_z = lw_z

        # === Pengurutan Kedalaman (Painter's Algorithm) ===
        def get_face_depth(face):
            if face['type'] == 'poly':
                base_depth = sum(get_pt(pt[0], pt[1])[1] for pt in face['pts']) / len(face['pts'])
                height_contrib = sum(pt[2] for pt in face['pts']) / len(face['pts']) * 1.5
                return base_depth + height_contrib
            elif face['type'] in ('wheel', 'light'):
                c = face['center']
                depth = get_pt(c[0], c[1])[1] + c[2] * 1.5
                # Tentukan apakah roda/lampu ini berada di sisi kiri atau kanan mobil
                is_left_side = (c[1] > 0)
                is_right_side = (c[1] < 0)
                # Sisi kiri menghadap viewer jika ry > 0, sisi kanan jika ry < 0
                side_faces_viewer = (is_left_side and ry > 0) or (is_right_side and ry < 0)
                if side_faces_viewer:
                    depth += length * 0.55
                return depth
            return 0

        sorted_faces = sorted(faces, key=get_face_depth)

        # === Menggambar Elemen Sesuai Urutan Kedalaman ===
        outline_w = max(1, int(sc * 0.8))
        for elem in sorted_faces:
            if elem['type'] == 'poly':
                screen_pts = [project_pt(pt[0], pt[1], pt[2]) for pt in elem['pts']]
                
                # Dynamic lighting shading
                dot = elem['normal'][0] * ll_x + elem['normal'][1] * ll_y + elem['normal'][2] * ll_z
                factor = 0.42 + 0.53 * ((dot + 1) / 2)
                
                c = elem['base_color']
                shaded_c = (
                    max(0, min(255, int(c[0] * factor))),
                    max(0, min(255, int(c[1] * factor))),
                    max(0, min(255, int(c[2] * factor)))
                )
                
                # Draw filled polygon
                pygame.draw.polygon(self.screen, shaded_c, screen_pts)
                
                # Draw outline
                out_c = elem['outline_color']
                shaded_out = (
                    max(0, min(255, int(out_c[0] * factor))),
                    max(0, min(255, int(out_c[1] * factor))),
                    max(0, min(255, int(out_c[2] * factor)))
                )
                pygame.draw.polygon(self.screen, shaded_out, screen_pts, outline_w)
                
            elif elem['type'] == 'wheel':
                c = elem['center']
                cx, cy = project_pt(c[0], c[1], c[2])
                t_r = elem['tire_r']
                # Tebal ban
                t_w = max(2, int(t_r * 0.45))
                
                # Arah pergeseran ke dalam (axle)
                if c[1] > 0:  # Kiri
                    shift_x = -rx * t_w
                    shift_y = -ry * t_w
                else:         # Kanan
                    shift_x = rx * t_w
                    shift_y = ry * t_w
                    
                # Bangun titik lingkaran terluar dan terdalam (berorientasi vertikal sejajar body)
                steps = 12
                outer_pts = []
                inner_pts = []
                for i in range(steps):
                    theta = 2 * math.pi * i / steps
                    dx = t_r * math.cos(theta) * fx
                    dy = t_r * math.cos(theta) * fy - t_r * math.sin(theta)
                    outer_pts.append((cx + dx, cy + dy))
                    inner_pts.append((cx + dx + shift_x, cy + dy + shift_y))
                    
                # 1. Gambar tapak ban (tread quads - selang-seling warna agar bertekstur/alur garis-garis)
                for i in range(steps):
                    next_i = (i + 1) % steps
                    quad = [outer_pts[i], outer_pts[next_i], inner_pts[next_i], inner_pts[i]]
                    tread_c = (20, 20, 20) if i % 2 == 0 else (38, 38, 38)
                    pygame.draw.polygon(self.screen, tread_c, quad)
                    
                # 2. Gambar dinding ban luar (outer face)
                pygame.draw.polygon(self.screen, (42, 42, 42), outer_pts)
                
                # 3. Gambar velg perak (rim)
                rim_pts = []
                rim_r = t_r * 0.58
                for i in range(steps):
                    theta = 2 * math.pi * i / steps
                    dx = rim_r * math.cos(theta) * fx
                    dy = rim_r * math.cos(theta) * fy - rim_r * math.sin(theta)
                    rim_pts.append((cx + dx, cy + dy))
                pygame.draw.polygon(self.screen, (200, 200, 200), rim_pts)
                
                # Gambar 8 lubang melingkar pada velg (Sesuai Gambar 1 & 2)
                hole_r = rim_r * 0.65
                hole_rad = max(0.8, 1.2 * sc)
                for j in range(8):
                    phi = 2 * math.pi * j / 8
                    hx = cx + hole_r * math.cos(phi) * fx
                    hy = cy + hole_r * math.cos(phi) * fy - hole_r * math.sin(phi)
                    pygame.draw.circle(self.screen, (60, 60, 60), (int(hx), int(hy)), int(hole_rad))
                
                # 4. Gambar dop tengah (center cap)
                cap_pts = []
                cap_r = t_r * 0.2
                for i in range(steps):
                    theta = 2 * math.pi * i / steps
                    dx = cap_r * math.cos(theta) * fx
                    dy = cap_r * math.cos(theta) * fy - cap_r * math.sin(theta)
                    cap_pts.append((cx + dx, cy + dy))
                pygame.draw.polygon(self.screen, (50, 50, 50), cap_pts)
                
                # 5. Outline untuk detail tajam
                pygame.draw.polygon(self.screen, (10, 10, 10), outer_pts, 1)
                pygame.draw.polygon(self.screen, (100, 100, 100), rim_pts, 1)
                
            elif elem['type'] == 'light':
                c = elem['center']
                cx, cy = project_pt(c[0], c[1], c[2])
                rad = max(1.5, 2.5 * sc)
                
                pygame.draw.circle(self.screen, elem['color'], (int(cx), int(cy)), int(rad))
                pygame.draw.circle(self.screen, (0, 0, 0), (int(cx), int(cy)), int(rad), 1)

    def get_car_transform(self, path_edges, progress):
        if not path_edges or progress <= 0 or progress < path_edges[0]['start']:
            self.car_last_prog = progress
            self._angle_initialized = False
            self.car_last_x = None
            self.car_last_y = None
            return None, None, None

        car_x, car_y = get_smooth_path_coord(path_edges, progress)
        if car_x is None:
            return None, None, None

        # Find current segment index and its speed
        idx = 0
        for i, pe in enumerate(path_edges):
            if pe['start'] <= progress <= pe['end']:
                idx = i
                break
        
        current_pe = path_edges[idx]
        from src.core.geometry import polyline_length
        pe_len = polyline_length(current_pe['curve'])
        pe_dur = current_pe['end'] - current_pe['start']
        
        if pe_dur > 0.0001:
            speed_px_per_prog = pe_len / pe_dur
        else:
            speed_px_per_prog = 24.0
            
        # Target physical lookahead (in pixels)
        # Closer lookaheads for tighter cornering and accurate centerline tracking.
        lookahead_dists = [8.0, 20.0, 35.0]
        dx_acc, dy_acc = 0.0, 0.0
        weight_total = 0.0
        
        for dist_la, w in zip(lookahead_dists, [1.0, 0.6, 0.3]):
            # Convert physical lookahead distance to progress unit lookahead
            la = dist_la / max(1.0, speed_px_per_prog)
            nx, ny = get_smooth_path_coord(path_edges, progress + la)
            if nx is not None:
                dx_acc += (nx - car_x) * w
                dy_acc += (ny - car_y) * w
                weight_total += w

        if weight_total > 0 and (abs(dx_acc) > 0.001 or abs(dy_acc) > 0.001):
            dx = dx_acc / weight_total
            dy = dy_acc / weight_total
            # Convert isometric screen-space direction → 3D world-space angle
            dx_3d = 0.5 * (dx / 1.6 + dy / 0.8)
            dy_3d = 0.5 * (dy / 0.8 - dx / 1.6)
            self.car_target_angle = math.atan2(dy_3d, dx_3d)

        # ── Smooth angular interpolation (shortest arc) ─────────────────────
        if not self._angle_initialized or self.car_last_x is None:
            self.car_smooth_angle = self.car_target_angle
            self._angle_initialized = True
        else:
            # Calculate physical distance traveled in this frame
            dx_pos = car_x - self.car_last_x
            dy_pos = car_y - self.car_last_y
            ds = math.hypot(dx_pos, dy_pos)
            
            # Find shortest angular distance (handles ±π wrap-around)
            delta = self.car_target_angle - self.car_smooth_angle
            delta = (delta + math.pi) % (2 * math.pi) - math.pi
            
            # Distance-based smoothing factor
            # Less drift at high speed, smooth turning at low speed
            # Lower distance constant = faster steering alignment (less drift)
            distance_constant = 1.0
            smooth = 1.0 - math.exp(-ds / distance_constant)
            smooth = max(0.18, min(0.9, smooth))
            
            self.car_smooth_angle += delta * smooth

        self.car_angle = self.car_smooth_angle
        self.car_last_prog = progress
        self.car_last_x = car_x
        self.car_last_y = car_y
        return car_x, car_y, self.car_angle

    def draw_anim_layer_ground(self, nodes, search_edges, path_edges, progress):
        ribbon_h = self.screen.get_height() - self.H
        sc = self.cam.zoom
        ov = pygame.Surface((self.W, self.H + ribbon_h), pygame.SRCALPHA)
        
        for se in search_edges:
            if progress >= se['start']:
                p = (progress - se['start']) / (se['end'] - se['start'])
                p = max(0, min(1, p))
                is_eval = progress >= se['target'].eval_step
                if se['is_optimal']:
                    color = (59, 130, 246, 178) if is_eval else (46, 204, 113, 153)
                    lw = max(2, int(RW * 0.4 * sc))
                else:
                    color = (239, 68, 68, 102); lw = max(1, int(RW * 0.25 * sc))
                
                curve = self._curve_until(se.get('curve'), p)
                if not curve:
                    cur_x = se['from'].x + (se['to'].x - se['from'].x) * p
                    cur_y = se['from'].y + (se['to'].y - se['from'].y) * p
                    curve = [(se['from'].x, se['from'].y), (cur_x, cur_y)]
                self._draw_curve(ov, curve, color, lw)

        for n in nodes:
            if getattr(n, 'is_roundabout', False):
                # Draw a node at each road junction on the roundabout
                is_eval = n.eval_step <= progress; is_disc = n.disc_step <= progress
                if is_eval or is_disc:
                    for e in n.edges:
                        nb = e[1] if e[0] is n else e[0]
                        L = math.hypot(nb.x - n.x, nb.y - n.y)
                        if L > 0.0001:
                            ux = (nb.x - n.x) / L
                            uy = (nb.y - n.y) / L
                            jx = n.x + ux * 140.25
                            jy = n.y + uy * 140.25
                            sx, sy = self._ws(jx, jy)
                            if sx < 0 or sx > self.W or sy < ribbon_h or sy > self.H + ribbon_h: continue
                            if is_eval:
                                pygame.draw.circle(ov, (59, 130, 246, 230), (sx, sy), max(2, int(RW*.35*sc)))
                            elif is_disc:
                                p = (progress - n.disc_step) / 0.5; p = max(0, min(1, p))
                                if p > 0:
                                    pygame.draw.circle(ov, (46, 204, 113, 230), (sx, sy), max(2, int(RW*.4*p*sc)))
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
            is_eval = n.eval_step <= progress; is_disc = n.disc_step <= progress
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < ribbon_h or sy > self.H + ribbon_h: continue
            if is_eval: pygame.draw.circle(ov, (59, 130, 246, 230), (sx, sy), max(2, int(RW*.35*sc)))
            elif is_disc:
                p = (progress - n.disc_step) / 0.5; p = max(0, min(1, p))
                if p > 0: pygame.draw.circle(ov, (46, 204, 113, 230), (sx, sy), max(2, int(RW*.4*p*sc)))

        for pe in path_edges:
            if progress >= pe['start']:
                p = (progress - pe['start']) / (pe['end'] - pe['start'])
                p = max(0, min(1, p))
                w1 = max(4, int(RW*.9*sc)); w2 = max(3, int(RW*.55*sc)); w3 = max(2, int(RW*.38*sc))
                curve = self._curve_until(pe.get('curve'), p)
                if not curve:
                    cur_x = pe['from'].x + (pe['to'].x - pe['from'].x) * p
                    cur_y = pe['from'].y + (pe['to'].y - pe['from'].y) * p
                    curve = [(pe['from'].x, pe['from'].y), (cur_x, cur_y)]

                self._draw_curve(ov, curve, (251, 191, 36, 64), w1)
                self._draw_curve(ov, curve, (0, 0, 0, 64), w2)
                self._draw_curve(self.screen, curve, (246, 173, 85), w3)
                self._draw_curve(ov, curve, (255, 255, 255, 140), max(1, int(RW*.09*sc)))

        self.screen.blit(ov, (0, 0))