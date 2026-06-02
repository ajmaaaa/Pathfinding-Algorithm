import pygame
import sys

# --- PALET WARNA (3D Isometric Shading) ---
WALL_LIGHT = (254, 249, 222)       # Krem terang (Sisi Kiri Depan)
WALL_SHADOW = (238, 228, 198)      # Krem bayangan (Sisi Kanan Depan)
STRIPE_BROWN = (122, 44, 56)       # Cokelat kemerahan gelap (Garis tengah ikonik)
ROOF_RED = (195, 60, 75)           # Merah bata cerah (Lis Atap)
ROOF_RED_SHADOW = (155, 45, 55)    # Merah bata gelap (Lis Atap Bayangan)
WINDOW_BLUE = (65, 155, 215)       # Biru kaca utama
WINDOW_SHADOW = (50, 130, 185)     # Biru kaca bayangan
WINDOW_LIGHT = (190, 235, 255)     # Putih/Biru muda kilauan cahaya

SIDEWALK_GRAY = (220, 220, 225)    # Abu-abu trotoar
SIDEWALK_SHADOW = (190, 190, 195)  # Abu-abu bayangan trotoar
GRASS_GREEN = (135, 190, 95)       # Hijau rumput taman
ROAD_DARK = (60, 62, 68)           # Hitam aspal jalan raya
CAR_RED = (215, 40, 55)            # Merah mobil
CAR_RED_DARK = (165, 30, 40)       # Merah mobil bayangan

def get_iso_p(cx, cy, x, y, z):
    """Mengonversi koordinat 3D Space (X, Y, Z) ke 2D Screen Space Isometrik 2:1"""
    rx = cx + (x - y) * 2
    ry = cy + (x + y) * 1 - z
    return (int(rx), int(ry))

def draw_iso_poly(screen, cx, cy, points, color):
    """Menggambar bidang poligon 3D isometrik terisi warna"""
    screen_pts = [get_iso_p(cx, cy, x, y, z) for x, y, z in points]
    pygame.draw.polygon(screen, color, screen_pts)

def draw_iso_outline(screen, cx, cy, points, color, width=1):
    """Menggambar garis tepi tajam untuk menegaskan bentuk 3D"""
    screen_pts = [get_iso_p(cx, cy, x, y, z) for x, y, z in points]
    pygame.draw.polygon(screen, color, screen_pts, width)

