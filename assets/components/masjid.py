import pygame
import sys

# =========================================================
# PALET WARNA ISOMETRI REALSITIS (Gradasi Cahaya 3D)
# =========================================================
# Kubah Hijau Zamrud (3D Spherikal Perspektif)
DOME_DARK        = (12, 54, 32)     # Sisi kiri/belakang pekat
DOME_MED         = (20, 92, 56)     # Sisi tengah
DOME_LIGHT       = (38, 145, 90)    # Sisi kanan depan (terkena cahaya)
DOME_HILITE      = (72, 190, 128)   # Kilauan pantulan matahari matahari
DOME_GRID        = (120, 200, 160)  # Jala tekstur kubah

# Dinding Mewah Isometrik (Krim / Beige)
WALL_SHADOW_LEFT = (198, 188, 168)  # Dinding Sisi Kiri (Gelap/Membelakangi Cahaya)
WALL_LIGHT_RIGHT = (248, 242, 228)  # Dinding Sisi Kanan (Terang/Menghadap Cahaya)
WALL_BASE_MID    = (226, 216, 198)  # Warna pembatas / transisi sudut
ARCH_VOID        = (35, 40, 38)     # Kedalaman lubang pintu/jendela gelap

# Atap & List Isometrik (Hijau Tua)
ROOF_DARK_LEFT   = (14, 66, 40)     # Atap miring sisi kiri
ROOF_LIGHT_RIGHT = (28, 110, 70)    # Atap miring sisi kanan
GOLD_ORAMENT     = (235, 185, 45)   # Bulan sabit emas puncak

# Vegetasi Alam
GRASS_BASE       = (110, 190, 120)  # Hijau rumput segar disamakan dengan taman


