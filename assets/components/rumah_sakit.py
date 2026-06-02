import pygame
C_DARK = (50, 50, 50)

# --- PENGATURAN SKALA & PROYEKSI 3D ISOMETRIK ---
SCALE = 1.3
def to_iso(x, y, z, ox, oy):
    """Mengubah koordinat 3D (x,y,z) menjadi koordinat 2D Isometrik pada layar"""
    ix = ox + (x - z) * 2 * SCALE
    iy = oy + (x + z) * 1 * SCALE - y * 2 * SCALE
    return (ix, iy)

def draw_polygon_iso(screen, color, points, ox, oy):
    """Menggambar poligon berdasarkan titik 3D"""
    iso_points = [to_iso(px, py, pz, ox, oy) for (px, py, pz) in points]
    pygame.draw.polygon(screen, color, iso_points)

def draw_block(screen, x, y, z, w, h, d, ox, oy, c_top, c_left, c_right):
    """Menggambar blok 3D padat dengan 3 sisi yang terlihat (Top, Left, Right)"""
    # Titik-titik sudut
    p_top = [(x, y+h, z), (x+w, y+h, z), (x+w, y+h, z+d), (x, y+h, z+d)]
    p_left = [(x, y, z+d), (x+w, y, z+d), (x+w, y+h, z+d), (x, y+h, z+d)]
    p_right = [(x+w, y, z), (x+w, y, z+d), (x+w, y+h, z+d), (x+w, y+h, z)]

    # Urutan gambar: Kiri, Kanan, lalu Atas
    draw_polygon_iso(screen, c_left, p_left, ox, oy)
    draw_polygon_iso(screen, c_right, p_right, ox, oy)
    draw_polygon_iso(screen, c_top, p_top, ox, oy)

def draw_roof(screen, x, y, z, w, d, ox, oy, c_inner):
    """Menggambar atap yang sedikit menjorok ke dalam (parapet)"""
    p_roof = [(x+1, y, z+1), (x+w-1, y, z+1), (x+w-1, y, z+d-1), (x+1, y, z+d-1)]
    draw_polygon_iso(screen, c_inner, p_roof, ox, oy)

def draw_window_band_left(screen, x1, x2, y, h, z, ox, oy, c_win, c_frame):
    """Menggambar sabuk jendela kaca sisi kiri dengan tiang pemisah (mullion)"""
    p_left = [(x1, y, z), (x2, y, z), (x2, y+h, z), (x1, y+h, z)]
    draw_polygon_iso(screen, c_win, p_left, ox, oy)
    for mx in range(x1 + 5, x2, 5):
        p_mullion = [(mx, y, z), (mx+1, y, z), (mx+1, y+h, z), (mx, y+h, z)]
        draw_polygon_iso(screen, c_frame, p_mullion, ox, oy)

def draw_window_band_right(screen, z1, z2, y, h, x, ox, oy, c_win, c_frame):
    """Menggambar sabuk jendela kaca sisi kanan dengan tiang pemisah"""
    p_right = [(x, y, z1), (x, y, z2), (x, y+h, z2), (x, y+h, z1)]
    draw_polygon_iso(screen, c_win, p_right, ox, oy)
    for mz in range(z1 + 5, z2, 5):
        p_mullion = [(x, y, mz), (x, y, mz+1), (x, y+h, mz+1), (x, y+h, mz)]
        draw_polygon_iso(screen, c_frame, p_mullion, ox, oy)



