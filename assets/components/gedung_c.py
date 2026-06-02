import pygame

SCALE = 1.4  # Faktor pembesaran Gedung C

def iso_pt(cx, cy, x, y, z):
    """Mengonversi koordinat 3D (x, y, z) ke kordinat 2D isometrik layar"""
    x, y, z = x * SCALE, y * SCALE, z * SCALE
    # Rasio isometrik standar 2:1
    sx = cx + (x - y) * 2
    sy = cy + (x + y) * 1 - z
    return (sx, sy)

def draw_block(surface, cx, cy, x, y, z, w, d, h, c_top, c_left, c_right):
    """Menggambar blok 3D isometrik dasar dengan Wajah Depan yang benar"""
    # Titik bawah
    b0 = iso_pt(cx, cy, x, y, z)
    b1 = iso_pt(cx, cy, x+w, y, z)
    b2 = iso_pt(cx, cy, x+w, y+d, z)
    b3 = iso_pt(cx, cy, x, y+d, z)

    # Titik atas
    t0 = iso_pt(cx, cy, x, y, z+h)
    t1 = iso_pt(cx, cy, x+w, y, z+h)
    t2 = iso_pt(cx, cy, x+w, y+d, z+h)
    t3 = iso_pt(cx, cy, x, y+d, z+h)

    # Wajah Kiri Depan (Bidang X, Y = y+d konstan)
    pygame.draw.polygon(surface, c_left, [b3, b2, t2, t3])
    
    # Wajah Kanan Depan (Bidang Y, X = x+w konstan)
    pygame.draw.polygon(surface, c_right, [b2, b1, t1, t2])
    
    # Wajah Atas (Bidang Z)
    pygame.draw.polygon(surface, c_top, [t0, t1, t2, t3])

def draw_front_left_window(surface, cx, cy, x, y, z, w_x, w_z, color):
    """Menggambar jendela pipih pada wajah kiri depan bangunan (Y konstan)"""
    b3 = iso_pt(cx, cy, x, y, z)
    b2 = iso_pt(cx, cy, x+w_x, y, z)
    t2 = iso_pt(cx, cy, x+w_x, y, z+w_z)
    t3 = iso_pt(cx, cy, x, y, z+w_z)
    pygame.draw.polygon(surface, color, [b3, b2, t2, t3])

def draw_front_right_window(surface, cx, cy, x, y, z, w_y, w_z, color):
    """Menggambar jendela pipih pada wajah kanan depan bangunan (X konstan)"""
    b2 = iso_pt(cx, cy, x, y+w_y, z)
    b1 = iso_pt(cx, cy, x, y, z)
    t1 = iso_pt(cx, cy, x, y, z+w_z)
    t2 = iso_pt(cx, cy, x, y+w_y, z+w_z)
    pygame.draw.polygon(surface, color, [b2, b1, t1, t2])

