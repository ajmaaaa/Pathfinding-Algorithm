import pygame

# ===========================================================================
# PALET WARNA — BANDARA
# ===========================================================================

# Tanah & Infrastruktur
GRASS_F     = (148, 200, 108)
RUNWAY_TOP  = (85,  85,  82)
RUNWAY_L    = (68,  68,  66)
RUNWAY_R    = (55,  55,  52)
TAXIWAY_TOP = (98,  98,  95)
TAXIWAY_L   = (82,  82,  79)
TAXIWAY_R   = (68,  68,  65)
APRON_TOP   = (115, 115, 110)
APRON_L     = (95,  95,  91)
APRON_R     = (78,  78,  75)
ROAD_TOP    = (118, 115, 110)
ROAD_L      = (98,  95,  90)
ROAD_R      = (82,  80,  75)
CURB_TOP    = (205, 202, 195)
CURB_L      = (178, 175, 168)
CURB_R      = (152, 149, 142)
MARKA_W     = (255, 255, 255)
MARKA_Y     = (252, 228, 45)
LIGHT_COL   = (255, 248, 180)

# Terminal
TERM_L      = (238, 234, 226)
TERM_R      = (208, 204, 196)
TERM_TOP    = (250, 246, 238)
CONC_L      = (230, 226, 218)
CONC_R      = (200, 196, 188)
CONC_TOP    = (242, 238, 230)
GLASS_L     = (138, 198, 228)
GLASS_R     = (98,  160, 195)
GLASS_TOP   = (168, 215, 238)
WIN_FRAME   = (255, 255, 255)
ACCENT_L    = (52,  108, 178)
ACCENT_R    = (35,  82,  148)
ROOF_L      = (135, 152, 168)
ROOF_R      = (105, 122, 138)
ROOF_TOP    = (158, 175, 192)
CANOPY_L    = (50,  105, 172)
CANOPY_R    = (35,  80,  142)
CANOPY_TOP  = (65,  122, 188)
DOOR_COL    = (80,  155, 205)

# ATC Tower
ATC_L       = (222, 218, 210)
ATC_R       = (192, 188, 180)
ATC_TOP     = (235, 230, 222)
CAB_L       = (95,  182, 218)
CAB_R       = (65,  148, 188)
CAB_TOP     = (122, 198, 228)
RADAR_COL   = (75,  78,  85)

# Garbarata
JB_L        = (198, 195, 188)
JB_R        = (168, 165, 158)
JB_TOP      = (212, 208, 200)

# Pesawat
PL_BODY_L   = (240, 240, 245)
PL_BODY_R   = (210, 212, 218)
PL_BODY_T   = (252, 252, 255)
PL_WING_L   = (215, 218, 225)
PL_WING_R   = (185, 188, 195)
PL_ENG_L    = (158, 160, 168)
PL_ENG_R    = (128, 130, 138)
PL_ENG_T    = (175, 178, 185)
PL_TAIL     = (28,  75,  178)
PL_STRIPE   = (28,  75,  178)
PL_WIN      = (155, 208, 235)
PL_NOSE_L   = (232, 232, 238)
PL_NOSE_R   = (202, 202, 208)

# Misc
POLE_COL    = (152, 155, 160)
PRICE_BG    = (28,  28,  32)
LINE_COL    = (45,  45,  45)


