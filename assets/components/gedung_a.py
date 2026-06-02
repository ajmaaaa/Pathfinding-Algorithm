import pygame

# --- Konstanta & Skala Isometrik ---
TILE_W = 18
TILE_H = 9
Z_SCALE = 9

# --- Palet Warna ---
COLOR_GRASS = (139, 195, 74)        # Hijau rumput
COLOR_PATH = (158, 158, 158)        # Abu-abu jalan
COLOR_WALL_LEFT = (245, 245, 250)   # Dinding kiri (Terang/Kena cahaya)
COLOR_WALL_RIGHT = (200, 205, 210)  # Dinding kanan (Lebih gelap/Bayangan)
COLOR_ROOF_OUTER = (250, 250, 255)  # Pinggiran atap
COLOR_ROOF_INNER = (130, 135, 140)  # Lantai atap

def to_iso(x, y, z, anchor_x, anchor_y):
    """Konversi koordinat 3D ke 2D Layar Isometrik"""
    sx = (x - y) * TILE_W + anchor_x
    sy = (x + y) * TILE_H - z * Z_SCALE + anchor_y
    return sx, sy

def draw_poly(surface, color, points_3d, anchor_x, anchor_y):
    """Fungsi pembantu untuk menggambar poligon dari titik 3D"""
    points_2d = [to_iso(x, y, z, anchor_x, anchor_y) for x, y, z in points_3d]
    pygame.draw.polygon(surface, color, points_2d)

