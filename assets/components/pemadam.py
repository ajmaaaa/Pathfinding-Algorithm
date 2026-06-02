import pygame
import math

# ===================================================
# 1. PALET WARNA (Gedung Pemadam Kebakaran Modern)
# ===================================================
LINE         = (30, 32, 35)      # Outline gelap tipis
WALL_L       = (35, 36, 40)      # Sisi Kiri (Composite Panel - Dark Charcoal)
WALL_R       = (50, 52, 58)      # Sisi Kanan (Composite Panel - Charcoal/Black)
RED_L        = (185, 20, 25)     # Sisi Kiri (Accent Crimson Red)
RED_R        = (220, 30, 35)     # Sisi Kanan (Accent Crimson Red)
BLUE_L       = (20, 100, 200)    # Sisi Kiri (Blue Accent - Dikit Aja)
BLUE_R       = (30, 140, 255)    # Sisi Kanan (Blue Accent - Dikit Aja)
TRIM_L       = (210, 215, 220)   # Aluminium Silver (Kiri)
TRIM_R       = (240, 245, 250)   # Aluminium Silver (Kanan)
ROOF_TOP     = (25, 26, 28)      # Atap Beton Gelap
ROOF_IN      = (15, 16, 18)      # Inset Atap
WIN_BG       = (135, 210, 240)   # Kaca Tinted Cyan
FRAME        = (255, 255, 255)   # Bingkai putih
CONCRETE_TOP = (85, 88, 92)      # Aspal Jalan Masuk (Gelap Modern)
CONCRETE_L   = (70, 72, 75)      # Aspal Kiri
CONCRETE_R   = (55, 57, 60)      # Aspal Kanan
STRIPE_W     = (245, 245, 250)   # Garis Putih Solid Minimalis
SIREN_AMBER  = (255, 190, 0)     # Sirine LED Amber
SIREN_RED    = (255, 40, 40)     # Sirine Merah
STEEL_L      = (100, 105, 110)
STEEL_R      = (130, 135, 140)