def render_bandara(screen, cx, cy, scale=1.0):
    def iso(x, y, z):
        sx = cx + (x - y) * 1.6 * scale
        sy = cy + ((x + y) * 0.8 - z) * scale
        return sx, sy

    def draw_poly(pts3, color, outline=True, lw=2):
        pts2 = [iso(x, y, z) for x, y, z in pts3]
        pygame.draw.polygon(screen, color, pts2)
        if outline:
            pygame.draw.polygon(screen, LINE_COL, pts2, lw)

    def draw_block(x1, x2, y1, y2, z1, z2, ct, cf, cs):
        draw_poly([(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)], ct)
        draw_poly([(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)], cf)
        draw_poly([(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)], cs)

    def ln(x1,y1,z1, x2,y2,z2, col, w=2):
        pygame.draw.line(screen, col, iso(x1,y1,z1), iso(x2,y2,z2), w)

    def glass_left(x, y, z, w=20, h=28):
        draw_poly([(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)], GLASS_L)
        ln(x+w/2,y,z, x+w/2,y,z+h, WIN_FRAME, 1)
        ln(x,y,z+h*0.55, x+w,y,z+h*0.55, WIN_FRAME, 1)

    def glass_right(x, y, z, w=20, h=28):
        draw_poly([(x,y,z),(x,y+w,z),(x,y+w,z+h),(x,y,z+h)], GLASS_R)
        ln(x,y+w/2,z, x,y+w/2,z+h, WIN_FRAME, 1)
        ln(x,y,z+h*0.55, x,y+w,z+h*0.55, WIN_FRAME, 1)

    # =======================================================================
    # LAYOUT KOORDINAT 3D
    #   Sumbu x  : kanan-kiri (iso depan-kanan)
    #   Sumbu y  : kedalaman  (iso belakang-kiri)
    #   Sumbu z  : ketinggian
    #
    #   Taxiway      x=[0..650],   y=[365..435]
    #   Apron        x=[30..530],  y=[205..360]
    #   Terminal     x=[70..430],  y=[55..185]
    #   Concourse kiri x=[88..132], y=[185..260] (finger pier)
    #   Concourse kanan x=[368..412], y=[185..260]
    #   ATC Tower    x=[455..505], y=[65..120]
    #   Taxiway loop x=[-25..585], y=[-55..435]
    # =======================================================================

    # 0. BASE CEMENT PLATFORM (Rectangle)
    C_PLAT_TOP = (195, 200, 205)
    C_PLAT_LEFT = (175, 180, 185)
    C_PLAT_RIGHT = (155, 160, 165)
    
    # Top face of platform
    draw_poly([(-40, -70, 0), (630, -70, 0), (630, 580, 0), (-40, 580, 0)], C_PLAT_TOP)
    # Bottom-right side: x = 630, y from -70 to 580
    draw_poly([(630, -70, -8), (630, 580, -8), (630, 580, 0), (630, -70, 0)], C_PLAT_RIGHT)
    # Bottom-left side: y = 580, x from 630 to -40
    draw_poly([(630, 580, -8), (-40, 580, -8), (-40, 580, 0), (630, 580, 0)], C_PLAT_LEFT)

    # -----------------------------------------------------------------------
    # 2. TAXIWAY
    # -----------------------------------------------------------------------
    # Diperpendek ke x=540 agar menyatu langsung dengan landasan pacu baru di kanan
    draw_poly([(0,365,0),(540,365,0),(540,435,0),(0,435,0)], TAXIWAY_TOP)

    # Connector samping untuk membentuk loop taxiway di luar terminal/apron (Sisi Kiri saja).
    # Sisi kanan loop ditiadakan karena digantikan langsung oleh landasan pacu (runway).
    draw_poly([(-25,0,0),(20,0,0),(20,365,0),(-25,365,0)], TAXIWAY_TOP)

    # -----------------------------------------------------------------------
    # 3. APRON
    # -----------------------------------------------------------------------
    draw_poly([(30,205,0),(530,205,0),(530,360,0),(30,360,0)], APRON_TOP)

    # Garis parkir (lead-in line) per gate — 4 gate
    for gate_x in [110, 215, 325, 430]:
        ln(gate_x, 220, 1, gate_x, 345, 1, MARKA_Y, 2)           # center
        ln(gate_x-32, 245, 1, gate_x+32, 245, 1, MARKA_Y, 2)     # stop bar

    # Taxiway dari apron ke taxiway utama (connector)
    draw_poly([(210,358,0),(340,358,0),(340,368,0),(210,368,0)], TAXIWAY_TOP)
    ln(275, 358, 1, 275, 368, 1, MARKA_Y, 2)

    # -----------------------------------------------------------------------
    # 4. TAXIWAY BELAKANG  x:[-25..540], y:[-55..0]
    # -----------------------------------------------------------------------
    # Diperpendek ke x=540 agar menyatu langsung dengan landasan pacu baru di kanan
    draw_poly([(-25,-55,0),(540,-55,0),(540,0,0),(-25,0,0)], TAXIWAY_TOP)

    # Rapikan sambungan internal agar taxiway loop terbaca sebagai satu jalur (Hanya Kiri).
    for x1, x2, y1, y2 in [
        (-25, 20, -55, 5),
        (-25, 20, 360, 435),
    ]:
        draw_poly([(x1,y1,1),(x2,y1,1),(x2,y2,1),(x1,y2,1)], TAXIWAY_TOP, outline=False)

    # Marka garis pemandu kuning (Taxiway centerlines)
    ln(-3, -28, 1, 580, -28, 1, MARKA_Y, 3)  # Lurus langsung masuk ke runway center x=580
    ln(-3, -28, 1, -3, 400, 1, MARKA_Y, 3)
    ln(-3, 400, 1, 580, 400, 1, MARKA_Y, 3)  # Lurus langsung masuk ke runway center x=580

    # -----------------------------------------------------------------------
    # 4b. LANDASAN PACU (RUNWAY) & MARKA (SISI KANAN MENGGANTIKAN LOOP KANAN)
    # -----------------------------------------------------------------------
    # Runway Base Kanan (x: 540 s.d 620, y: -55 s.d 580)
    # Ujung atas sejajar taxiway belakang (y=-55), ujung bawah memanjang (y=580)
    draw_poly([(540,-55,0),(620,-55,0),(620,580,0),(540,580,0)], RUNWAY_TOP)
    
    # Marka Garis Tepi Runway Kanan (Solid White)
    ln(545, -55, 1, 545, 580, 1, MARKA_W, 2)
    ln(615, -55, 1, 615, 580, 1, MARKA_W, 2)
    
    # Marka Tengah Runway Kanan (Dashed White)
    for ry in range(-20, 540, 60):
        ln(580, ry, 1, 580, ry + 30, 1, MARKA_W, 3)
        
    # Piano Threshold Markings Kanan (Ujung Belakang & Depan)
    for rx in range(550, 611, 6):
        ln(rx, -45, 1, rx, -20, 1, MARKA_W, 3) # Belakang (y: -45 s.d -20)
        ln(rx, 545, 1, rx, 570, 1, MARKA_W, 3) # Depan (y: 545 s.d 570)

    # -----------------------------------------------------------------------
    # 6. TERMINAL UTAMA  x:[70..430], y:[55..185]
    # -----------------------------------------------------------------------

    # --- STEP 1: Balok Lantai 1 (Sayap Kiri, Badan Tengah, Sayap Kanan) ---
    # 6a. Sayap kiri terminal (wing A) x:[70..190]
    draw_block(70, 190, 60, 185, 0, 48, CONC_TOP, CONC_L, CONC_R)
    # 6b. Badan tengah terminal x:[190..310]
    draw_block(190, 310, 55, 185, 0, 72, TERM_TOP, TERM_L, TERM_R)
    # 6c. Sayap kanan terminal (wing B) x:[310..430]
    draw_block(310, 430, 60, 185, 0, 48, CONC_TOP, CONC_L, CONC_R)

    # --- STEP 2: Atap Datar & Trim Sayap Kiri & Sayap Kanan ---
    # Sayap kiri (atap datar)
    draw_poly([(70,60,48),(190,60,48),(190,185,48),(70,185,48)], ROOF_TOP)
    draw_poly([(70,185,44),(190,185,44),(190,185,48),(70,185,48)], ROOF_L)
    # Sayap kanan (atap datar)
    draw_poly([(310,60,48),(430,60,48),(430,185,48),(310,185,48)], ROOF_TOP)
    draw_poly([(310,185,44),(430,185,44),(430,185,48),(310,185,48)], ROOF_L)
    draw_poly([(430,60,44),(430,185,44),(430,185,48),(430,60,48)], ROOF_R)

    # --- STEP 3: Jendela Kaca Lantai 1 & Livery Biru Bawah ---
    # Kaca lantai 1 (apron side, y=185)
    for gx in range(82, 185, 28):
        glass_left(gx, 185, 5, w=18, h=34)
    for gx in range(204, 300, 24):
        glass_left(gx, 185, 5, w=18, h=60)
    for gx in range(316, 420, 28):
        glass_left(gx, 185, 5, w=18, h=34)
    # Kaca sisi kanan (x=430)
    for gy in range(68, 178, 28):
        glass_right(430, gy, 5, w=18, h=34)
    # Aksen livery biru lantai 1 (z=45..49) - Terbagi menjadi sayap kiri dan sayap kanan,
    # melewati dermaga depan kiri dan kanan, serta membebaskan area pintu masuk tengah (190..310) agar rapi
    draw_poly([(70,185,45),(190,185,45),(190,185,49),(70,185,49)], ACCENT_L, outline=False)
    draw_poly([(310,185,45),(430,185,45),(430,185,49),(310,185,49)], ACCENT_L, outline=False)
    # Aksen livery biru sisi kanan lantai 1 (x=430, z=45..49) - Selaras dengan depan agar tersambung rapi di sudut
    draw_poly([(430,60,45),(430,185,45),(430,185,49),(430,60,49)], ACCENT_R, outline=False)

    # --- STEP 4: Pintu Masuk Utama & Kanopi ---
    for dx in [222, 243, 264]:
        draw_poly([(dx,185,2),(dx+18,185,2),(dx+18,185,46),(dx,185,46)], GLASS_L)
        ln(dx+9,185,2, dx+9,185,46, WIN_FRAME, 1)
    # Kanopi pintu
    draw_poly([(210,185,48),(290,185,48),(290,198,42),(210,198,42)], CANOPY_TOP)
    draw_poly([(210,185,48),(290,185,48),(290,185,48),(210,185,48)], CANOPY_L, outline=False)
    draw_poly([(210,198,42),(290,198,42),(290,198,44),(210,198,44)], CANOPY_R, outline=False)
    # Catatan: Tiang kanopi di bawah tulisan terminal dihapus sepenuhnya agar area masuk depan bersih dan rapi

    # --- STEP 5: Lantai Dua Tengah ---
    draw_block(175, 325, 65, 178, 72, 114, TERM_TOP, TERM_L, TERM_R)

    # --- STEP 6: Jendela Kaca Lantai Dua & Livery Atas/Tengah ---
    # Kaca lantai dua (apron side, y=178)
    for gx in range(188, 314, 28):
        glass_left(gx, 178, 78, w=20, h=28)
    # Kaca sisi kanan lantai dua (x=325)
    for gy in range(72, 170, 28):
        glass_right(325, gy, 78, w=20, h=28)
    # Aksen livery biru tengah (z=62) - hanya pada badan tengah
    draw_poly([(190,185,62),(310,185,62),(310,185,66),(190,185,66)], ACCENT_L, outline=False)
    # Aksen livery biru lantai dua (z=108)
    draw_poly([(175,178,108),(325,178,108),(325,178,112),(175,178,112)], ACCENT_L, outline=False)

    # --- STEP 7: Atap Pelana Tengah & Skylight ---
    draw_poly([(175,65,114),(175,178,114),(175,122,140)], ROOF_L) # 1. Left triangle
    draw_poly([(175,65,114),(325,65,114),(325,122,140),(175,122,140)], ROOF_R) # 2. Back slope
    draw_poly([(175,178,114),(325,178,114),(325,122,140),(175,122,140)], ROOF_L) # 3. Front slope
    draw_poly([(325,65,114),(325,178,114),(325,122,140)], ROOF_R) # 4. Right triangle
    # Skylight strip
    for sx in range(198, 304, 35):
        draw_poly([(sx,118,139),(sx+22,118,139),(sx+22,128,139),(sx,128,139)], GLASS_L, outline=False)

    # 5l. Nama terminal
    font_term = pygame.font.SysFont("Arial", max(6, int(18*scale)), bold=True)
    txt = font_term.render("TERMINAL", True, (255,255,255))
    txt = pygame.transform.rotate(txt, -26.5)
    tc = iso(250, 185, 92)
    screen.blit(txt, txt.get_rect(center=(int(tc[0]), int(tc[1]))))

    # -----------------------------------------------------------------------
    # 6. FINGER PIER / CONCOURSE (jari-jari gate menuju apron)
    #    Hanya Kiri: x:[88..132] dan Kanan: x:[368..412] (Pier Tengah dihapus)
    #    Dibuat 2 tingkat (tinggi z=48) agar sejajar dengan tinggi wing terminal
    # -----------------------------------------------------------------------
    piers = [(88, 132), (368, 412)]
    for px1, px2 in piers:
        # Blok utama gedung pier (z: 0..48)
        draw_block(px1, px2, 185, 260, 0, 48, CONC_TOP, CONC_L, CONC_R)
        
        # --- LANTAI 1 WINDOWS & BLUE ACCENT ---
        # Kaca sepanjang pier (y=260)
        for gx in range(px1+5, px2-5, 22):
            glass_left(gx, 260, 4, w=15, h=16)
        # Kaca sisi kanan pier (x=px2)
        for gy in range(192, 254, 22):
            glass_right(px2, gy, 4, w=15, h=16)
        # List biru pembatas lantai 1 (z=20..24)
        draw_poly([(px1,260,20),(px2,260,20),(px2,260,24),(px1,260,24)], ACCENT_L, outline=False)
        
        # --- LANTAI 2 WINDOWS & BLUE ACCENT ---
        # Kaca sepanjang pier (y=260)
        for gx in range(px1+5, px2-5, 22):
            glass_left(gx, 260, 26, w=15, h=16)
        # Kaca sisi kanan pier (x=px2)
        for gy in range(192, 254, 22):
            glass_right(px2, gy, 26, w=15, h=16)
        # List biru pembatas lantai 2 / atap (z=44..48)
        draw_poly([(px1,260,44),(px2,260,44),(px2,260,48),(px1,260,48)], ACCENT_L, outline=False)

        # Atap pier
        draw_poly([(px1,185,48),(px2,185,48),(px2,260,48),(px1,260,48)], CONC_TOP)

    # -----------------------------------------------------------------------
    # 7. GARBARATA / JETBRIDGE (tiap pier 1 garbarata - Kiri & Kanan Saja)
    # -----------------------------------------------------------------------
    gate_cx = [110, 390]   # x tengah pier (kiri & kanan)
    for gx in gate_cx:
        jx = gx - 16
        # Tiang penyangga (digambar lebih dulu agar ter-render di bawah, dan didekatkan dengan pesawat ke y=281..285)
        draw_block(jx-2, jx+2, 281, 285, 0, 20, CURB_TOP, CURB_L, CURB_R)
        # Lorong teleskopik
        draw_block(jx-5, jx+5, 258, 280, 20, 29, JB_TOP, JB_L, JB_R)
        # Kepala gate (menyentuh pintu kiri pesawat di gx - 8)
        draw_block(jx-6, jx+8, 280, 288, 18, 29, JB_TOP, JB_L, JB_R)

    # -----------------------------------------------------------------------
    # 8. MENARA ATC  x:[455..505], y:[65..120]
    # -----------------------------------------------------------------------

    # Pondasi
    draw_block(452, 508, 62, 123, 0, 8, CURB_TOP, CURB_L, CURB_R)

    # Badan menara (ramping, tinggi)
    draw_block(466, 494, 76, 109, 8, 130, ATC_TOP, ATC_L, ATC_R)

    # Band struktural di tengah menara
    draw_block(462, 498, 72, 113, 58, 67, CURB_TOP, CURB_L, CURB_R)

    # Pengerucutan badan atas
    draw_poly([(466,76,130),(494,76,130),(500,70,142),(460,70,142)], ATC_R)
    draw_poly([(466,109,130),(494,109,130),(500,115,142),(460,115,142)], ATC_L)
    draw_poly([(460,70,142),(460,115,142),(466,109,130),(466,76,130)], ATC_L)
    draw_poly([(500,70,142),(500,115,142),(494,109,130),(494,76,130)], ATC_R)
    draw_poly([(460,70,142),(500,70,142),(494,76,130),(466,76,130)], ATC_TOP)

    # Kabin pengawas (hexagonal — pendekatan 4 sisi)
    draw_block(452, 508, 62, 124, 142, 176, CAB_TOP, CAB_L, CAB_R)

    # Panel kaca kabin (setiap sisi)
    for ax in range(457, 503, 16):
        glass_left(ax, 124, 146, w=12, h=24)
    for ay in range(66, 121, 16):
        glass_right(508, ay, 146, w=12, h=24)

    # Atap kabin
    draw_block(450, 510, 60, 126, 176, 183, ROOF_TOP, ROOF_L, ROOF_R)

    # Tiang antena
    ln(480, 93, 183, 480, 93, 222, RADAR_COL, 4)

    # Piringan radar (rotary)
    rcx, rcy = iso(480, 93, 217)
    pygame.draw.ellipse(screen, RADAR_COL, (int(rcx)-int(18*scale), int(rcy)-int(6*scale), int(36*scale), int(12*scale)), 0)
    pygame.draw.ellipse(screen, LINE_COL,  (int(rcx)-int(18*scale), int(rcy)-int(6*scale), int(36*scale), int(12*scale)), max(1, int(2*scale)))
    ln(480, 93, 183, 480, 93, 226, RADAR_COL, max(1, int(2*scale)))

    # Lampu navigasi ATC
    tip = iso(480, 93, 226)
    pygame.draw.circle(screen, (255, 50, 50), (int(tip[0]), int(tip[1])), max(1, int(4*scale)))
    pygame.draw.circle(screen, LINE_COL,     (int(tip[0]), int(tip[1])), max(1, int(4*scale)), 1)

    # Label ATC
    font_atc = pygame.font.SysFont("Arial", max(6, int(11*scale)), bold=True)
    ts = font_atc.render("ATC", True, WIN_FRAME)
    ts = pygame.transform.rotate(ts, -26.5)
    tc = iso(480, 124, 160)
    screen.blit(ts, ts.get_rect(center=(int(tc[0]), int(tc[1]))))

    # -----------------------------------------------------------------------
    # 9. PESAWAT DI APRON
    # -----------------------------------------------------------------------

    def draw_pesawat(px, py, pz, scale=1.0):
        """
        Pesawat memanjang arah sumbu y (depth),
        hidung mengarah ke y kecil (ke terminal).
        scale: faktor ukuran.
        """
        BL = int(88 * scale)   # panjang badan
        BW = int(12 * scale)   # setengah lebar badan
        BH = int(14 * scale)   # tinggi badan
        WS = int(70 * scale)   # rentang sayap (ke samping / sumbu x)
        WD = int(22 * scale)   # panjang sayap ke depan (sumbu y)
        EL = int(18 * scale)   # panjang mesin
        EW = int(7 * scale)    # radius mesin
        EH = int(8 * scale)    # tinggi mesin

        # --- Badan utama (memanjang sumbu y, bentuk silindris/hexagonal) ---
        # 1. Badan bawah (balok dasar)
        draw_block(px-BW, px+BW, py, py+BL, pz, pz+int(BH*0.75), PL_BODY_T, PL_BODY_L, PL_BODY_R)
        # 2. Atap tengah (top roof flat)
        draw_poly([(px-int(BW*0.6), py, pz+BH), (px+int(BW*0.6), py, pz+BH), (px+int(BW*0.6), py+BL, pz+BH), (px-int(BW*0.6), py+BL, pz+BH)], PL_BODY_T)
        # 3. Shoulder Kiri (sloped shoulder)
        draw_poly([(px-BW, py, pz+int(BH*0.75)), (px-int(BW*0.6), py, pz+BH), (px-int(BW*0.6), py+BL, pz+BH), (px-BW, py+BL, pz+int(BH*0.75))], PL_BODY_L)
        # 4. Shoulder Kanan
        draw_poly([(px+int(BW*0.6), py, pz+BH), (px+BW, py, pz+int(BH*0.75)), (px+BW, py+BL, pz+int(BH*0.75)), (px+int(BW*0.6), py+BL, pz+BH)], PL_BODY_R)

        # --- Hidung (runcing ke y-, berbentuk 3D shaded cone) ---
        nose_y = py
        # Titik ujung hidung
        tip = (px, nose_y - int(22 * scale), pz + int(BH * 0.35))
        
        # Vertices wajah depan fuselage
        v_bot_left  = (px-BW, nose_y, pz)
        v_bot_right = (px+BW, nose_y, pz)
        v_mid_left  = (px-BW, nose_y, pz+int(BH*0.75))
        v_mid_right = (px+BW, nose_y, pz+int(BH*0.75))
        v_top_left  = (px-int(BW*0.6), nose_y, pz+BH)
        v_top_right = (px+int(BW*0.6), nose_y, pz+BH)
        
        # Wajah-wajah hidung
        draw_poly([v_bot_left, v_mid_left, tip], PL_NOSE_L)
        draw_poly([v_mid_right, v_bot_right, tip], PL_BODY_R)
        draw_poly([v_mid_left, v_top_left, tip], PL_NOSE_L)
        draw_poly([v_top_right, v_mid_right, tip], PL_BODY_R)
        draw_poly([v_top_left, v_top_right, tip], PL_BODY_T)
        draw_poly([v_bot_right, v_bot_left, tip], PL_NOSE_L)

        # --- Kaca Depan Kokpit (Windshield miring, menghadap depan-top) ---
        w_wind = int(BW * 0.6)
        y_wind = py + int(8 * scale)
        draw_poly([
            (px - w_wind, y_wind, pz + BH),
            (px + w_wind, y_wind, pz + BH),
            (px + w_wind, py, pz + int(BH * 0.75)),
            (px - w_wind, py, pz + int(BH * 0.75))
        ], GLASS_TOP)
        # Kaca samping kokpit
        draw_poly([
            (px - BW, py, pz + int(BH * 0.75)),
            (px - w_wind, py, pz + int(BH * 0.75)),
            (px - w_wind, y_wind, pz + BH),
            (px - BW, y_wind, pz + int(BH * 0.75))
        ], GLASS_L)
        draw_poly([
            (px + w_wind, py, pz + int(BH * 0.75)),
            (px + BW, py, pz + int(BH * 0.75)),
            (px + BW, y_wind, pz + int(BH * 0.75)),
            (px + w_wind, y_wind, pz + BH)
        ], GLASS_R)

        # --- Ekor (y+ ujung, sirip miring ke belakang) ---
        tail_y = py + BL
        # Sirip vertikal (miring ke belakang)
        draw_poly([
            (px-2, tail_y - int(18*scale), pz+BH),
            (px+2, tail_y - int(18*scale), pz+BH),
            (px+2, tail_y,                 pz+BH+int(26*scale)),
            (px-2, tail_y,                 pz+BH+int(26*scale)),
        ], PL_TAIL)
        draw_poly([
            (px-2, tail_y - int(18*scale), pz+BH),
            (px-2, tail_y,                 pz+BH+int(26*scale)),
            (px-2, tail_y,                 pz+BH),
        ], PL_TAIL)
        
        # Horizontal stabilizer (kecil miring ke belakang di ekor bawah)
        # Sisi Kiri
        draw_poly([
            (px, tail_y - int(12*scale), pz+int(BH*0.3)),
            (px, tail_y,                 pz+int(BH*0.3)),
            (px - int(25*scale), tail_y, pz+int(BH*0.3)),
            (px - int(25*scale), tail_y - int(5*scale), pz+int(BH*0.3))
        ], PL_WING_L)
        # Sisi Kanan
        draw_poly([
            (px, tail_y - int(12*scale), pz+int(BH*0.3)),
            (px, tail_y,                 pz+int(BH*0.3)),
            (px + int(25*scale), tail_y, pz+int(BH*0.3)),
            (px + int(25*scale), tail_y - int(5*scale), pz+int(BH*0.3))
        ], PL_WING_R)

        # --- Sayap utama (x ke kiri & kanan, menyapu ke belakang / swept-back) ---
        wing_y = py + BL//3
        # Sayap kiri (x-)
        draw_poly([
            (px-BW,    wing_y,    pz+4),
            (px-BW,    wing_y+WD, pz+4),
            (px-BW-WS, wing_y+WD+int(20*scale), pz+2),
            (px-BW-WS, wing_y+int(20*scale),    pz+2),
        ], PL_WING_L)
        # Sayap kanan (x+)
        draw_poly([
            (px+BW,    wing_y,    pz+4),
            (px+BW,    wing_y+WD, pz+4),
            (px+BW+WS, wing_y+WD+int(20*scale), pz+2),
            (px+BW+WS, wing_y+int(20*scale),    pz+2),
        ], PL_WING_R)

        # --- Mesin (2 buah di bawah sayap swept-back) ---
        for ex_off in [-int(38*scale), int(38*scale)]:
            ex = px + ex_off
            ratio = abs(ex_off) / float(WS)
            ey = wing_y + int(20 * scale * ratio) + int(4 * scale)
            draw_block(ex-EW, ex+EW, ey, ey+EL, pz-EH, pz+2, PL_ENG_T, PL_ENG_L, PL_ENG_R)
            # Intake (lingkaran depan)
            ep = iso(ex, ey, pz-EH//2)
            pygame.draw.ellipse(screen, (45,45,48),
                                (int(ep[0])-int(EW*1.2), int(ep[1])-int(EH*0.6),
                                 int(EW*2.4), int(EH*1.2)), 0)
            pygame.draw.ellipse(screen, LINE_COL,
                                (int(ep[0])-int(EW*1.2), int(ep[1])-int(EH*0.6),
                                 int(EW*2.4), int(EH*1.2)), 1)

        # --- Jendela kabin (titik oval di badan, sisi kiri/x-) ---
        win_start = py + int(20*scale)
        win_end   = py + int(58*scale)
        num_win   = 7
        for i in range(num_win):
            wy = win_start + int(i * (win_end - win_start) / (num_win - 1))
            wp = iso(px - BW, wy, pz + int(BH * 0.50))
            r = max(2, int(3 * scale))
            pygame.draw.ellipse(screen, PL_WIN,
                                (int(wp[0])-r, int(wp[1])-int(r*1.4), r*2, int(r*2.8)))
            pygame.draw.ellipse(screen, LINE_COL,
                                (int(wp[0])-r, int(wp[1])-int(r*1.4), r*2, int(r*2.8)), 1)

        # --- Stripe livery biru ---
        draw_poly([
            (px-BW, py+int(12*scale),        pz+int(BH*0.28)),
            (px-BW, py+BL-int(12*scale),    pz+int(BH*0.28)),
            (px-BW, py+BL-int(12*scale),    pz+int(BH*0.40)),
            (px-BW, py+int(12*scale),         pz+int(BH*0.40)),
        ], PL_STRIPE, outline=False)

    # Pesawat 1 — gate kiri
    draw_pesawat(110, 286, 1, scale=0.78)
    # Pesawat 2 — gate kanan (lebih kecil, parkir miring sedikit)
    draw_pesawat(390, 290, 1, scale=0.68)

    # -----------------------------------------------------------------------
    # 11. WINDSOCK
    # -----------------------------------------------------------------------
    wp_x, wp_y = 640, 425
    ln(wp_x, wp_y, 0, wp_x, wp_y, 38, POLE_COL, max(1, int(4*scale)))
    # Ring logam
    ring_p = iso(wp_x, wp_y, 38)
    pygame.draw.circle(screen, POLE_COL, (int(ring_p[0]),int(ring_p[1])), max(1, int(5*scale)))
    # Kerucut windsock
    draw_poly([
        (wp_x,    wp_y, 36),
        (wp_x+18, wp_y, 31),
        (wp_x+28, wp_y, 33),
        (wp_x,    wp_y, 38),
    ], (215, 55, 38))
    draw_poly([
        (wp_x,    wp_y, 36),
        (wp_x+8,  wp_y, 34),
        (wp_x+18, wp_y, 31),
        (wp_x,    wp_y, 38),
    ], (245, 245, 245), outline=False)


# --- CLASS WRAPPER UNTUK OOP ---
class Bandara:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0

    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_bandara(screen, self.x - 64 * scale, self.y - 440 * scale, scale=scale)
