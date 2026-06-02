import pygame

# --- VARIABEL GLOBAL UNTUK ROTASI ---
_rotasi_sudut = 0.0
PI = 3.141592653589793

# --- CUSTOM TRIGONOMETRY (Tanpa Import Math) ---
def get_sin_cos(angle_deg):
    rad = angle_deg * PI / 180.0
    twopi = 2.0 * PI
    rad = rad % twopi
    if rad > PI:
        rad -= twopi
    elif rad < -PI:
        rad += twopi
        
    r2 = rad * rad
    r3 = r2 * rad
    r4 = r3 * rad
    r5 = r4 * rad
    r6 = r5 * rad
    r7 = r6 * rad
    r8 = r7 * rad
    r9 = r8 * rad
    
    sin_x = rad - (r3)/6.0 + (r5)/120.0 - (r7)/5040.0 + (r9)/362880.0
    cos_x = 1.0 - (r2)/2.0 + (r4)/24.0 - (r6)/720.0 + (r8)/40320.0
    
    return sin_x, cos_x

def draw_bianglala(screen, cx, cy):
    global _rotasi_sudut
    import time
    _rotasi_sudut = (time.time() * 35.0) % 360.0  # Bergerak dinamis (35 derajat/detik)

    # 1. KONSTANTA DIMENSI BIANGLALA
    R = 120    # Radius Roda
    H = 170    # Tinggi Axle dari Tanah
    W = 18     # Jarak roda depan-belakang (total lebar 36)
    num_spokes = 8
    num_pts = 24

    # 2. PROYEKSI ISOMETRIK (Sumbu X: depan-kanan, Y: belakang-kiri, Z: tinggi)
    def iso(x, y, z):
        sx = cx + (x - y) * 1.6
        sy = cy + (x + y) * 0.8 - z
        return sx, sy

    def draw_poly(pts3, color, outline=True, lw=2, outline_color=(45, 45, 45)):
        pts2 = [iso(x, y, z) for x, y, z in pts3]
        pygame.draw.polygon(screen, color, pts2)
        if outline:
            pygame.draw.polygon(screen, outline_color, pts2, lw)

    def draw_block(x1, x2, y1, y2, z1, z2, ct, cf, cs, outline=True, lw=2):
        # Top Face
        draw_poly([(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)], ct, outline, lw)
        # Left Face
        draw_poly([(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)], cf, outline, lw)
        # Right Face
        draw_poly([(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)], cs, outline, lw)

    def ln(x1,y1,z1, x2,y2,z2, col, w=2):
        pygame.draw.line(screen, col, iso(x1,y1,z1), iso(x2,y2,z2), w)

    def draw_thick_line(x1, y1, z1, x2, y2, z2, col_base, col_lite, w_base, w_lite):
        p1 = iso(x1, y1, z1)
        p2 = iso(x2, y2, z2)
        # Bold Outline
        pygame.draw.line(screen, (45, 45, 45), p1, p2, w_base + 3)
        # Base Color
        pygame.draw.line(screen, col_base, p1, p2, w_base)
        # Highlight Color
        pygame.draw.line(screen, col_lite, p1, p2, w_lite)

    # ==========================================
    # 1. PLAZA UTAMA & ELEMEN DEKORATIF (z = -H)
    # ==========================================
    # Plaza Utama
    draw_poly([(-190, -170, -H), (190, -170, -H), (190, 170, -H), (-190, 170, -H)], (238, 235, 228))

    # Pola Paving Jalan Utama
    draw_poly([(-30, 20, -H), (30, 20, -H), (30, 170, -H), (-30, 170, -H)], (210, 205, 195))
    draw_poly([(-145, 40, -H), (-105, 40, -H), (-105, 115, -H), (-145, 115, -H)], (210, 205, 195))
    draw_poly([(100, -30, -H), (130, -30, -H), (130, 40, -H), (100, 40, -H)], (210, 205, 195))

    # Taman Hijau / Semak Belakang
    draw_poly([(-180, -160, -H), (-40, -160, -H), (-40, -120, -H), (-180, -120, -H)], (76, 140, 64))
    draw_poly([(40, -160, -H), (180, -160, -H), (180, -120, -H), (40, -120, -H)], (76, 140, 64))
    for fx, fy in [
        (-160, -145), (-130, -135), (-100, -145), (-70, -135),
        (70, -145), (100, -135), (130, -145), (160, -135)
    ]:
        pygame.draw.circle(screen, (235, 65, 65), iso(fx, fy, -H+2), 4)
        pygame.draw.circle(screen, (255, 230, 80), iso(fx, fy, -H+2), 2)
        pygame.draw.circle(screen, (255, 230, 80), iso(fx+8, fy+4, -H+2), 3)

    # Pagar Pembatas Kiri
    for py in range(-160, 161, 30):
        ln(-185, py, -H, -185, py, -H+18, (60, 62, 65), 3)
    ln(-185, -160, -H+15, -185, 160, -H+15, (45, 45, 45), 2)

    # Bendera Dekorasi Depan
    ln(-175, 150, -H, -175, 150, -H+55, (170, 175, 180), 3)
    draw_poly([(-175, 150, -H+55), (-150, 150, -H+48), (-175, 150, -H+42)], (65, 115, 235))
    ln(175, 150, -H, 175, 150, -H+55, (170, 175, 180), 3)
    draw_poly([(175, 150, -H+55), (150, 150, -H+48), (175, 150, -H+42)], (245, 195, 35))

    # ==========================================
    # 2. LOKET TIKET (CARNIVAL TICKET KIOSK)
    # ==========================================
    draw_block(-145, -105, 75, 115, -H, -H+48, (245, 245, 245), (215, 215, 215), (195, 195, 195))
    for sx in range(-140, -100, 10):
        draw_poly([(sx, 115, -H), (sx+4, 115, -H), (sx+4, 115, -H+48), (sx, 115, -H+48)], (225, 55, 55), outline=False)
    draw_poly([(-132, 115, -H+16), (-118, 115, -H+16), (-118, 115, -H+34), (-132, 115, -H+34)], (135, 205, 235))
    draw_block(-135, -115, 115, 120, -H+13, -H+16, (245, 185, 45), (195, 135, 20), (175, 115, 15))
    draw_poly([(-145, 75, -H+48), (-105, 75, -H+48), (-125, 95, -H+68)], (250, 200, 50))
    draw_poly([(-105, 75, -H+48), (-105, 115, -H+48), (-125, 95, -H+68)], (210, 160, 30))
    draw_poly([(-105, 115, -H+48), (-145, 115, -H+48), (-125, 95, -H+68)], (210, 160, 30))
    draw_poly([(-145, 115, -H+48), (-145, 75, -H+48), (-125, 95, -H+68)], (250, 200, 50))
    ln(-125, 95, -H+68, -125, 95, -H+82, (120, 120, 120), 2)
    draw_poly([(-125, 95, -H+82), (-112, 95, -H+77), (-125, 95, -H+72)], (225, 55, 55))

    # ==========================================
    # 3. KIOS ES KRIM / FOOD CART
    # ==========================================
    draw_block(100, 135, -60, -25, -H, -H+22, (255, 215, 230), (235, 185, 205), (215, 165, 185))
    pygame.draw.circle(screen, (45, 45, 45), iso(108, -25, -H+6), 7)
    pygame.draw.circle(screen, (245, 185, 45), iso(108, -25, -H+6), 3)
    pygame.draw.circle(screen, (45, 45, 45), iso(127, -25, -H+6), 7)
    pygame.draw.circle(screen, (245, 185, 45), iso(127, -25, -H+6), 3)
    ln(117, -42, -H+22, 117, -42, -H+48, (80, 80, 85), 3)
    draw_poly([(102, -57, -H+48), (132, -57, -H+48), (132, -27, -H+48), (102, -27, -H+48)], (255, 105, 180))
    draw_poly([(108, -51, -H+48), (126, -51, -H+48), (126, -33, -H+48), (108, -33, -H+48)], (255, 255, 255), outline=False)
    ln(117, -42, -H+48, 117, -42, -H+54, (255, 105, 180), 3)

    # ==========================================
    # 3b. BANGKU TAMAN KAYU RAPI DI DEPAN KANAN
    # ==========================================
    # 4 Kaki Penyangga Bangku (Digambar lebih dulu agar ditutupi oleh dudukan/sandaran)
    for lx, ly in [(92, 106), (123, 106), (92, 118), (123, 118)]:
        ln(lx, ly, -H, lx, ly, -H+12, (45, 45, 45), 3)
    # Dudukan Bench (z: -H+12 s.d -H+15)
    draw_block(90, 125, 105, 120, -H+12, -H+15, (170, 115, 75), (135, 90, 55), (115, 75, 45))
    # Sandaran Belakang Bench
    draw_block(90, 125, 102, 105, -H+15, -H+28, (170, 115, 75), (135, 90, 55), (115, 75, 45))

    # ==========================================
    # 4. DOCK PENUMPANG (CENTERED BOARDING PLATFORM)
    # ==========================================
    # Y disempurnakan menjadi [-14 s.d 14] agar muat persis di antara kedua roda (W=18)
    # Z diatur menjadi [-H s.d -H+5] agar memberi ruang bagi gondola yang lewat di atasnya (z=-160)
    draw_block(-55, 55, -14, 14, -H, -H+5, (190, 150, 105), (150, 115, 75), (130, 95, 60))
    # Tangga naik tengah ke arah luar (y = 14 s.d 26)
    draw_block(-20, 20, 14, 26, -H, -H+3, (150, 110, 70), (120, 85, 50), (100, 70, 40))
    
    # Railing keselamatan warna kuning di tepi platform
    ln(-55, -14, -H+5, 55, -14, -H+5, (245, 185, 45), 3) # Belakang
    ln(-55, 14, -H+5, -20, 14, -H+5, (245, 185, 45), 3)  # Depan Kiri
    ln(20, 14, -H+5, 55, 14, -H+5, (245, 185, 45), 3)    # Depan Kanan
    ln(-55, -14, -H+5, -55, 14, -H+5, (245, 185, 45), 3) # Samping Kiri
    ln(55, -14, -H+5, 55, 14, -H+5, (245, 185, 45), 3)   # Samping Kanan
    # Tiang railing keselamatan
    for rx in [-55, -20, 20, 55]:
        ln(rx, 14, -H+5, rx, 14, -H+16, (245, 185, 45), 2)
    for rx in [-55, 55]:
        ln(rx, -14, -H+5, rx, -14, -H+16, (245, 185, 45), 2)

    # ==========================================
    # 5. KAKI PENYANGGA BIANGLALA (SUPPORT LEGS) & RODA BELAKANG (y = -W)
    # ==========================================
    # Kaki Belakang (y = -W) (further away)
    draw_thick_line(-75, -W, -H, 0, -W, 0, (15, 45, 140), (90, 150, 255), 10, 4)
    draw_thick_line(75, -W, -H, 0, -W, 0, (15, 45, 140), (90, 150, 255), 10, 4)

    # Ruji Roda Belakang
    for i in range(num_spokes):
        ang = _rotasi_sudut + i * (360.0 / num_spokes)
        sin_a, cos_a = get_sin_cos(ang)
        ln(0, -W, 0, R * cos_a, -W, R * sin_a, (90, 150, 255), 3)

    # Rim Roda Belakang (Vibrant Blue & Outline)
    back_rim_pts = []
    for i in range(num_pts):
        ang = i * (360.0 / num_pts)
        sin_a, cos_a = get_sin_cos(ang)
        back_rim_pts.append(iso(R * cos_a, -W, R * sin_a))
    pygame.draw.lines(screen, (45, 45, 45), True, back_rim_pts, 14)
    pygame.draw.lines(screen, (15, 45, 140), True, back_rim_pts, 10)
    pygame.draw.lines(screen, (90, 150, 255), True, back_rim_pts, 4)

    # ==========================================
    # 6. POROS TENGAH BIANGLALA 3D (AXLE HUB BLOCK)
    # ==========================================
    draw_block(-4, 4, -W-3, W+3, -4, 4, (140, 145, 150), (115, 120, 125), (95, 100, 105))

    # ==========================================
    # 7. PALANG PENGHUBUNG RODA DEPAN-BELAKANG (CROSSBARS)
    # ==========================================
    for i in range(num_spokes * 2):
        ang = _rotasi_sudut + i * (180.0 / num_spokes)
        sin_a, cos_a = get_sin_cos(ang)
        draw_thick_line(R * cos_a, -W, R * sin_a, R * cos_a, W, R * sin_a, (150, 160, 170), (220, 225, 230), 5, 2)

    # ==========================================
    # 8. GONDOLA / KABIN 3D (DEPTH SORTED & BOTTOM-TO-TOP ORDER)
    # ==========================================
    gondolas = []
    for i in range(num_spokes):
        ang = _rotasi_sudut + i * (360.0 / num_spokes)
        sin_a, cos_a = get_sin_cos(ang)
        gx = R * cos_a
        gy = 0
        gz = R * sin_a
        gondolas.append((gx, gy, gz, i))

    gondolas.sort(key=lambda item: item[0])

    for gx, gy, gz, idx in gondolas:
        cabin_themes = [
            ((235, 55, 55), (175, 30, 30)),     # Merah
            ((245, 195, 35), (195, 140, 15)),   # Kuning
            ((50, 185, 80), (25, 130, 45)),     # Hijau
            ((155, 55, 180), (115, 30, 135))    # Ungu
        ]
        c_light, c_dark = cabin_themes[idx % len(cabin_themes)]
        
        # A. Gantungan Belakang (dari rim belakang y=-W ke tepi atap belakang y=-10)
        ln(gx, -W, gz, gx, -10, gz - 10, (120, 130, 140), 3)
        
        # B. Struktur Kabin (Bawah-ke-Atas agar penumpukan kedalaman benar)
        # 1. Pilar sudut belakang (y = -10)
        ln(gx-10, -10, gz-26, gx-10, -10, gz-14, c_dark, 3)
        ln(gx+10, -10, gz-26, gx+10, -10, gz-14, c_dark, 3)
        
        # 2. Keranjang bawah kabin (y = -10 s.d 10)
        draw_block(gx-10, gx+10, -10, 10, gz-40, gz-26, c_light, c_dark, c_dark)
        
        # 3. Kaca tengah kabin (sedikit lebih kecil agar berada di dalam pilar)
        draw_block(gx-8, gx+8, -8, 8, gz-26, gz-14, (168, 225, 248), (138, 198, 228), (98, 160, 195))
        
        # 4. Atap kabin
        draw_block(gx-10, gx+10, -10, 10, gz-14, gz-10, (255, 235, 100), (210, 180, 40), (180, 150, 30))
        
        # 5. Pilar sudut depan (y = 10, digambar terakhir di atas kaca/atap/keranjang)
        ln(gx-10, 10, gz-26, gx-10, 10, gz-14, c_dark, 3)
        ln(gx+10, 10, gz-26, gx+10, 10, gz-14, c_dark, 3)
        
        # C. Gantungan Depan (dari rim depan y=W ke tepi atap depan y=10)
        ln(gx, W, gz, gx, 10, gz - 10, (90, 100, 110), 3)

    # ==========================================
    # 9. RODA DEPAN & KAKI PENYANGGA DEPAN (y = W)
    # ==========================================
    # Kaki Depan (y = W) (closer)
    draw_thick_line(-75, W, -H, 0, W, 0, (15, 45, 140), (90, 150, 255), 11, 4)
    draw_thick_line(75, W, -H, 0, W, 0, (15, 45, 140), (90, 150, 255), 11, 4)

    # Ruji Roda Depan (Tebal)
    for i in range(num_spokes):
        ang = _rotasi_sudut + i * (360.0 / num_spokes)
        sin_a, cos_a = get_sin_cos(ang)
        ln(0, W, 0, R * cos_a, W, R * sin_a, (90, 150, 255), 3)

    # Rim Roda Depan (Vibrant Blue & Outline)
    front_rim_pts = []
    for i in range(num_pts):
        ang = i * (360.0 / num_pts)
        sin_a, cos_a = get_sin_cos(ang)
        front_rim_pts.append(iso(R * cos_a, W, R * sin_a))
    pygame.draw.lines(screen, (45, 45, 45), True, front_rim_pts, 14)
    pygame.draw.lines(screen, (15, 45, 140), True, front_rim_pts, 10)
    pygame.draw.lines(screen, (90, 150, 255), True, front_rim_pts, 4)

    # Cap Poros tambahan kecil berwarna oranye di paling DEPAN (y = W)
    draw_block(-2, 2, W+3, W+4, -2, 2, (245, 185, 45), (225, 105, 25), (195, 85, 15))

    # Lampu LED Neon Berputar pada Rim Roda Depan
    for i in range(num_spokes * 2):
        ang = _rotasi_sudut + i * (180.0 / num_spokes)
        sin_a, cos_a = get_sin_cos(ang)
        rx = R * cos_a
        rz = R * sin_a
        neon_colors = [(255, 60, 60), (60, 255, 60), (255, 235, 50), (50, 235, 255)]
        col = neon_colors[i % len(neon_colors)]
        p_light = iso(rx, W + 2, rz)
        pygame.draw.circle(screen, col, p_light, 5)
        pygame.draw.circle(screen, (255, 255, 255), p_light, 2)


# --- CLASS WRAPPER UNTUK OOP ---
class Bianglala:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def render(self, screen):
        draw_bianglala(screen, self.x, self.y)