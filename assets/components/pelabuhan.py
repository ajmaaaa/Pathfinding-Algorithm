import pygame

def render_pelabuhan(screen, cx, cy, direction='SE'):
    # --- SISTEM KOORDINAT ISOMETRIK ---
    
    def iso(x, y, z):
        sx = cx + (x - y) * 18
        sy = cy - (x + y) * 9 - z * 16
        return sx, sy

    # --- FUNGSI PENGGAMBAR KUBUS ISOMETRIK ---
    def draw_iso_cube(x, y, z, w, d, h, c_top, c_left, c_right):
        p0 = iso(x, y, z)
        p1 = iso(x+w, y, z)
        p3 = iso(x, y+d, z)
        p4 = iso(x, y, z+h)
        p5 = iso(x+w, y, z+h)
        p6 = iso(x+w, y+d, z+h)
        p7 = iso(x, y+d, z+h)

        outline = (60, 65, 70)

        # Sisi Atas
        pygame.draw.polygon(screen, c_top, [p4, p5, p6, p7])
        pygame.draw.polygon(screen, outline, [p4, p5, p6, p7], 1)
        # Sisi Kiri Depan
        pygame.draw.polygon(screen, c_left, [p0, p3, p7, p4])
        pygame.draw.polygon(screen, outline, [p0, p3, p7, p4], 1)
        # Sisi Kanan Depan
        pygame.draw.polygon(screen, c_right, [p0, p1, p5, p4])
        pygame.draw.polygon(screen, outline, [p0, p1, p5, p4], 1)

    def draw_container(x, y, z, colors):
        c_top, c_left, c_right = colors
        w, d, h = 1.2, 3.0, 1.5 # Dimensi vertikal
        draw_iso_cube(x, y, z, w, d, h, c_top, c_left, c_right)

    # --- PALET WARNA ---
    C_PLAT_TOP = (145, 153, 161)
    C_PLAT_LEFT = (110, 118, 126)
    C_PLAT_RIGHT = (85, 92, 100)

    C_RED = ((220, 70, 70), (180, 40, 40), (130, 20, 20))
    C_BLUE = ((70, 140, 210), (40, 100, 170), (20, 60, 120))
    C_GREEN = ((90, 170, 90), (40, 130, 40), (20, 80, 20))
    C_YELLOW = ((240, 200, 60), (200, 160, 30), (150, 110, 15))

    B_TOP = (235, 240, 245)
    B_LEFT = (195, 200, 210)
    B_RIGHT = (145, 150, 160)
    BL_TOP = (85, 140, 190)
    BL_LEFT = (60, 110, 160)
    BL_RIGHT = (40, 80, 120)

    O_TOP = (245, 140, 50)
    O_LEFT = (210, 110, 30)
    O_RIGHT = (160, 70, 15)

    # ==========================================
    # 1. PLATFORM ABU-ABU (Bentuk Angka 7 - Halaman Diperkecil)
    # ==========================================
    pts_top = [(5, 25), (20, 25), (20, 0), (14, 0), (14, 19), (5, 19)]
    poly_top = [iso(x, y, 1) for x, y in pts_top]
    pygame.draw.polygon(screen, C_PLAT_TOP, poly_top)
    pygame.draw.polygon(screen, (100, 100, 100), poly_top, 1)

    # Dinding Samping Kanan Depan 1 (Y=0, X=14..20)
    fr1_top = [iso(x, 0, 1) for x in range(14, 21)]
    fr1_bot = [iso(x, 0, 0) for x in range(20, 13, -1)]
    pygame.draw.polygon(screen, C_PLAT_RIGHT, fr1_top + fr1_bot)

    # Dinding Samping Kanan Depan 2 (Y=19, X=5..14)
    fr2_top = [iso(x, 19, 1) for x in range(5, 15)]
    fr2_bot = [iso(x, 19, 0) for x in range(14, 4, -1)]
    pygame.draw.polygon(screen, C_PLAT_RIGHT, fr2_top + fr2_bot)

    # Dinding Samping Kiri Depan 1 (X=14, Y=0..19)
    fl1_top = [iso(14, y, 1) for y in range(0, 20)]
    fl1_bot = [iso(14, y, 0) for y in range(19, -1, -1)]
    pygame.draw.polygon(screen, C_PLAT_LEFT, fl1_top + fl1_bot)

    # Dinding Samping Kiri Depan 2 (X=5, Y=19..25)
    fl2_top = [iso(5, y, 1) for y in range(19, 26)]
    fl2_bot = [iso(5, y, 0) for y in range(25, 18, -1)]
    pygame.draw.polygon(screen, C_PLAT_LEFT, fl2_top + fl2_bot)

    # Ban Pelindung Kapal (Bumpers)
    for bx in range(15, 20, 3):
        px, py = iso(bx, -0.2, 0.5)
        pygame.draw.ellipse(screen, (30,30,30), (px-6, py-8, 12, 16))
        pygame.draw.ellipse(screen, (10,10,10), (px-3, py-5, 6, 10))
        
    for bx in range(6, 14, 3):
        px, py = iso(bx, 18.8, 0.5)
        pygame.draw.ellipse(screen, (30,30,30), (px-6, py-8, 12, 16))
        pygame.draw.ellipse(screen, (10,10,10), (px-3, py-5, 6, 10))

    for by in range(2, 19, 3):
        px, py = iso(13.8, by, 0.5)
        pygame.draw.ellipse(screen, (30,30,30), (px-6, py-8, 12, 16))
        pygame.draw.ellipse(screen, (10,10,10), (px-3, py-5, 6, 10))

    for by in range(20, 25, 3):
        px, py = iso(4.8, by, 0.5)
        pygame.draw.ellipse(screen, (30,30,30), (px-6, py-8, 12, 16))
        pygame.draw.ellipse(screen, (10,10,10), (px-3, py-5, 6, 10))

    # ==========================================
    # URUTAN RENDERING OBJEK (Belakang ke Depan)
    # ==========================================

    # 2. TOWER CRANE (Desain Liebherr, Kuning)
    # Urutan render disesuaikan (dari belakang ke depan) untuk kedalaman 3D yang benar
    
    # Counter-Jib (Lengan Belakang) - Belakang (Y=22.0)
    draw_iso_cube(10.6, 22.0, 14.5, 0.8, 4.0, 0.6, C_YELLOW[0], C_YELLOW[1], C_YELLOW[2])
    
    # Counterweights (Beban Penyeimbang) - Tepat di ujung lengan belakang (Y=24.5)
    # X dan W disamakan dengan lengan belakang agar tidak menonjol ke samping
    draw_iso_cube(10.6, 24.0, 14.4, 0.8, 1.5, 0.9, B_TOP, B_LEFT, B_RIGHT)
    
    # Pondasi / Base Weights
    draw_iso_cube(9.5, 20.0, 1.0, 3.0, 3.0, 0.5, B_TOP, B_LEFT, B_RIGHT)
    draw_iso_cube(10.0, 20.5, 1.5, 2.0, 2.0, 0.5, B_TOP, B_LEFT, B_RIGHT)
    
    # Mast (Tiang Utama)
    draw_iso_cube(10.5, 21.0, 2.0, 1.0, 1.0, 12.0, C_YELLOW[0], C_YELLOW[1], C_YELLOW[2])

    # Slewing Ring (Cincin Putar)
    draw_iso_cube(10.4, 20.9, 14.0, 1.2, 1.2, 0.5, (50,50,50), (40,40,40), (30,30,30))

    # Operator Cabin (Di depan tiang)
    draw_iso_cube(10.5, 20.2, 12.8, 1.0, 0.8, 1.2, (50,50,50), (200,245,255), (150,215,245))
    
    # Apex (Puncak Tiang)
    draw_iso_cube(10.5, 21.0, 14.5, 1.0, 1.0, 3.0, C_YELLOW[0], C_YELLOW[1], C_YELLOW[2])
    
    # Jib (Lengan Utama) - Kotak Kuning Panjang yang Rapi (Paling Depan)
    draw_iso_cube(10.6, 5.0, 14.5, 0.8, 16.0, 0.6, C_YELLOW[0], C_YELLOW[1], C_YELLOW[2])
    
    # Tension Cables (Kabel Baja Penahan 3D)
    apex_l = iso(10.6, 21.5, 17.5)
    apex_r = iso(11.4, 21.5, 17.5)
    
    # Kabel ke Jib Depan
    pygame.draw.line(screen, (40, 40, 40), apex_l, iso(10.6, 16.0, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_r, iso(11.4, 16.0, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_l, iso(10.6, 10.0, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_r, iso(11.4, 10.0, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_l, iso(10.6, 6.0, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_r, iso(11.4, 6.0, 15.1), 2)
    
    # Kabel ke Counter-Jib Belakang
    pygame.draw.line(screen, (40, 40, 40), apex_l, iso(10.6, 25.5, 15.1), 2)
    pygame.draw.line(screen, (40, 40, 40), apex_r, iso(11.4, 25.5, 15.1), 2)
    


    # 3. KELOMPOK KONTAINER BELAKANG (Y=15)
    ct_data_1 = [
        (17.1, 15, 1, C_GREEN), (15.8, 15, 1, C_BLUE), (14.5, 15, 1, C_RED),
        (17.1, 15, 2.5, C_YELLOW), (15.8, 15, 2.5, C_RED), (14.5, 15, 2.5, C_BLUE),
        (15.8, 15, 4.0, C_BLUE), (14.5, 15, 4.0, C_GREEN),
    ]
    for d in ct_data_1:
        draw_container(d[0], d[1], d[2], d[3])

    # 4. BANGUNAN KANTOR / TOWER KONTROL (Di Sayap Kiri Horizontal)
    draw_iso_cube(5.0, 20.0, 1.0, 3.0, 3.0, 1.5, B_TOP, B_LEFT, B_RIGHT)      
    draw_iso_cube(5.0, 20.0, 2.5, 3.0, 3.0, 2.0, BL_TOP, BL_LEFT, BL_RIGHT)  
    draw_iso_cube(5.0, 20.0, 4.5, 3.0, 3.0, 1.5, B_TOP, B_LEFT, B_RIGHT)      
    draw_iso_cube(4.8, 19.8, 6.0, 3.4, 3.4, 0.4, (150,155,160), (120,125,130), (90,95,100)) 

    # Radar Atas Kantor
    draw_iso_cube(6.2, 21.2, 6.4, 0.6, 0.6, 1.5, C_RED[0], C_RED[1], C_RED[2])
    rx, ry = iso(6.5, 21.5, 8.2)
    pygame.draw.circle(screen, (250,100,100), (int(rx), int(ry)), 8)
    pygame.draw.circle(screen, C_RED[1], (int(rx), int(ry)), 8, 2)

    # Kaca jendela kantor
    for wx in [5.4, 6.5, 7.6]:
        draw_iso_cube(wx, 19.99, 2.8, 0.5, 0.0, 1.2, (0,0,0), (0,0,0), (200,245,255)) 
        draw_iso_cube(wx, 19.99, 4.8, 0.5, 0.0, 1.0, (0,0,0), (0,0,0), (200,245,255)) 
    for wy in [20.4, 21.5, 22.6]:
        draw_iso_cube(4.99, wy, 2.8, 0.0, 0.5, 1.2, (0,0,0), (160,215,245), (0,0,0)) 
        draw_iso_cube(4.99, wy, 4.8, 0.0, 0.5, 1.0, (0,0,0), (160,215,245), (0,0,0)) 

    # 5. KELOMPOK KONTAINER TENGAH (Y=11)
    ct_data_2 = [
        (17.1, 11, 1, C_BLUE), (15.8, 11, 1, C_RED), (14.5, 11, 1, C_YELLOW),
        (17.1, 11, 2.5, C_BLUE), (15.8, 11, 2.5, C_GREEN), (14.5, 11, 2.5, C_RED),
    ]
    for d in ct_data_2:
        draw_container(d[0], d[1], d[2], d[3])

    # 7. KELOMPOK KONTAINER DEPAN (Y=7)
    ct_data_3 = [
        (17.1, 7, 1, C_RED), (15.8, 7, 1, C_YELLOW), (14.5, 7, 1, C_GREEN),
        (15.8, 7, 2.5, C_YELLOW), (14.5, 7, 2.5, C_BLUE),
    ]
    for d in ct_data_3:
        draw_container(d[0], d[1], d[2], d[3])