def render_pemadam(layar, cx_pusat, cy_pusat, scale=1.0):
    """Render 2D Isometrik Murni untuk Gedung Pemadam Kebakaran Kontemporer"""

    def iso(x, y, z=0):
        scale_x, scale_y = 1.6 * scale, 0.8 * scale
        sx = cx_pusat + (x - y) * scale_x
        sy = cy_pusat + (x + y) * scale_y - z * scale
        return sx, sy

    def poly(warna, titik, ketebalan_outline=1):
        pts = [iso(p[0], p[1], p[2]) for p in titik]
        layar_polygon = pygame.draw.polygon(layar, warna, pts)
        if ketebalan_outline > 0:
            pygame.draw.polygon(layar, LINE, pts, max(1, int(ketebalan_outline * scale)))

    def draw_box(x, y, z, dx, dy, dz, col_left, col_right, col_top, outline=1):
        # Kiri
        poly(col_left, [(x, y+dy, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)], outline)
        # Kanan
        poly(col_right, [(x+dx, y, z), (x+dx, y+dy, z), (x+dx, y+dy, z+dz), (x+dx, y, z+dz)], outline)
        # Atas
        poly(col_top, [(x, y, z+dz), (x+dx, y, z+dz), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)], outline)

    # Menggambar panel kaca transparan premium
    def draw_glass_panel(points_3d, col_rgba=(150, 220, 255, 110), outline_thick=1):
        pts_2d = [iso(x, y, z) for x, y, z in points_3d]
        xs = [p[0] for p in pts_2d]
        ys = [p[1] for p in pts_2d]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = int(max_x - min_x) + 2
        h = int(max_y - min_y) + 2
        if w > 0 and h > 0:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            rel_pts = [(p[0] - min_x, p[1] - min_y) for p in pts_2d]
            pygame.draw.polygon(surf, col_rgba, rel_pts)
            if outline_thick > 0:
                pygame.draw.polygon(surf, LINE, rel_pts, max(1, int(outline_thick * scale)))
            layar.blit(surf, (min_x, min_y))

    # Helper untuk menggambar Pintu Garasi Kaca Sekat Modern (Sectional Glazed Door)
    def draw_sectional_door(x1, x2, y, z1, z2):
        # Frame luar hitam
        poly(LINE, [(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)], 2)
        
        w_door = x2 - x1
        h_door = z2 - z1
        
        # Grid sekat kaca: 4 kolom, 4 baris
        cols = 4
        rows = 4
        for r in range(rows):
            for c in range(cols):
                px1 = x1 + w_door * (c / cols) + 1.5
                px2 = x1 + w_door * ((c + 1) / cols) - 1.5
                pz1 = z1 + h_door * (r / rows) + 1.5
                pz2 = z1 + h_door * ((r + 1) / rows) - 1.5
                poly(WIN_BG, [(px1, y, pz1), (px2, y, pz1), (px2, y, pz2), (px1, y, pz2)], 1)

    # ========================================================
    # URUTAN PENGGAMBARAN (PAINTER'S ALGORITHM)
    # Objek paling BELAKANG (y kecil) digambar DULUAN,
    # agar objek DEPAN (y besar) menutupinya secara benar.
    # ========================================================

    # 1. PLATFORM ASPAL JALAN MASUK (DRIVEWAY MODERN) - Paling Bawah
    draw_box(-45, -35, -2, 90, 90, 2, CONCRETE_L, CONCRETE_R, CONCRETE_TOP)

    # Marka Parkir Putih Minimalis untuk Mobil Pemadam
    # Bay 1 (Kiri)
    poly(STRIPE_W, [(-32, 35, 0), (-8, 35, 0), (-8, 36, 0), (-32, 36, 0)], 0)
    poly(STRIPE_W, [(-32, 52, 0), (-8, 52, 0), (-8, 53, 0), (-32, 53, 0)], 0)
    poly(STRIPE_W, [(-32, 35, 0), (-32, 52, 0), (-31, 52, 0), (-31, 35, 0)], 0)
    poly(STRIPE_W, [(-8, 35, 0), (-8, 52, 0), (-7, 52, 0), (-7, 35, 0)], 0)
    # Bay 2 (Kanan)
    poly(STRIPE_W, [(8, 35, 0), (32, 35, 0), (32, 36, 0), (8, 36, 0)], 0)
    poly(STRIPE_W, [(8, 52, 0), (32, 52, 0), (32, 53, 0), (8, 53, 0)], 0)
    poly(STRIPE_W, [(8, 35, 0), (8, 52, 0), (9, 52, 0), (9, 35, 0)], 0)
    poly(STRIPE_W, [(32, 35, 0), (32, 52, 0), (33, 52, 0), (33, 35, 0)], 0)

    # 2. MENARA PENGAWAS (DIGAMBAR DULUAN karena di BELAKANG, y = -35..-15)
    # Badan menara: x dari 20 ke 40, y dari -35 ke -15, z = 0 ke 120
    draw_box(20, -35, 0, 20, 20, 120, WALL_L, WALL_R, ROOF_TOP)

    # Strip Lampu LED Biru Vertikal di Sisi Depan Menara (y = -15)
    draw_box(28, -15, 20, 2, 0.2, 90, BLUE_L, BLUE_R, BLUE_R)

    # Tangga Logam Vertikal (Ladder) di Dinding Kiri Menara (y = -35)
    # Digambar sekarang karena menara sudah ada, dan akan tertutup oleh bangunan depan
    pygame.draw.line(layar, LINE, iso(28, -35, 10), iso(28, -35, 115), max(1, int(2 * scale)))
    pygame.draw.line(layar, LINE, iso(31, -35, 10), iso(31, -35, 115), max(1, int(2 * scale)))
    for sz in range(14, 115, 8):
        pygame.draw.line(layar, LINE, iso(28, -35, sz), iso(31, -35, sz), max(1, int(2 * scale)))

    # 3. LANTAI 1 GEDUNG UTAMA (Digambar SETELAH menara agar menutupinya)
    # Bagian Garasi Charcoal (x: -40..15, y: -35..35)
    draw_box(-40, -35, 0, 55, 70, 42, WALL_L, WALL_R, ROOF_TOP)

    # Bagian Kantor Crimson Red (x: 15..40, y: -35..35) - menutupi menara di belakangnya
    draw_box(15, -35, 0, 25, 70, 42, RED_L, RED_R, ROOF_TOP)

    # Pintu Garasi Kaca Sekat 1 (Kiri)
    draw_sectional_door(-34, -6, 35, 2, 30)
    # Pintu Garasi Kaca Sekat 2 (Kanan)
    draw_sectional_door(6, 34, 35, 2, 30)

    # Strip Lampu LED Biru Horizontal di atas Pintu Garasi
    draw_box(-40, 35, 32, 55, 0.2, 2, BLUE_L, BLUE_R, BLUE_R)

    # Pintu Lobby Kaca Tinggi (x = 40, y: 10..25)
    draw_glass_panel([(40, 10, 0), (40, 25, 0), (40, 25, 30), (40, 10, 30)], (150, 220, 255, 140), 2)
    pygame.draw.line(layar, FRAME, iso(40, 17.5, 0), iso(40, 17.5, 30), max(1, int(2 * scale)))

    # Jendela Sudut Kantor Depan (x = 40, y: -25..-5)
    draw_glass_panel([(40, -25, 12), (40, -5, 12), (40, -5, 30), (40, -25, 30)], (150, 220, 255, 130), 2)

    # Kanopi Aluminium Kantilever di atas Pintu Garasi
    draw_box(-38, 33, 34, 74, 10, 2, TRIM_L, TRIM_R, TRIM_R)

    # 4. LANTAI 2 GEDUNG UTAMA (Digambar SETELAH lantai 1)
    # Balok Kiri Charcoal (x: -40..15, y: -35..18, z = 42..76)
    draw_box(-40, -35, 42, 55, 53, 34, WALL_L, WALL_R, ROOF_TOP)

    # Balok Kanan Red (x: 15..40, y: -15..35, z = 42..76) - menutupi menara di belakangnya
    draw_box(15, -15, 42, 25, 50, 34, RED_L, RED_R, ROOF_TOP)

    # Atap Parapet Dalam
    poly(ROOF_IN, [(-38, -33, 76), (13, -33, 76), (13, 16, 76), (-38, 16, 76)], 0)
    poly(ROOF_IN, [(17, -13, 76), (38, -13, 76), (38, 33, 76), (17, 33, 76)], 0)

    # Pagar Kaca Balkon (y dari 18 ke 35, x dari -40 ke 15)
    draw_glass_panel([(-40, 35, 42), (15, 35, 42), (15, 35, 51), (-40, 35, 51)], (170, 230, 255, 120), 1)
    draw_glass_panel([(15, 18, 42), (15, 35, 42), (15, 35, 51), (15, 18, 51)], (170, 230, 255, 120), 1)
    for bx in range(-40, 16, 11):
        pygame.draw.line(layar, LINE, iso(bx, 35, 42), iso(bx, 35, 51), max(1, int(2 * scale)))
    for by in range(18, 36, 6):
        pygame.draw.line(layar, LINE, iso(15, by, 42), iso(15, by, 51), max(1, int(2 * scale)))

    # Jendela Panoramic Dinding Balkon (y = 18)
    draw_glass_panel([(-32, 18, 48), (8, 18, 48), (8, 18, 70), (-32, 18, 70)], (150, 220, 255, 130), 2)
    pygame.draw.line(layar, FRAME, iso(-18, 18, 48), iso(-18, 18, 70), max(1, int(scale)))
    pygame.draw.line(layar, FRAME, iso(-6, 18, 48), iso(-6, 18, 70), max(1, int(scale)))

    # Jendela Dinding Kanan Lantai 2 (x = 40)
    draw_glass_panel([(40, 0, 48), (40, 22, 48), (40, 22, 70), (40, 0, 70)], (150, 220, 255, 130), 2)
    pygame.draw.line(layar, FRAME, iso(40, 11, 48), iso(40, 11, 70), max(1, int(scale)))

    # 5. BAGIAN ATAS MENARA (z > 76, di atas gedung utama - digambar TERAKHIR)
    # Trim Aluminium Silver Atas Menara (z = 120..123)
    draw_box(19, -36, 120, 22, 22, 3, TRIM_L, TRIM_R, TRIM_R)

    # 4 Tiang Penyangga Dek Pengamatan
    pygame.draw.line(layar, LINE, iso(21, -34, 123), iso(21, -34, 133), max(1, int(3 * scale)))
    pygame.draw.line(layar, LINE, iso(39, -34, 123), iso(39, -34, 133), max(1, int(3 * scale)))
    pygame.draw.line(layar, LINE, iso(39, -16, 123), iso(39, -16, 133), max(1, int(3 * scale)))
    pygame.draw.line(layar, LINE, iso(21, -16, 123), iso(21, -16, 133), max(1, int(3 * scale)))

    # Sirine LED Amber di Puncak Menara
    draw_box(27, -28, 123, 6, 6, 7, STEEL_L, STEEL_R, STEEL_L)
    draw_box(26, -29, 130, 8, 8, 4, SIREN_AMBER, SIREN_AMBER, (255, 240, 150))

    # Efek Pendaran Sirine (Amber Glow)
    sir_pos = iso(30, -25, 132)
    siren_glow = pygame.Surface((int(36 * scale), int(18 * scale)), pygame.SRCALPHA)
    pygame.draw.ellipse(siren_glow, (255, 200, 0, 85), (0, 0, int(36 * scale), int(18 * scale)))
    layar.blit(siren_glow, (sir_pos[0] - 18 * scale, sir_pos[1] - 9 * scale))

    # Atap Kanopi Dek Pengamatan Menara (z = 133..136)
    draw_box(20, -35, 133, 20, 20, 3, TRIM_L, TRIM_R, TRIM_R)

    # 6. PAPAN NAMA "FIRE STATION" DI ATAS KANOPI GARASI
    poly(ROOF_TOP, [(-18, 35.1, 36), (18, 35.1, 36), (18, 35.1, 42), (-18, 35.1, 42)], 1)
    try:
        font = pygame.font.SysFont("arial", int(9 * scale), bold=True)
        text_surf = font.render("F I R E   S T A T I O N", True, (255, 255, 255))
        rotated_text = pygame.transform.rotate(text_surf, -26.565)
        txt_pos = iso(0, 35.3, 38.5)
        text_rect = rotated_text.get_rect(center=(int(txt_pos[0]), int(txt_pos[1])))
        layar.blit(rotated_text, text_rect)
    except Exception as e:
        pass

    # 7. HYDRANT MERAH DI SUDUT TAMAN
    draw_box(-43, 45, 0, 4, 4, 10, SIREN_RED, SIREN_RED, SIREN_RED)
    draw_box(-44, 44, 10, 6, 6, 3, TRIM_L, TRIM_R, TRIM_R)


class Pemadam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0

    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_pemadam(screen, self.x + 16 * scale, self.y - 8 * scale, scale=scale)