def draw_gedungC(screen, cx, cy, scale=1.0):
    local_scale = SCALE * scale
    
    def iso_pt(cx_dummy, cy_dummy, x, y, z):
        lx, ly, lz = x * local_scale, y * local_scale, z * local_scale
        sx = cx + (lx - ly) * 2
        sy = cy + (lx + ly) * 1 - lz
        return (sx, sy)

    def draw_block(surface, cx_dummy, cy_dummy, x, y, z, w, d, h, c_top, c_left, c_right):
        b0 = iso_pt(cx, cy, x, y, z)
        b1 = iso_pt(cx, cy, x+w, y, z)
        b2 = iso_pt(cx, cy, x+w, y+d, z)
        b3 = iso_pt(cx, cy, x, y+d, z)
        t0 = iso_pt(cx, cy, x, y, z+h)
        t1 = iso_pt(cx, cy, x+w, y, z+h)
        t2 = iso_pt(cx, cy, x+w, y+d, z+h)
        t3 = iso_pt(cx, cy, x, y+d, z+h)
        pygame.draw.polygon(surface, c_left, [b3, b2, t2, t3])
        pygame.draw.polygon(surface, c_right, [b2, b1, t1, t2])
        pygame.draw.polygon(surface, c_top, [t0, t1, t2, t3])

    def draw_front_left_window(surface, cx_dummy, cy_dummy, x, y, z, w_x, w_z, color):
        b3 = iso_pt(cx, cy, x, y, z)
        b2 = iso_pt(cx, cy, x+w_x, y, z)
        t2 = iso_pt(cx, cy, x+w_x, y, z+w_z)
        t3 = iso_pt(cx, cy, x, y, z+w_z)
        pygame.draw.polygon(surface, color, [b3, b2, t2, t3])

    def draw_front_right_window(surface, cx_dummy, cy_dummy, x, y, z, w_y, w_z, color):
        b2 = iso_pt(cx, cy, x, y+w_y, z)
        b1 = iso_pt(cx, cy, x, y, z)
        t1 = iso_pt(cx, cy, x, y, z+w_z)
        t2 = iso_pt(cx, cy, x, y+w_y, z+w_z)
        pygame.draw.polygon(surface, color, [b2, b1, t1, t2])

    # --- PALET WARNA ---
    # Tanah & Jalan
    C_BASE_T, C_BASE_L, C_BASE_R = (245, 245, 250), (215, 215, 220), (185, 185, 190)
    C_ROAD_T, C_ROAD_L, C_ROAD_R = (60, 60, 65), (45, 45, 50), (35, 35, 40)
    
    # Kaca Menara (Teal/Cyan)
    C_GLASS_T, C_GLASS_L, C_GLASS_R = (150, 230, 240), (80, 200, 215), (40, 150, 170)
    C_GLASS_LINE = (30, 130, 150)
    
    # Pilar Oranye/Kuning
    C_PIL_T, C_PIL_L, C_PIL_R = (240, 200, 120), (220, 160, 80), (180, 120, 50)
    
    # Beton Abu-abu (Sayap Gedung)
    C_CONC_T, C_CONC_L, C_CONC_R = (225, 230, 235), (185, 190, 195), (145, 150, 155)
    
    # Jendela Sayap Gedung
    C_WIN_L, C_WIN_R = (100, 210, 220), (60, 170, 180)

    # Pohon
    C_TREE_T, C_TREE_L, C_TREE_R = (130, 210, 100), (90, 180, 60), (60, 150, 40)
    C_TRUNK_L, C_TRUNK_R = (100, 70, 40), (70, 40, 20)

    # (Platform dasar, jalan raya, dan tanaman dihapus sesuai permintaan)

    # 3. STRUKTUR GEDUNG (Diurutkan dari belakang ke depan berdasarkan kedalaman Z/Isometrik)
    # PILAR BELAKANG
    draw_block(screen, cx, cy, 34, 34, 0, 12, 12, 200, C_PIL_T, C_PIL_L, C_PIL_R)
    
    # MENARA KACA UTAMA (x=40, y=40, w=40, d=40, h=180)
    draw_block(screen, cx, cy, 40, 40, 0, 40, 40, 180, C_GLASS_T, C_GLASS_L, C_GLASS_R)
    
    # Grid Garis Kaca pada Menara
    for z_line in range(15, 180, 15): # Garis Horizontal
        pygame.draw.line(screen, C_GLASS_LINE, iso_pt(cx,cy, 40, 80, z_line), iso_pt(cx,cy, 80, 80, z_line), 1)
        pygame.draw.line(screen, C_GLASS_LINE, iso_pt(cx,cy, 80, 40, z_line), iso_pt(cx,cy, 80, 80, z_line), 1)
    for line_offset in range(48, 80, 8):   # Garis Vertikal Wajah Kiri dan Kanan
        pygame.draw.line(screen, C_GLASS_LINE, iso_pt(cx,cy, line_offset, 80, 0), iso_pt(cx,cy, line_offset, 80, 180), 1)
        pygame.draw.line(screen, C_GLASS_LINE, iso_pt(cx,cy, 80, line_offset, 0), iso_pt(cx,cy, 80, line_offset, 180), 1)

    # 4. DETAIL ATAP MENARA UTAMA
    # Atap Menara (Rim Putih)
    draw_block(screen, cx, cy, 38, 38, 180, 44, 44, 10, C_CONC_T, C_CONC_L, C_CONC_R)
    # Area Dalam Atap (Cekungan Gelap)
    draw_block(screen, cx, cy, 42, 42, 180, 36, 36, 5, (120,125,130), (100,105,110), (80,85,90))

    # PINTU MASUK BAWAH
    draw_block(screen, cx, cy, 40, 55, 0, 12, 20, 15, C_CONC_T, C_CONC_L, C_CONC_R) # Kanopi Pintu
    draw_front_left_window(screen, cx, cy, 41, 75, 0, 10, 10, (20, 20, 25)) # Lubang Hitam Pintu

    # PILAR KANAN & KIRI
    draw_block(screen, cx, cy, 74, 34, 0, 12, 12, 200, C_PIL_T, C_PIL_L, C_PIL_R) # Kanan
    draw_block(screen, cx, cy, 34, 74, 0, 12, 12, 200, C_PIL_T, C_PIL_L, C_PIL_R) # Kiri

    # SAYAP KANAN (Beton Abu-abu) (Menempel pada Menara, tepat di tengah Pilar)
    draw_block(screen, cx, cy, 80, 50, 0, 24, 20, 100, C_CONC_T, C_CONC_L, C_CONC_R)
    # Jendela Sayap Kanan
    for r in range(5):
        for c in range(3):
            w_z = 15 + r * 15
            w_x = 80 + 3 + c * 7
            w_y = 50 + 2 + c * 6
            # Jendela Kiri (Front Left Face) -> Y konstan di 50+20=70
            draw_front_left_window(screen, cx, cy, w_x, 70, w_z, 5, 8, C_WIN_L)
            # Jendela Kanan (Front Right Face) -> X konstan di 80+24=104
            draw_front_right_window(screen, cx, cy, 104, w_y, w_z, 4, 8, C_WIN_R)
    # Atap Sayap Kanan
    draw_block(screen, cx, cy, 82, 52, 100, 20, 16, 2, (100,100,100), (80,80,80), (60,60,60))

    # SAYAP KIRI (Beton Abu-abu) (Menempel pada Menara, tepat di tengah Pilar)
    draw_block(screen, cx, cy, 50, 80, 0, 20, 24, 100, C_CONC_T, C_CONC_L, C_CONC_R)
    # Jendela Sayap Kiri
    for r in range(5):
        for c in range(3):
            w_z = 15 + r * 15
            w_x = 50 + 2 + c * 6
            w_y = 80 + 3 + c * 7
            # Jendela Kiri (Front Left Face) -> Y konstan di 80+24=104
            draw_front_left_window(screen, cx, cy, w_x, 104, w_z, 4, 8, C_WIN_L)
            # Jendela Kanan (Front Right Face) -> X konstan di 50+20=70
            draw_front_right_window(screen, cx, cy, 70, w_y, w_z, 5, 8, C_WIN_R)
    # Atap Sayap Kiri
    draw_block(screen, cx, cy, 52, 82, 100, 16, 20, 2, (100,100,100), (80,80,80), (60,60,60))

    # PILAR DEPAN UTAMA
    draw_block(screen, cx, cy, 74, 74, 0, 12, 12, 200, C_PIL_T, C_PIL_L, C_PIL_R)