def draw_iso_block(surface, cx, cy, w_left, w_right, h, c_left, c_right, c_top=None, scale=1.0):
    """
    Helper untuk menggambar balok gedung 3D Isometrik (Menyamping).
    cx, cy: Titik sudut depan bawah gedung
    """
    w_left = int(w_left * scale)
    w_right = int(w_right * scale)
    h = int(h * scale)

    # Titik sudut bawah
    p_front_bottom = (cx, cy)
    p_left_bottom  = (cx - w_left, cy - w_left // 2)
    p_right_bottom = (cx + w_right, cy - w_right // 2)
    p_back_bottom  = (cx - w_left + w_right, cy - (w_left // 2) - (w_right // 2))

    # Titik sudut atas (vertikal ditarik ke atas sebesar h)
    p_front_top = (cx, cy - h)
    p_left_top  = (cx - w_left, cy - w_left // 2 - h)
    p_right_top = (cx + w_right, cy - w_right // 2 - h)
    p_back_top  = (cx - w_left + w_right, cy - (w_left // 2) - (w_right // 2) - h)

    # Gambaran Sisi Dinding Kiri (Shadow)
    pygame.draw.polygon(surface, c_left, [p_front_bottom, p_left_bottom, p_left_top, p_front_top])
    pygame.draw.polygon(surface, (45, 45, 45), [p_front_bottom, p_left_bottom, p_left_top, p_front_top], max(1, int(2 * scale)))
    
    # Gambaran Sisi Dinding Kanan (Light)
    pygame.draw.polygon(surface, c_right, [p_front_bottom, p_right_bottom, p_right_top, p_front_top])
    pygame.draw.polygon(surface, (45, 45, 45), [p_front_bottom, p_right_bottom, p_right_top, p_front_top], max(1, int(2 * scale)))
    
    # Gambaran Sisi Atap Atas (Jika ditentukan)
    if c_top:
        pygame.draw.polygon(surface, c_top, [p_front_top, p_left_top, p_back_top, p_right_top])
        pygame.draw.polygon(surface, (45, 45, 45), [p_front_top, p_left_top, p_back_top, p_right_top], max(1, int(2 * scale)))


def draw_iso_arch(surface, cx, cy, h_base, w_half, h_arch, side='right', scale=1.0):
    """Menggambar pintu/jendela busur melengkung yang mengikuti arah miring dinding isometrik."""
    dx = int(w_half * scale)
    # Jika side == 'right', dinding miring ke kanan atas (dy harus negatif agar titik kanan lebih tinggi di y)
    # Jika side == 'left', dinding miring ke kiri atas (dy harus positif agar titik kiri lebih tinggi di y)
    dy = -dx // 2 if side == 'right' else dx // 2
    h_base = int(h_base * scale)
    h_arch = int(h_arch * scale)

    # Poligon Rongga Pintu
    pts = [
        (cx - dx, cy - dy),
        (cx + dx, cy + dy),
        (cx + dx, cy + dy - h_base),
        (cx, cy - h_base - h_arch),
        (cx - dx, cy - dy - h_base)
    ]
    pygame.draw.polygon(surface, ARCH_VOID, pts)
    pygame.draw.polygon(surface, GOLD_ORAMENT, pts, max(1, int(1 * scale)))


def draw_iso_minaret(surface, cx, cy, size, height, scale=1.0):
    """Menggambar satu tiang menara bulat-segiempat 3D menyamping."""
    half = int((size // 2) * scale)
    # Pondasi Bawah Menara
    draw_iso_block(surface, cx, cy, half + int(4 * scale), half + int(4 * scale), int(25 * scale), WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, ROOF_DARK_LEFT, scale=1.0)
    # Tiang Panjang Utama
    draw_iso_block(surface, cx, cy - int(25 * scale), half, half, int(height * scale), WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, scale=1.0)
    
    # Pembatas Balkon Tengah
    by = cy - int(25 * scale) - int(height * scale)
    draw_iso_block(surface, cx, by, half + int(6 * scale), half + int(6 * scale), int(10 * scale), ROOF_DARK_LEFT, ROOF_LIGHT_RIGHT, (35, 135, 80), scale=1.0)
    
    # Tiang Menara Bagian Atas
    draw_iso_block(surface, cx, by - int(10 * scale), half - int(2 * scale), half - int(2 * scale), int(35 * scale), WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, scale=1.0)
    
    # Atap Kubah Kecil Menara (Berbentuk Kerucut Isometrik)
    ty = by - int(45 * scale)
    pygame.draw.polygon(surface, DOME_DARK, [(cx - half, ty), (cx, ty - int(22 * scale)), (cx, ty), (cx - half, ty)])
    pygame.draw.polygon(surface, DOME_LIGHT, [(cx, ty), (cx, ty - int(22 * scale)), (cx + half, ty), (cx, ty)])
    pygame.draw.polygon(surface, (45, 45, 45), [(cx - half, ty), (cx, ty - int(22 * scale)), (cx + half, ty)], max(1, int(1 * scale)))
    pygame.draw.line(surface, GOLD_ORAMENT, (cx, ty - int(22 * scale)), (cx, ty - int(32 * scale)), max(1, int(2 * scale)))


def draw_masjid(surface, cx, cy, scale=1.0):
    """
    Merender seluruh Kompleks Masjid Megah 3D dengan Sudut Pandang Menyamping (Isometrik).
    cx, cy: Pusat koordinat alas depan bangunan.
    """

    # =========================================================
    # 1. PEKARANGAN ALAS (Isometrik Rhombus Rapi, Tanpa Pohon)
    # =========================================================
    def iso(u, v, w):
        return cx + (u - v) * 1.6 * scale, cy + ((u + v) * 0.8 - w) * scale

    L_out = 90
    L_in = 82
    thickness = 3

    # Alas Paving Putih Luar (Ketebalan 3px)
    base_top = [(-L_out, -L_out, 0), (L_out, -L_out, 0), (L_out, L_out, 0), (-L_out, L_out, 0)]
    base_left = [(-L_out, L_out, -thickness), (L_out, L_out, -thickness), (L_out, L_out, 0), (-L_out, L_out, 0)]
    base_right = [(L_out, -L_out, -thickness), (L_out, L_out, -thickness), (L_out, L_out, 0), (L_out, -L_out, 0)]

    pygame.draw.polygon(surface, (195, 190, 180), [iso(u, v, w) for u, v, w in base_left])
    pygame.draw.polygon(surface, (175, 170, 160), [iso(u, v, w) for u, v, w in base_right])
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in base_left], max(1, int(2 * scale)))
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in base_right], max(1, int(2 * scale)))
    
    # Atap Paving Putih
    pygame.draw.polygon(surface, (245, 242, 235), [iso(u, v, w) for u, v, w in base_top])
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in base_top], max(1, int(2 * scale)))

    # Alas Rumput Hijau Dalam
    grass_top = [(-L_in, -L_in, 0), (L_in, -L_in, 0), (L_in, L_in, 0), (-L_in, L_in, 0)]
    pygame.draw.polygon(surface, GRASS_BASE, [iso(u, v, w) for u, v, w in grass_top])
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in grass_top], max(1, int(2 * scale)))



    # =========================================================
    # 3. GEDUNG UTAMA SAYAP KIRI & KANAN (Main Hull Wings)
    # =========================================================
    draw_iso_block(surface, cx, cy - 15 * scale, 130, 130, 90, WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, ROOF_DARK_LEFT, scale=scale)

    # Jendela Lengkung Isometrik pada Dinding Sayap (Miring Mengikuti Sudut Dinding)
    draw_iso_arch(surface, cx - 45 * scale, cy - 40 * scale, 30, 10, 12, side='left', scale=scale)
    draw_iso_arch(surface, cx - 95 * scale, cy - 65 * scale, 30, 10, 12, side='left', scale=scale)
    draw_iso_arch(surface, cx + 45 * scale, cy - 40 * scale, 30, 10, 12, side='right', scale=scale)
    draw_iso_arch(surface, cx + 95 * scale, cy - 65 * scale, 30, 10, 12, side='right', scale=scale)

    # List Atap Atas Tambahan
    draw_iso_block(surface, cx, cy - 105 * scale, 134, 134, 8, ROOF_DARK_LEFT, ROOF_LIGHT_RIGHT, scale=scale)

    # =========================================================
    # 4. STRUKTUR LANTAI DUA / DRUM KUBAH PUSAT (Ditinggikan)
    # =========================================================
    draw_iso_block(surface, cx, cy - 113 * scale, 75, 75, 65, WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, ROOF_DARK_LEFT, scale=scale)
    draw_iso_block(surface, cx, cy - 178 * scale, 76, 76, 5, GOLD_ORAMENT, GOLD_ORAMENT, scale=scale)

    # =========================================================
    # 5. KUBAH UTAMA 3D SIMETRIS & RAPI (Dinaikkan & Ditinggikan)
    # =========================================================
    # Lempengan leher kubah (neck pedestal)
    draw_iso_block(surface, cx, cy - 193 * scale, 64, 64, 5, WALL_SHADOW_LEFT, WALL_LIGHT_RIGHT, ROOF_DARK_LEFT, scale=scale)
    
    dome_center_y = cy - 198 * scale
    
    def get_dome_r(z):
        if z < 20 * scale:
            return (48 + 10 * (z / (20.0 * scale))) * scale
        else:
            t = (z - 20 * scale) / (80.0 * scale)
            t = max(0.0, min(1.0, t))
            return 58 * (1.0 - t) * (1.0 - t * t * 0.5) * scale

    # 4 sayatan warna vertikal untuk gradasi cahaya
    slices = [
        (-1.0, -0.5, DOME_DARK),
        (-0.5, 0.0, DOME_MED),
        (0.0, 0.5, DOME_LIGHT),
        (0.5, 1.0, DOME_HILITE)
    ]
    
    H_dome = int(100 * scale)  # Tinggi ditinggikan dari 85 menjadi 100 agar lebih megah
    
    # Gambar sayatan gradasi
    for f_left, f_right, color in slices:
        pts = []
        for z in range(0, H_dome + 1, 2):
            r = get_dome_r(z)
            pts.append((cx + r * f_left, dome_center_y - z))
        for z in range(H_dome, -1, -2):
            r = get_dome_r(z)
            pts.append((cx + r * f_right, dome_center_y - z))
        pygame.draw.polygon(surface, color, pts)
    
    # Outline luar kubah
    outer_pts = []
    for z in range(0, H_dome + 1, 2):
        r = get_dome_r(z)
        outer_pts.append((cx - r, dome_center_y - z))
    for z in range(H_dome, -1, -2):
        r = get_dome_r(z)
        outer_pts.append((cx + r, dome_center_y - z))
    pygame.draw.polygon(surface, (45, 45, 45), outer_pts, max(1, int(2 * scale)))

    # Jala/Grid Tekstur Kubah
    # Lingkaran Latitudinal (Ring)
    for z_ring in [int(25 * scale), int(50 * scale), int(75 * scale)]:
        r_ring = get_dome_r(z_ring)
        pygame.draw.ellipse(surface, DOME_GRID, (cx - r_ring, dome_center_y - z_ring - r_ring * 0.15, 2 * r_ring, r_ring * 0.3), max(1, int(1 * scale)))

    # Garis Longitudinal (Vertikal melengkung)
    for f_long in [-0.5, 0.0, 0.5]:
        pts_long = []
        for z in range(0, H_dome + 1, 3):
            r = get_dome_r(z)
            pts_long.append((cx + r * f_long, dome_center_y - z))
        pygame.draw.lines(surface, DOME_GRID, False, pts_long, max(1, int(1 * scale)))

    # Bulan Sabit Spire Emas di Puncak
    pygame.draw.line(surface, GOLD_ORAMENT, (cx, dome_center_y - H_dome), (cx, dome_center_y - H_dome - int(20 * scale)), max(1, int(3 * scale)))
    pygame.draw.circle(surface, GOLD_ORAMENT, (cx, dome_center_y - H_dome - int(25 * scale)), int(6 * scale), max(1, int(2 * scale)))

    # =========================================================
    # 6. GAPURA / PORTAL MASUK DEPAN
    # =========================================================
    portal_x = cx - 15 * scale
    portal_y = cy + 25 * scale
    
    draw_iso_block(surface, portal_x, portal_y, 50, 40, 85, (38, 46, 42), (54, 64, 60), (60, 75, 70), scale=scale)
    draw_iso_block(surface, portal_x, portal_y - 85 * scale, 52, 42, 6, ROOF_DARK_LEFT, ROOF_LIGHT_RIGHT, scale=scale)
    draw_iso_block(surface, portal_x, portal_y - 91 * scale, 52, 42, 3, GOLD_ORAMENT, GOLD_ORAMENT, scale=scale)

    # Pintu utama dirapikan di tengah dinding kanan (portal_y - 10)
    draw_iso_arch(surface, portal_x + 20 * scale, portal_y - 10 * scale, 45, 12, 16, side='right', scale=scale)
    draw_iso_arch(surface, portal_x + 20 * scale, portal_y - 10 * scale, 35, 8, 10, side='right', scale=scale)

    # =========================================================
    # 7. MENARA DEPAN KANAN (Forefront Minaret)
    # =========================================================
    draw_iso_minaret(surface, cx + 130 * scale, cy - 25 * scale, 24, 155, scale=scale)

    # =========================================================
    # 8. ELEMEN DETAIL TANGGA (3D Blocky Staircase di depan pintu)
    # =========================================================
    # Tangga diposisikan tepat di bawah pintu masuk pada dinding kanan portal
    # Portal front-bottom = (portal_x, portal_y), door di portal_x+20
    # Dinding kanan miring ke kanan-atas: titik bawah pintu ~(portal_x+20, portal_y - 0.5*20) = (portal_x+20, portal_y-10)
    stair_cx = portal_x + 20
    stair_base_y = portal_y - 5 * scale
    draw_iso_block(surface, stair_cx, stair_base_y + 10 * scale, 22, 22, 4, (195, 190, 180), (220, 215, 205), (240, 235, 225), scale=scale)
    draw_iso_block(surface, stair_cx, stair_base_y + 6 * scale, 18, 18, 4, (195, 190, 180), (220, 215, 205), (240, 235, 225), scale=scale)
    draw_iso_block(surface, stair_cx, stair_base_y + 2 * scale, 14, 14, 4, (195, 190, 180), (220, 215, 205), (240, 235, 225), scale=scale)


# ================= SCRIPT EKSEKUSI (Bisa dirun mandiri) =================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Desain Kompleks Masjid 3D")
    clock = pygame.time.Clock()

    while True:
        screen.fill((100, 149, 237))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_masjid(screen, 400, 350)

        pygame.display.flip()
        clock.tick(30)