def draw_window_left(screen, cx, cy, x1, x2, y, z1, z2):
    """Menggambar jendela dengan efek refleksi glossy di sisi kiri bangunan"""
    pts = [(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)]
    draw_iso_poly(screen, cx, cy, pts, WINDOW_BLUE)
    # Efek kilau diagonal sudut atas jendela
    ref_pts = [(x1, y, (z1 + z2) // 2), (x2, y, z2), (x1, y, z2)]
    draw_iso_poly(screen, cx, cy, ref_pts, WINDOW_LIGHT)
    draw_iso_outline(screen, cx, cy, pts, (40, 90, 130), 1)

def draw_window_right(screen, cx, cy, x, y1, y2, z1, z2):
    """Menggambar jendela dengan efek refleksi glossy di sisi kanan bangunan"""
    pts = [(x, y1, z1), (x, y2, z1), (x, y2, z2), (x, y1, z2)]
    draw_iso_poly(screen, cx, cy, pts, WINDOW_SHADOW)
    ref_pts = [(x, y2, (z1 + z2) // 2), (x, y2, z2), (x, y1, z2)]
    draw_iso_poly(screen, cx, cy, ref_pts, WINDOW_LIGHT)
    draw_iso_outline(screen, cx, cy, pts, (30, 75, 110), 1)

def draw_tree(screen, cx, cy, x, y):
    """Menggambar pohon bulat 3D menggunakan tumpukan gradasi bola isometrik"""
    p_bot = get_iso_p(cx, cy, x, y, 0)
    p_top = get_iso_p(cx, cy, x, y, 16)
    pygame.draw.line(screen, (115, 80, 60), p_bot, p_top, 3) # Batang pohon
    
    # Daun berlapis (efek shading bulat)
    c1 = get_iso_p(cx, cy, x, y, 18)
    pygame.draw.circle(screen, (65, 125, 65), c1, 10)
    c2 = get_iso_p(cx, cy, x - 2, y - 2, 21)
    pygame.draw.circle(screen, (85, 165, 85), c2, 8)
    c3 = get_iso_p(cx, cy, x - 4, y - 4, 23)
    pygame.draw.circle(screen, (125, 195, 125), c3, 5)

def draw_gedungD(screen, cx, cy, scale=1.0):
    def get_iso_p(cx_dummy, cy_dummy, x, y, z):
        rx = cx + (x - y) * 2 * scale
        ry = cy + ((x + y) * 1 - z) * scale
        return (int(rx), int(ry))

    def draw_iso_poly(screen, cx_dummy, cy_dummy, points, color):
        screen_pts = [get_iso_p(cx, cy, x, y, z) for x, y, z in points]
        pygame.draw.polygon(screen, color, screen_pts)

    def draw_iso_outline(screen, cx_dummy, cy_dummy, points, color, width=1):
        screen_pts = [get_iso_p(cx, cy, x, y, z) for x, y, z in points]
        pygame.draw.polygon(screen, color, screen_pts, max(1, int(width * scale)))

    def draw_window_left(screen, cx_dummy, cy_dummy, x1, x2, y, z1, z2):
        pts = [(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)]
        draw_iso_poly(screen, cx, cy, pts, WINDOW_BLUE)
        ref_pts = [(x1, y, (z1 + z2) // 2), (x2, y, z2), (x1, y, z2)]
        draw_iso_poly(screen, cx, cy, ref_pts, WINDOW_LIGHT)
        draw_iso_outline(screen, cx, cy, pts, (40, 90, 130), 1)

    def draw_window_right(screen, cx_dummy, cy_dummy, x, y1, y2, z1, z2):
        pts = [(x, y1, z1), (x, y2, z1), (x, y2, z2), (x, y1, z2)]
        draw_iso_poly(screen, cx, cy, pts, WINDOW_SHADOW)
        ref_pts = [(x, y2, (z1 + z2) // 2), (x, y2, z2), (x, y1, z2)]
        draw_iso_poly(screen, cx, cy, ref_pts, WINDOW_LIGHT)
        draw_iso_outline(screen, cx, cy, pts, (30, 75, 110), 1)

    def draw_tree(screen, cx_dummy, cy_dummy, x, y):
        p_bot = get_iso_p(cx, cy, x, y, 0)
        p_top = get_iso_p(cx, cy, x, y, 16)
        pygame.draw.line(screen, (115, 80, 60), p_bot, p_top, max(1, int(3 * scale)))
        c1 = get_iso_p(cx, cy, x, y, 18)
        pygame.draw.circle(screen, (65, 125, 65), c1, max(1, int(10 * scale)))
        c2 = get_iso_p(cx, cy, x - 2, y - 2, 21)
        pygame.draw.circle(screen, (85, 165, 85), c2, max(1, int(8 * scale)))
        c3 = get_iso_p(cx, cy, x - 4, y - 4, 23)
        pygame.draw.circle(screen, (125, 195, 125), c3, max(1, int(5 * scale)))

    """Fungsi utama merender seluruh aset Gedung D beserta lingkungannya secara presisi"""
    # (Base slab, taman, dan pohon dihapus agar tidak tumpang tindih di klaster CBD)
    # CBD base sudah menyediakan alas bersama untuk semua gedung.


    # 5. GEDUNG LANTAI 1 (BASE BUILDING)
    g1_l = [(-55, 55, 0), (55, 55, 0), (55, 55, 40), (-55, 55, 40)]
    g1_r = [(55, -55, 0), (55, 55, 0), (55, 55, 40), (55, -55, 40)]
    draw_iso_poly(screen, cx, cy, g1_l, WALL_LIGHT)
    draw_iso_poly(screen, cx, cy, g1_r, WALL_SHADOW)

    # PINTU UTAMA DAN LIS TOPI (Lantai 1)
    door = [(-12, 55, 0), (12, 55, 0), (12, 55, 24), (-12, 55, 24)]
    draw_iso_poly(screen, cx, cy, door, (50, 52, 58)) # Kusen pintu gelap
    awn_l = [(-16, 62, 24), (16, 62, 24), (16, 62, 28), (-16, 62, 28)]
    awn_top = [(-16, 55, 28), (16, 55, 28), (16, 62, 28), (-16, 62, 28)]
    draw_iso_poly(screen, cx, cy, awn_l, ROOF_RED)
    draw_iso_poly(screen, cx, cy, awn_top, ROOF_RED)

    # Jendela Lengkung Lantai 1
    draw_window_left(screen, cx, cy, -42, -24, 55, 8, 28)
    draw_window_left(screen, cx, cy, 24, 42, 55, 8, 28)
    for wy in [-42, -9, 24]: draw_window_right(screen, cx, cy, 55, wy, wy+16, 8, 28)

    # LIS ATAP LANTAI 1
    r1_l = [(-60, 60, 40), (60, 60, 40), (60, 60, 45), (-60, 60, 45)]
    r1_r = [(60, -60, 40), (60, 60, 40), (60, 60, 45), (60, -60, 45)]
    r1_top = [(-60, -60, 45), (60, -60, 45), (60, 60, 45), (-60, 60, 45)]
    draw_iso_poly(screen, cx, cy, r1_l, ROOF_RED)
    draw_iso_poly(screen, cx, cy, r1_r, ROOF_RED_SHADOW)
    draw_iso_poly(screen, cx, cy, r1_top, ROOF_RED)

    # 6. MENARA UTAMA (LANTAI 2 - 7 / 6 Tingkat)
    m_l = [(-48, 48, 45), (48, 48, 45), (48, 48, 195), (-48, 48, 195)]
    m_r = [(48, -48, 45), (48, 48, 45), (48, 48, 195), (48, -48, 195)]
    draw_iso_poly(screen, cx, cy, m_l, WALL_LIGHT)
    draw_iso_poly(screen, cx, cy, m_r, WALL_SHADOW)

    # GARIS COKELAT VERTIKAL IKONIK (Sisi Kiri Depan)
    stripe = [(-7, 48, 45), (7, 48, 45), (7, 48, 195), (-7, 48, 195)]
    draw_iso_poly(screen, cx, cy, stripe, STRIPE_BROWN)

    # LOOP JENDELA MENARA UTAMA (6 Lantai)
    for f in range(6):
        z1 = 53 + f * 24
        z2 = 68 + f * 24
        # Jendela Kiri (Terbagi 2 kolom di kiri & kanan garis cokelat)
        draw_window_left(screen, cx, cy, -38, -26, 48, z1, z2)
        draw_window_left(screen, cx, cy, -22, -11, 48, z1, z2)
        draw_window_left(screen, cx, cy, 11, 22, 48, z1, z2)
        draw_window_left(screen, cx, cy, 26, 38, 48, z1, z2)
        # Jendela Kanan (3 Kolom Jendela)
        draw_window_right(screen, cx, cy, 48, -38, -22, z1, z2)
        draw_window_right(screen, cx, cy, 48, -8, 8, z1, z2)
        draw_window_right(screen, cx, cy, 48, 22, 38, z1, z2)

    # LIS ATAP MENARA UTAMA
    r2_l = [(-52, 52, 195), (52, 52, 195), (52, 52, 200), (-52, 52, 200)]
    r2_r = [(52, -52, 195), (52, 52, 195), (52, 52, 200), (52, -52, 200)]
    r2_top = [(-52, -52, 200), (52, -52, 200), (52, 52, 200), (-52, 52, 200)]
    draw_iso_poly(screen, cx, cy, r2_l, ROOF_RED)
    draw_iso_poly(screen, cx, cy, r2_r, ROOF_RED_SHADOW)
    draw_iso_poly(screen, cx, cy, r2_top, ROOF_RED)

    # 7. MENARA ATAS / SETBACK TOP (2 Tingkat Teratas)
    top_l = [(-35, 35, 200), (35, 35, 200), (35, 35, 250), (-35, 35, 250)]
    top_r = [(35, -35, 200), (35, 35, 200), (35, 35, 250), (35, -35, 250)]
    draw_iso_poly(screen, cx, cy, top_l, WALL_LIGHT)
    draw_iso_poly(screen, cx, cy, top_r, WALL_SHADOW)

    # Jendela Lantai Atas (2 Lantai)
    for f in range(2):
        z1 = 206 + f * 22
        z2 = 220 + f * 22
        draw_window_left(screen, cx, cy, -25, -10, 35, z1, z2)
        draw_window_left(screen, cx, cy, 10, 25, 35, z1, z2)
        draw_window_right(screen, cx, cy, 35, -25, -10, z1, z2)
        draw_window_right(screen, cx, cy, 35, 10, 25, z1, z2)

    # LIS ATAP PALING ATAS (Puncak Gedung)
    r3_l = [(-39, 39, 250), (39, 39, 250), (39, 39, 255), (-39, 39, 255)]
    r3_r = [(39, -39, 250), (39, 39, 250), (39, 39, 255), (39, -39, 255)]
    r3_top = [(-39, -39, 255), (39, -39, 255), (39, 39, 255), (-39, 39, 255)]
    draw_iso_poly(screen, cx, cy, r3_l, ROOF_RED)
    draw_iso_poly(screen, cx, cy, r3_r, ROOF_RED_SHADOW)
    draw_iso_poly(screen, cx, cy, r3_top, ROOF_RED)
    
    # Bagian Dek Atas Dalam Krem Ringan
    top_deck = [(-35, -35, 255), (35, -35, 255), (35, 35, 255), (-35, 35, 255)]
    draw_iso_poly(screen, cx, cy, top_deck, WALL_LIGHT)