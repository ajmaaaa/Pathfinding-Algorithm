import pygame
import random
import math
from config import C, RW
from src.ui.hud import get_font

class ElseRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.decorations = []

        # struktur folder nya di ubah 
        self.cat_img = pygame.image.load('assets/cat.png').convert_alpha() 

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def generate_decorations(self, city):  # --- ini tambahan auriel ---
        """Menghasilkan koordinat dekorasi dengan Algoritma Spatial Clearance Optimal"""
        self.decorations = []
        if not city or 'nodes' not in city: return
        
        nodes = city['nodes']
        edges = city.get('edges', [])
        buildings = city.get('buildings', [])
        roundabouts = city.get('roundabouts', [])
        
        # Fungsi pembantu untuk Sensor Jalan (Distance from Point to Line Segment)
        def dist_to_segment(px, py, ax, ay, bx, by):
            l2 = (bx - ax)**2 + (by - ay)**2
            if l2 == 0: return math.hypot(px - ax, py - ay)
            t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2))
            proj_x = ax + t * (bx - ax)
            proj_y = ay + t * (by - ay)
            return math.hypot(px - proj_x, py - proj_y)

        # --- 1. FITUR KHUSUS: PASTI MUNCUL DI TENGAH BUNDARAN ---
        for rb in roundabouts:
            dec_type = random.choice(['flower_patch', 'cat'])
            if dec_type == 'flower_patch':
                color = random.choice([(231, 76, 60), (255, 119, 255), (155, 89, 182)])
                patch = []
                offsets = [(0, 0), (-6, -6), (6, -4), (-4, 6)] 
                for i in range(random.randint(2, 4)):
                    ox, oy = offsets[i]
                    patch.append({'wx': rb.x + ox, 'wy': rb.y + oy})
                self.decorations.append({
                    'type': 'flower_patch', 'wx': rb.x, 'wy': rb.y,
                    'patch': patch, 'color': color
                })
            elif dec_type == 'cat':
                self.decorations.append({'type': 'cat', 'wx': rb.x, 'wy': rb.y})

        # --- 2. PENYEBARAN DI RUANG HIJAU ---
        TREE_COLORS = [
            (56, 142, 60), (46, 125, 50), (76, 175, 80),
            (33, 113, 41), (102, 187, 106), (27, 94, 32),
        ]
        ROCK_COLORS = [
            (120, 120, 115), (140, 135, 128), (105, 100, 95),
            (158, 152, 140), (96, 110, 102),
        ]

        attempts = 0
        while len(self.decorations) < 80 and attempts < 3000:
            attempts += 1
            base_node = random.choice(nodes)
            radius = random.uniform(50, 250)
            angle  = random.uniform(0, math.pi * 2)
            bx = base_node.x + math.cos(angle) * radius
            by = base_node.y + math.sin(angle) * radius

            aman = True

            # Sensor Jalan
            for e in edges:
                n1, n2 = e[0], e[1]
                if dist_to_segment(bx, by, n1.x, n1.y, n2.x, n2.y) < 55:
                    aman = False; break
            if not aman: continue

            # Sensor Persimpangan
            for n in nodes:
                if math.hypot(bx - n.x, by - n.y) < 65:
                    aman = False; break
            if not aman: continue

            # Sensor Bangunan
            for b in buildings:
                if math.hypot(bx - b['x'], by - b['y']) < 120 * b['scale']:
                    aman = False; break
            if not aman: continue

            # Sensor Dekorasi Lain
            for dec in self.decorations:
                if math.hypot(bx - dec['wx'], by - dec['wy']) < 90:
                    aman = False; break
            if not aman: continue

            # LOLOS SENSOR — pilih tipe dekorasi
            dec_type = random.choices(
                ['flower_patch', 'cat', 'tree', 'rock'],
                weights=[30, 10, 45, 15]
            )[0]

            if dec_type == 'flower_patch':
                color = random.choice([(231, 76, 60), (255, 119, 255), (155, 89, 182)])
                patch = []
                offsets = [(0, 0), (-35, -25), (35, -15), (-15, 35)]
                for i in range(random.randint(2, 4)):
                    ox, oy = offsets[i]
                    patch.append({'wx': bx + ox, 'wy': by + oy})
                self.decorations.append({
                    'type': 'flower_patch', 'wx': bx, 'wy': by,
                    'patch': patch, 'color': color
                })

            elif dec_type == 'cat':
                self.decorations.append({'type': 'cat', 'wx': bx, 'wy': by})

            elif dec_type == 'tree':
                col = random.choice(TREE_COLORS)
                col = tuple(max(0, min(255, c + random.randint(-12, 12))) for c in col)
                self.decorations.append({
                    'type': 'tree', 'wx': bx, 'wy': by,
                    'r': random.uniform(22, 42),
                    'col': col,
                    'seed': random.randint(0, 999999),
                })

            elif dec_type == 'rock':
                base_col = random.choice(ROCK_COLORS)
                stones = []
                for _ in range(random.randint(2, 5)):
                    col_var = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in base_col)
                    stones.append({
                        'ox':   random.uniform(-18, 18),
                        'oy':   random.uniform(-14, 14),
                        'r':    random.uniform(7, 18),
                        'col':  col_var,
                        'seed': random.randint(0, 999999),
                    })
                self.decorations.append({
                    'type': 'rock', 'wx': bx, 'wy': by,
                    'stones': stones,
                })

    # ─────────────────────────────────────────────
    #  RENDER POHON REALISTIS
    # ─────────────────────────────────────────────
    def _draw_tree(self, wx, wy, r_world, col, seed):
        sc = self.cam.zoom
        if sc < 0.06: return

        sx, sy = self._ws(wx, wy)
        W = self.screen.get_width(); H = self.screen.get_height()
        if sx < -150 or sx > W+150 or sy < -150 or sy > H+150: return

        r   = max(6, int(r_world * sc))
        rng = random.Random(seed)
        scr = self.screen

        dark     = tuple(max(0,   c-50) for c in col)
        mid      = col
        light    = tuple(min(255, c+55) for c in col)
        vlight   = tuple(min(255, c+90) for c in col)
        xdark    = tuple(max(0,   c-70) for c in col)
        sun_tint = (min(255, col[0]+30), min(255, col[1]+60), max(0, col[2]-20))

        # 1. Shadow tanah
        sw, sh = int(r*2.0), int(r*0.5)
        if sw >= 4:
            shad = pygame.Surface((sw*2, sh*2), pygame.SRCALPHA)
            pygame.draw.ellipse(shad, (5,30,5,60), (0,0,sw*2,sh*2))
            scr.blit(shad, (int(sx)-sw, int(sy)-sh+int(r*0.3)))

        # 2. Batang
        tw = max(2, int(r*0.22)); th = max(5, int(r*0.65))
        trunk_y = int(sy) + int(r*0.22)
        pygame.draw.rect(scr, (55,33,10),  (int(sx)-tw+max(1,tw//2), trunk_y, tw,          th))
        pygame.draw.rect(scr, (85,54,20),  (int(sx)-tw,              trunk_y, tw*2,         th))
        pygame.draw.rect(scr, (115,78,35), (int(sx)-tw,              trunk_y, max(1,tw//2), th))

        # 3. Base mahkota gelap
        pygame.draw.circle(scr, xdark, (int(sx), int(sy)-int(r*0.05)), int(r*0.92))

        # 4. Cluster daun (7 bola)
        clusters = [
            (0,            -int(r*0.08), int(r*0.88)),
            (-int(r*0.50), -int(r*0.25), int(r*0.70)),
            ( int(r*0.50), -int(r*0.25), int(r*0.70)),
            (0,            -int(r*0.40), int(r*0.78)),
            (-int(r*0.28), -int(r*0.60), int(r*0.60)),
            ( int(r*0.28), -int(r*0.60), int(r*0.60)),
            (0,            -int(r*0.78), int(r*0.50)),
        ]
        for ox, oy, cr in clusters:
            cr   = max(3, cr)
            cx_c = int(sx)+ox; cy_c = int(sy)+oy
            pygame.draw.circle(scr, dark, (cx_c, cy_c), cr)
            pygame.draw.circle(scr, mid,  (cx_c-max(1,cr//5), cy_c-max(1,cr//5)), max(2,int(cr*0.82)))
            for _ in range(5):
                ang = rng.uniform(0, math.pi*2); dr = rng.uniform(cr*0.50, cr*0.85)
                pygame.draw.circle(scr, xdark,
                                   (cx_c+int(math.cos(ang)*dr), cy_c+int(math.sin(ang)*dr)),
                                   max(1, int(cr*0.20)))
            if cr >= 5:
                pygame.draw.circle(scr, light, (cx_c-max(1,cr//4), cy_c-max(1,cr//4)), max(2,int(cr*0.40)))
            if cr >= int(r*0.6) and sc > 0.15:
                pygame.draw.circle(scr, sun_tint, (cx_c-max(1,cr//3), cy_c-max(1,cr//3)), max(1,int(cr*0.20)))

        # 5. Specular
        sr = max(1, int(r*0.16))
        pygame.draw.circle(scr, vlight, (int(sx)-int(r*0.38), int(sy)-int(r*0.58)), sr)
        if sr >= 3:
            pygame.draw.circle(scr, (230,255,210), (int(sx)-int(r*0.38), int(sy)-int(r*0.58)), max(1,sr//2))

    # ─────────────────────────────────────────────
    #  RENDER BATU REALISTIS
    # ─────────────────────────────────────────────
    def _draw_rock(self, wx, wy, stones):
        sc = self.cam.zoom
        if sc < 0.05: return

        scr = self.screen
        W = self.screen.get_width(); H = self.screen.get_height()

        for stone in stones:
            sx, sy = self._ws(wx+stone['ox'], wy+stone['oy'])
            if sx < -80 or sx > W+80 or sy < -80 or sy > H+80: continue

            r   = max(3, int(stone['r']*sc))
            col = stone['col']
            rng = random.Random(stone['seed'])

            dark       = tuple(max(0,   c-45) for c in col)
            light      = tuple(min(255, c+50) for c in col)
            vlight     = tuple(min(255, c+80) for c in col)
            shadow_col = tuple(max(0,   c-65) for c in col)

            # Bayangan tanah
            sw, sh = int(r*1.5), int(r*0.38)
            if sw >= 3:
                shad = pygame.Surface((sw*2,sh*2), pygame.SRCALPHA)
                pygame.draw.ellipse(shad, (10,15,10,50), (0,0,sw*2,sh*2))
                scr.blit(shad, (int(sx)-sw, int(sy)-sh+int(r*0.5)))

            # Polygon batu acak tapi konsisten
            pts = []
            for i in range(rng.randint(5, 8)):
                ang = (i/8)*math.pi*2 + rng.uniform(-0.25, 0.25)
                pts.append((int(sx+math.cos(ang)*r*rng.uniform(0.72,1.0)),
                             int(sy+math.sin(ang)*r*rng.uniform(0.55,0.82))))

            if len(pts) >= 3:
                pygame.draw.polygon(scr, shadow_col, [(p[0]+max(1,r//5), p[1]+max(1,r//5)) for p in pts])
                pygame.draw.polygon(scr, col,  pts)
                pygame.draw.polygon(scr, dark, pts, max(1,r//3))
                pygame.draw.polygon(scr, dark, pts, max(1,int(sc*1.5)))

            if r >= 5:
                hx, hy = int(sx-r*0.28), int(sy-r*0.30)
                pygame.draw.ellipse(scr, light, (hx-max(2,r//3), hy-max(1,r//4), max(3,r//2), max(2,r//3)))
                if r >= 8:
                    pygame.draw.circle(scr, vlight, (int(sx-r*0.32), int(sy-r*0.35)), max(1,r//5))

            if sc > 0.18 and r >= 7:
                crack_col = tuple(max(0,c-55) for c in col)
                for _ in range(rng.randint(1,2)):
                    ang_c = rng.uniform(0, math.pi*2); len_c = rng.uniform(r*0.25, r*0.55)
                    x1c = int(sx+math.cos(ang_c)*r*0.1); y1c = int(sy+math.sin(ang_c)*r*0.1)
                    pygame.draw.line(scr, crack_col,
                                     (x1c, y1c),
                                     (int(x1c+math.cos(ang_c)*len_c), int(y1c+math.sin(ang_c)*len_c)), 1)

    # ─────────────────────────────────────────────
    #  DRAW SEMUA DEKORASI (dengan Y-sort)
    # ─────────────────────────────────────────────
    def draw_decorations(self):
        sc = self.cam.zoom
        if sc < 0.05: return

        W = self.screen.get_width(); H = self.screen.get_height()

        # Y-sort: elemen lebih bawah di layar tampil di depan
        for dec in sorted(self.decorations, key=lambda d: d['wy']):

            if dec['type'] == 'flower_patch':
                for f in dec['patch']:
                    sx, sy = self._ws(f['wx'], f['wy'])
                    if sx < -50 or sx > W+50 or sy < -50 or sy > H+50: continue
                    radius   = max(3, int(8*sc))
                    stem_len = max(8, int(35*sc))
                    flower_y = sy - stem_len
                    pygame.draw.line(self.screen, (27,94,32), (sx,sy), (sx,flower_y), max(2,int(3*sc)))
                    pygame.draw.circle(self.screen, dec['color'], (sx, flower_y-radius), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx, flower_y+radius), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx-radius, flower_y), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx+radius, flower_y), radius)
                    pygame.draw.circle(self.screen, (241,196,15), (sx, flower_y), int(radius*0.8))

            elif dec['type'] == 'cat':
                sx, sy = self._ws(dec['wx'], dec['wy'])
                if sx < -50 or sx > W+50 or sy < -50 or sy > H+50: continue
                scaled_size = max(5, int(50*sc))
                scaled_img  = pygame.transform.smoothscale(self.cat_img, (scaled_size, scaled_size))
                self.screen.blit(scaled_img, scaled_img.get_rect(center=(sx, sy)))

            elif dec['type'] == 'tree':
                self._draw_tree(dec['wx'], dec['wy'], dec['r'], dec['col'], dec['seed'])

            elif dec['type'] == 'rock':
                self._draw_rock(dec['wx'], dec['wy'], dec['stones'])

    def draw_pin(self, n, color, lbl):
        sx, sy = self._ws(n.x, n.y)
        sc = self.cam.zoom
        r  = max(8, int(RW*1.12*sc)); pr = max(4, int(r*0.7))
        ov = pygame.Surface((r*4, r*2), pygame.SRCALPHA)
        pygame.draw.ellipse(ov,(0,0,0,46),(r//2,r//2,r,r//3)); self.screen.blit(ov,(sx-r,sy-r//4))
        pygame.draw.circle(self.screen, color, (sx, sy-int(r*0.6)), pr)
        pygame.draw.circle(self.screen, C['white'], (sx, sy-int(r*0.6)), pr, max(2,int(4*sc)))
        pts = [(sx-int(pr*0.27), sy-int(r*0.6)), (sx+int(pr*0.27), sy-int(r*0.6)), (sx, sy+int(r*0.3))]
        pygame.draw.polygon(self.screen, color, pts)
        if sc > 0.12:
            fnt = get_font(max(8,int(pr*0.65)), bold=True)
            t   = fnt.render(lbl, True, C['white'])
            self.screen.blit(t, (sx-t.get_width()//2, sy-int(r*0.6)-t.get_height()//2))
