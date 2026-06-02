import pygame
import math

# ==========================================
# 1. PALET WARNA (Sesuai Referensi Gambar)
# ==========================================
GRASS       = (140, 195, 110)    # Hijau rumput
GRASS_SHADOW= (110, 160, 85)     # Hijau tanah bawah
WALL_L      = (75, 115, 175)     # Biru dinding kiri (bayangan)
WALL_R      = (95, 135, 200)     # Biru dinding kanan (terang)
TRIM_L      = (210, 215, 220)    # Pelipit putih abu-abu
TRIM_R      = (240, 245, 250)    # Pelipit putih terang
ROOF_TOP    = (40, 60, 90)       # Atap biru dongker gelap
WIN_BG      = (50, 75, 110)      # Kaca jendela
FRAME       = (255, 255, 255)    # Bingkai putih
AC_BOX      = (190, 195, 200)    # Abu-abu kotak AC
LINE        = (60, 75, 95)       # Outline biru tua (bukan hitam) agar estetik

# Warna khusus untuk tangga agar tekstur dan bentuknya lebih rapi & jelas
STEP_TOP    = (210, 215, 220)
STEP_L      = (150, 160, 170)
STEP_R      = (180, 185, 195)

def render_kantor_polisi(layar, cx_pusat, cy_pusat, scale=1.0):
    """Render 2D Isometrik Murni untuk Kantor Polisi"""

    # --- RUMUS PROYEKSI 2D ISOMETRIK ---
    def iso(x, y, z=0):
        scale_x, scale_y = 1.6 * scale, 0.8 * scale
        # Konversi X, Y, Z imajiner menjadi piksel Layar 2D
        sx = cx_pusat + (x - y) * scale_x
        sy = cy_pusat + (x + y) * scale_y - z * scale
        return sx, sy

    # --- FUNGSI MENGGAMBAR POLIGON MULUS ---
    def poly(warna, titik, ketebalan_outline=1):
        pts = [iso(p[0], p[1], p[2]) for p in titik]
        pygame.draw.polygon(layar, warna, pts)
        if ketebalan_outline > 0:
            pygame.draw.polygon(layar, LINE, pts, max(1, int(ketebalan_outline * scale)))

    # --- FUNGSI PEMBUAT BALOK 3D (PAINTER'S ALGORITHM) ---
    def draw_box(x, y, z, dx, dy, dz, col_left, col_right, col_top):
        # Kiri (Menghadap Kiri Bawah)
        poly(col_left, [(x, y+dy, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)])
        # Kanan (Menghadap Kanan Bawah)
        poly(col_right, [(x+dx, y, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x+dx, y, z+dz)])
        # Atas (Menghadap Atas)
        poly(col_top, [(x, y, z+dz), (x+dx, y, z+dz), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)])

    # --- KOMPONEN JENDELA & PINTU ---
    def draw_win_l(x, z):
        w, h = 18, 25
        pts = [(x, 61, z), (x+w, 61, z), (x+w, 61, z+h), (x, 61, z+h)]
        poly(WIN_BG, pts, 2)
        pygame.draw.line(layar, FRAME, iso(x+w/2, 61, z), iso(x+w/2, 61, z+h), max(1, int(2 * scale)))
        pygame.draw.line(layar, FRAME, iso(x, 61, z+h/2), iso(x+w, 61, z+h/2), max(1, int(2 * scale)))

    def draw_door_l(x, z):
        w, h = 30, 35
        pts = [(x, 61, z), (x+w, 61, z), (x+w, 61, z+h), (x, 61, z+h)]
        poly(WIN_BG, pts, 2)
        pygame.draw.line(layar, FRAME, iso(x+w/2, 61, z), iso(x+w/2, 61, z+h), max(1, int(2 * scale)))

    def draw_win_r(y, z):
        w, h = 18, 25
        pts = [(61, y, z), (61, y+w, z), (61, y+w, z+h), (61, y, z+h)]
        poly(WIN_BG, pts, 2)
        pygame.draw.line(layar, FRAME, iso(61, y+w/2, z), iso(61, y+w/2, z+h), max(1, int(2 * scale)))
        pygame.draw.line(layar, FRAME, iso(61, y, z+h/2), iso(61, y+w, z+h/2), max(1, int(2 * scale)))

    def draw_door_r(y, z):
        w, h = 20, 35
        pts = [(61, y, z), (61, y+w, z), (61, y+w, z+h), (61, y, z+h)]
        poly(WIN_BG, pts, 2)
        pygame.draw.line(layar, FRAME, iso(61, y+w/2, z), iso(61, y+w/2, z+h), max(1, int(2 * scale)))

    # ========================================================
    # URUTAN PENGGAMBARAN (SANGAT KRUSIAL!)
    # Dari Objek Paling Bawah/Belakang ke Atas/Depan
    # ========================================================

    # 0. PLATFORM DASAR (Statis)
    draw_box(-75, -75, -2, 150, 150, 2, STEP_L, STEP_R, STEP_TOP)

    # 3. KOTAK BANGUNAN UTAMA (Dibagi per lantai agar tidak tertimpa trim)
    # Lantai 1
    draw_box(-60, -60, 0, 120, 120, 43, WALL_L, WALL_R, ROOF_TOP)

    # 4. PELIPIT PUTIH (TRIM) TENGAH
    draw_box(-62, -62, 43, 124, 124, 5, TRIM_L, TRIM_R, TRIM_R)

    # Lantai 2
    draw_box(-60, -60, 48, 120, 120, 42, WALL_L, WALL_R, ROOF_TOP)

    # PELIPIT PUTIH (TRIM) ATAS
    draw_box(-62, -62, 90, 124, 124, 5, TRIM_L, TRIM_R, TRIM_R)

    # 5. JENDELA & PINTU
    # Lantai 1 (Z=14)
    draw_win_l(-45, 14)
    draw_door_l(-15, 4) # Pintu Utama Tengah
    draw_win_l(25, 14)

    # Lantai 2 (Z=55)
    draw_win_l(-45, 55)
    draw_win_l(25, 55)

    # Pintu Samping Lantai 2 (Dinding Kanan)
    draw_door_r(-45, 45)

    # 6. TANGGA TERAS DEPAN PINTU
    # Step 1 (bawah)
    draw_box(-20, 61, 0, 40, 16, 2, STEP_L, STEP_R, STEP_TOP)
    # Step 2 (atas)
    draw_box(-15, 61, 0, 30, 8, 4, STEP_L, STEP_R, STEP_TOP)

    # 7. TANGGA SAMPING (Di sisi kanan X=61)
    # Landing / Bordes Pintu Samping
    draw_box(61, -45, 0, 20, 20, 45, STEP_L, STEP_R, STEP_TOP)
    
    # Deretan Anak Tangga
    for i in range(10):
        sy = -25 + i * 8
        sz = 45 - (i+1) * 4.5
        draw_box(61, sy, 0, 20, 8, sz, STEP_L, STEP_R, STEP_TOP)

    # Pagar Tangga (Railing luar)
    pts_railing = [
        (81, -45, 60), (81, -25, 60), (81, 55, 15),
        (81, 55, 0), (81, -25, 45), (81, -45, 45)
    ]
    poly(TRIM_R, pts_railing, 2)
    # Tiang-tiang kecil penyangga pagar
    for i in range(6):
        ry = -25 + i * 16
        rz = 45 - i * 9
        pygame.draw.line(layar, LINE, iso(81, ry, rz), iso(81, ry, rz+15), max(1, int(2 * scale)))

    # 8. DETAIL ATAP
    # Mesin AC 1 & 2
    draw_box(-30, -40, 95, 16, 16, 12, AC_BOX, AC_BOX, TRIM_R)
    pygame.draw.circle(layar, LINE, (int(iso(-22, -32, 107)[0]), int(iso(-22, -32, 107)[1])), int(5 * scale), max(1, int(2 * scale)))
    
    draw_box(-10, -50, 95, 16, 16, 12, AC_BOX, AC_BOX, TRIM_R)
    pygame.draw.circle(layar, LINE, (int(iso(-2, -42, 107)[0]), int(iso(-2, -42, 107)[1])), int(5 * scale), max(1, int(2 * scale)))

    # 9. LENCANA POLISI DI DINDING DEPAN (Lantai 2)
    # Dasar Putih
    pts_shield_w = [
        (-15, 61, 80), (15, 61, 80),
        (15, 61, 60), (0, 61, 50), (-15, 61, 60)
    ]
    poly(FRAME, pts_shield_w, 2)
    
    # Dalam Biru Dongker
    pts_shield_b = [
        (-12, 61, 78), (12, 61, 78),
        (12, 61, 62), (0, 61, 54), (-12, 61, 62)
    ]
    poly(ROOF_TOP, pts_shield_b, 0)

    # Bintang 5 Sudut di Dalam Lencana
    pts_bintang = []
    for i in range(10):
        r = 5 * scale if i % 2 == 0 else 2 * scale
        ang = math.radians(i * 36 - 90)
        pts_bintang.append((r * math.cos(ang), 61, 66 - r * math.sin(ang)))
    poly(FRAME, pts_bintang, 0)