def draw_tree(surface, x, y, z, anchor_x, anchor_y, scale=1.0):
    """Fungsi untuk menggambar pohon isometrik 3D"""
    sx, sy = to_iso(x, y, z, anchor_x, anchor_y)
    
    # Batang pohon
    trunk_w = max(2, int(4 * scale))
    trunk_h = max(5, int(15 * scale))
    pygame.draw.rect(surface, (121, 85, 72), (sx - trunk_w//2, sy - trunk_h, trunk_w, trunk_h))
    
    # Daun (Dua layer lingkaran untuk efek 3D/Lighting)
    r1 = int(14 * scale)
    r2 = int(9 * scale)
    pygame.draw.circle(surface, (76, 175, 80), (int(sx), int(sy - trunk_h - r1//2)), r1)
    pygame.draw.circle(surface, (139, 195, 74), (int(sx - 3*scale), int(sy - trunk_h - r1//2 - 3*scale)), r2)

def draw_gedungA(screen, anchor_x, anchor_y, scale=1.0):
    local_tile_w = TILE_W * scale
    local_tile_h = TILE_H * scale
    local_z_scale = Z_SCALE * scale
    
    def to_iso_local(x, y, z):
        sx = (x - y) * local_tile_w + anchor_x
        sy = (x + y) * local_tile_h - z * local_z_scale + anchor_y
        return sx, sy

    def draw_poly(surface, color, points_3d, ax=None, ay=None):
        points_2d = [to_iso_local(x, y, z) for x, y, z in points_3d]
        pygame.draw.polygon(surface, color, points_2d)

    def draw_tree(surface, x, y, z, ax=None, ay=None, sc=1.0):
        sx, sy = to_iso_local(x, y, z)
        trunk_w = max(2, int(4 * scale))
        trunk_h = max(5, int(15 * scale))
        pygame.draw.rect(surface, (121, 85, 72), (sx - trunk_w//2, sy - trunk_h, trunk_w, trunk_h))
        r1 = int(14 * scale)
        r2 = int(9 * scale)
        pygame.draw.circle(surface, (76, 175, 80), (int(sx), int(sy - trunk_h - r1//2)), r1)
        pygame.draw.circle(surface, (139, 195, 74), (int(sx - 3*scale), int(sy - trunk_h - r1//2 - 3*scale)), r2)

    # Dimensi Gedung Utama
    W, D, H = 12, 12, 46
    
    # (Base slab, taman, dan pohon dihapus agar tidak tumpang tindih di klaster CBD)
    # CBD base sudah menyediakan alas bersama.


    # 3. Dinding Utama Gedung
    wall_r = [(W, 0, 0), (W, D, 0), (W, D, H), (W, 0, H)] # Kanan
    draw_poly(screen, COLOR_WALL_RIGHT, wall_r, anchor_x, anchor_y)
    
    wall_l = [(0, D, 0), (W, D, 0), (W, D, H), (0, D, H)] # Kiri
    draw_poly(screen, COLOR_WALL_LEFT, wall_l, anchor_x, anchor_y)

    # 4. Kaca Jendela (Looping per lantai dan kolom)
    for f in range(18): # 18 Lantai
        # Efek Pantulan: Lantai bawah memantulkan area gelap (persis seperti gambar)
        if f < 5:
            l_dark, l_light = (10, 40, 80), (20, 80, 140)
            r_dark, r_light = (5, 25, 50), (10, 40, 80)
        else:
            l_dark, l_light = (21, 101, 192), (66, 165, 245)
            r_dark, r_light = (13, 71, 161), (30, 136, 229)

        for c in range(4): # 4 Kolom
            # Kalkulasi posisi jendela
            offset_col = c * 2.8 + 0.6
            offset_col_end = offset_col + 2.2
            z1 = f * 2.5 + 1.0
            z2 = z1 + 1.7
            
            # Kaca Kanan (Dinding Kanan) - Dibelah diagonal untuk efek mengkilap
            pr1, pr2 = (W, offset_col, z1), (W, offset_col_end, z1)
            pr3, pr4 = (W, offset_col_end, z2), (W, offset_col, z2)
            draw_poly(screen, r_dark, [pr1, pr2, pr3], anchor_x, anchor_y)
            draw_poly(screen, r_light, [pr1, pr3, pr4], anchor_x, anchor_y)

            # Kaca Kiri (Dinding Kiri) - Dibelah diagonal untuk efek mengkilap
            pl1, pl2 = (offset_col, D, z1), (offset_col_end, D, z1)
            pl3, pl4 = (offset_col_end, D, z2), (offset_col, D, z2)
            draw_poly(screen, l_dark, [pl1, pl2, pl3], anchor_x, anchor_y)
            draw_poly(screen, l_light, [pl1, pl3, pl4], anchor_x, anchor_y)

    # 5. Atap & Detailnya
    # Border putih atap
    roof_outer = [(0, 0, H), (W, 0, H), (W, D, H), (0, D, H)]
    draw_poly(screen, COLOR_ROOF_OUTER, roof_outer, anchor_x, anchor_y)
    # Lantai dalam abu-abu
    roof_inner = [(0.5, 0.5, H+0.1), (W-0.5, 0.5, H+0.1), (W-0.5, D-0.5, H+0.1), (0.5, D-0.5, H+0.1)]
    draw_poly(screen, COLOR_ROOF_INNER, roof_inner, anchor_x, anchor_y)

    # Kolam Renang (Tepi putih, air cyan)
    pool_border = [(1.8, 6.8, H+0.2), (5.2, 6.8, H+0.2), (5.2, 11.2, H+0.2), (1.8, 11.2, H+0.2)]
    draw_poly(screen, (245, 245, 245), pool_border, anchor_x, anchor_y)
    pool_water = [(2.0, 7.0, H+0.3), (5.0, 7.0, H+0.3), (5.0, 11.0, H+0.3), (2.0, 11.0, H+0.3)]
    draw_poly(screen, (77, 208, 225), pool_water, anchor_x, anchor_y)

    # Kursi Santai
    for i in range(4):
        cy = 7.5 + i * 1.0
        chair = [(6.0, cy, H+0.2), (6.8, cy, H+0.2), (6.8, cy+0.4, H+0.2), (6.0, cy+0.4, H+0.2)]
        draw_poly(screen, (255, 255, 255), chair, anchor_x, anchor_y)

    # Ruang Lift / AC di Atap (Kotak putih)
    staircase_r = [(11.5, 0.5, H), (11.5, 2.5, H), (11.5, 2.5, H+3.0), (11.5, 0.5, H+3.0)]
    staircase_l = [(9.5, 2.5, H), (11.5, 2.5, H), (11.5, 2.5, H+3.0), (9.5, 2.5, H+3.0)]
    staircase_t = [(9.5, 0.5, H+3.0), (11.5, 0.5, H+3.0), (11.5, 2.5, H+3.0), (9.5, 2.5, H+3.0)]
    draw_poly(screen, (210, 210, 210), staircase_r, anchor_x, anchor_y)
    draw_poly(screen, (240, 240, 240), staircase_l, anchor_x, anchor_y)
    draw_poly(screen, (255, 255, 255), staircase_t, anchor_x, anchor_y)

    # Pohon/Taman Kecil di Atap (Dihapus sesuai permintaan)

    # 6. Pohon di Depan Gedung (Digambar terakhir agar menutupi bagian bawah)
    draw_tree(screen, -1, 14, 0, anchor_x, anchor_y)
    draw_tree(screen, 14, 13, 0, anchor_x, anchor_y)