# --- FUNGSI UTAMA MENGGAMBAR RUMAH SAKIT ---
def draw_rumah_sakit(screen, ox, oy, scale=1.0):
    global SCALE
    old_scale = SCALE
    SCALE = 1.3 * scale
    try:
        # Palet Warna (Pencahayaan dari Kiri Atas ke Kanan Bawah)
        C_W_TOP, C_W_LEFT, C_W_RIGHT = (255, 255, 255), (245, 245, 250), (200, 205, 215)
        C_R_TOP, C_R_LEFT, C_R_RIGHT = (255, 80, 80), (220, 30, 30), (170, 15, 15)
        C_B_LEFT, C_B_RIGHT = (120, 180, 210), (80, 130, 170)
        C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT = (240, 245, 245), (220, 225, 230), (180, 185, 190)
        C_GRASS_TOP, C_GRASS_LEFT, C_GRASS_RIGHT = (165, 200, 130), (135, 170, 100), (100, 130, 70)
        C_ROOF, C_ROOF_IN = (235, 240, 245), (215, 220, 225)
        # =========================================================================

        # 1. PLATFORM DASAR & HALAMAN RUMPUT (Statis)
        draw_block(screen, 15, 0, 15, 100, 0.8, 115, ox, oy, C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT)
        draw_block(screen, 18, 0.8, 18, 94, 0.2, 109, ox, oy, C_GRASS_TOP, C_GRASS_LEFT, C_GRASS_RIGHT)

        # Pohon Area Belakang
        def draw_tree(scr, x, y, z, oxx, oyy):
            ix, iy = to_iso(x, y, z, oxx, oyy)
            w_trunk = max(1, int(4 * scale))
            h_trunk = max(1, int(15 * scale))
            pygame.draw.rect(scr, (90, 60, 40), (ix-w_trunk//2, iy-h_trunk, w_trunk, h_trunk))
            pygame.draw.circle(scr, (60, 120, 50), (ix, iy-h_trunk-int(5*scale)), int(14*scale))
            pygame.draw.circle(scr, (70, 130, 60), (ix-int(8*scale), iy-h_trunk+int(3*scale)), int(10*scale))
            pygame.draw.circle(scr, (50, 110, 40), (ix+int(8*scale), iy-h_trunk+int(3*scale)), int(10*scale))
            pygame.draw.circle(scr, (90, 160, 70), (ix-int(4*scale), iy-h_trunk-int(7*scale)), int(8*scale))

        def draw_shrub(scr, x, y, z, oxx, oyy):
            ix, iy = to_iso(x, y, z, oxx, oyy)
            pygame.draw.circle(scr, (60, 120, 50), (ix, iy-int(5*scale)), int(8*scale))
            pygame.draw.circle(scr, (90, 160, 70), (ix-int(3*scale), iy-int(7*scale)), int(4*scale))

        draw_tree(screen, 15, 1.0, 15, ox, oy)
        draw_tree(screen, 15, 1.0, 80, ox, oy)

        # 2. GEDUNG BAWAH (Lantai 1-3)
        draw_block(screen, 25, 1.0, 25, 80, 35, 80, ox, oy, C_ROOF, C_W_LEFT, C_W_RIGHT)
        draw_roof(screen, 25, 36, 25, 80, 80, ox, oy, C_ROOF_IN)
        
        # Jendela Gedung Bawah
        for wy in [8, 18, 28]:
            # Kiri (Terpotong oleh lobi utama)
            draw_window_band_left(screen, 30, 60, wy, 6, 105, ox, oy, C_B_LEFT, C_W_LEFT)
            draw_window_band_left(screen, 98, 102, wy, 6, 105, ox, oy, C_B_LEFT, C_W_LEFT)
            # Kanan (Terpotong oleh sayap kanan)
            draw_window_band_right(screen, 65, 100, wy, 6, 105, ox, oy, C_B_RIGHT, C_W_RIGHT)

        # 3. SAYAP KANAN (Gedung Tengah)
        draw_block(screen, 65, 36, 30, 35, 45, 30, ox, oy, C_ROOF, C_W_LEFT, C_W_RIGHT)
        draw_roof(screen, 65, 81, 30, 35, 30, ox, oy, C_ROOF_IN)
        # AC / Atap kecil di sayap kanan
        draw_block(screen, 75, 81, 45, 8, 4, 8, ox, oy, C_ROOF, C_W_LEFT, C_W_RIGHT)
        
        for wy in [43, 53, 63, 73]:
            draw_window_band_right(screen, 33, 57, wy, 6, 100, ox, oy, C_B_RIGHT, C_W_RIGHT)
            
        # Pita Garis Merah di Sayap Kanan (Atas lalu Turun Ke Bawah)
        draw_block(screen, 65, 81, 35, 37, 2, 10, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)
        draw_block(screen, 100, 1.0, 35, 2, 81, 10, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)

        # 4. MENARA UTAMA TINGGI (Kiri Belakang)
        draw_block(screen, 30, 36, 60, 35, 75, 45, ox, oy, C_ROOF, C_W_LEFT, C_W_RIGHT)
        draw_roof(screen, 30, 111, 60, 35, 45, ox, oy, C_ROOF_IN)
        
        # Helipad & Atap Kaca di Menara
        draw_block(screen, 40, 111, 75, 15, 2, 15, ox, oy, (100, 110, 120), C_W_LEFT, C_W_RIGHT)
        draw_block(screen, 42, 113, 77, 11, 0, 11, ox, oy, (180, 220, 240), C_W_LEFT, C_W_RIGHT)
        
        # Jendela Sudut Dalam Menara Utama
        for wy in [43, 53, 63, 73, 83, 93]:
            draw_window_band_right(screen, 65, 100, wy, 6, 65, ox, oy, C_B_RIGHT, C_W_RIGHT)

        # Palang Merah Besar di Menara Utama
        draw_block(screen, 43, 56, 105, 9, 35, 2, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)
        draw_block(screen, 30, 69, 105, 35, 9, 2, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)

        # 5. LOBI UTAMA / PINTU MASUK
        draw_block(screen, 65, 1.0, 105, 30, 25, 15, ox, oy, C_ROOF, C_W_LEFT, C_W_RIGHT)
        draw_roof(screen, 65, 26, 105, 30, 15, ox, oy, C_ROOF_IN)
        
        # Palang Merah Kecil di Lobi
        draw_block(screen, 78, 14, 120, 4, 10, 1, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)
        draw_block(screen, 75, 17, 120, 10, 4, 1, ox, oy, C_R_TOP, C_R_LEFT, C_R_RIGHT)
        
        # Pintu Lobi Gelap
        draw_block(screen, 73, 1.0, 120, 14, 10, 1, ox, oy, C_DARK, C_DARK, C_DARK)
        
        # --- Pintu Kaca Lobby ---
        draw_block(screen, 70, 0, 120, 20, 0.8, 5, ox, oy, C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT)
        draw_block(screen, 72, 0, 125, 16, 0.8, 5, ox, oy, C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT)

        # 7. DETAIL HALAMAN DEPAN (Pohon & Semak)
        draw_tree(screen, 110, 1.0, 40, ox, oy)
        draw_tree(screen, 110, 1.0, 100, ox, oy)
        draw_shrub(screen, 60, 1.0, 125, ox, oy)
        draw_shrub(screen, 100, 1.0, 125, ox, oy)
        draw_shrub(screen, 110, 1.0, 115, ox, oy)
    finally:
        SCALE = old_scale
