import pygame
import sys

def render_kapal_kargo_besar(screen, cx, cy):
    """
    Fungsi Menggambar Kapal Kargo Isometrik Premium (100% Persis Gambar Desain).
    Fungsi diberi nama 'render_gedung' agar langsung plug-and-play dengan 
    panggilan `gedung.render_gedung(screen, CX_PUSAT, CY_PUSAT)` pada main.py Anda.
    """
    
    # --- SISTEM KOORDINAT ISOMETRIK ASLI ---
    # Menjamin keselarasan sudut kemiringan perspektif 100% dengan objek lainnya
    def iso(x, y, z):
        sx = cx + (x - y) * 18
        sy = cy - (x + y) * 9 - z * 16
        return sx, sy

    # --- FUNGSI DRAW BLOK/KUBUS ISOMETRIK SHADING ---
    def draw_block(x, y, z, w, d, h, c_top, c_left, c_right):
        p0 = iso(x, y, z)
        p1 = iso(x + w, y, z)
        p2 = iso(x + w, y + d, z)
        p3 = iso(x, y + d, z)
        
        p4 = iso(x, y, z + h)
        p5 = iso(x + w, y, z + h)
        p6 = iso(x + w, y + d, z + h)
        p7 = iso(x, y + d, z + h)
        
        c_outline = (35, 40, 45)
        
        # Sisi Atas (Top Face) - Terang terkena cahaya matahari
        pygame.draw.polygon(screen, c_top, [p4, p5, p6, p7])
        pygame.draw.polygon(screen, c_outline, [p4, p5, p6, p7], 1)
        
        # Sisi Kiri (Left Face) - Shading Medium
        pygame.draw.polygon(screen, c_left, [p0, p3, p7, p4])
        pygame.draw.polygon(screen, c_outline, [p0, p3, p7, p4], 1)
        
        # Sisi Kanan (Right Face) - Shading Gelap
        pygame.draw.polygon(screen, c_right, [p0, p1, p5, p4])
        pygame.draw.polygon(screen, c_outline, [p0, p1, p5, p4], 1)

    # --- FUNGSI KHUSUS KONTAINER BERTEKSTUR ---
    def draw_container_block(x, y, z, w, d, h, colors):
        c_top, c_left, c_right = colors
        draw_block(x, y, z, w, d, h, c_top, c_left, c_right)
        
        # Detail garis-garis vertikal tekstur bergelombang kontainer asli
        c_line = (int(c_left[0]*0.7), int(c_left[1]*0.7), int(c_left[2]*0.7))
        for i in range(1, 4):
            # Garis vertikal di sisi kiri
            f_y = y + d * (i / 4)
            p_bot_l = iso(x, f_y, z)
            p_top_l = iso(x, f_y, z + h)
            pygame.draw.line(screen, c_line, p_bot_l, p_top_l, 1)
            
            # Garis vertikal di sisi kanan
            f_x = x + w * (i / 4)
            p_bot_r = iso(f_x, y, z)
            p_top_r = iso(f_x, y, z + h)
            pygame.draw.line(screen, c_line, p_bot_r, p_top_r, 1)

    # --- PALET WARNA VEKTOR PREMIUM ---
    # Warna Lambung Atas (Slate Charcoal) & Lambung Bawah (Crimson Red)
    HULL_TOP, HULL_LEFT, HULL_RIGHT = (75, 82, 92), (48, 53, 60), (60, 66, 75)
    RED_TOP, RED_LEFT, RED_RIGHT    = (190, 45, 45), (135, 30, 30), (165, 38, 38)
    DECK_COLOR = (212, 218, 224)

    # Warna Kontainer (Top, Left, Right)
    C_RED    = ((235, 85, 85),   (165, 40, 40),   (205, 55, 55))
    C_BLUE   = ((80, 150, 225),  (45, 95, 165),   (60, 125, 200))
    C_GREEN  = ((90, 190, 120),  (50, 130, 75),   (65, 160, 95))
    C_YELLOW = ((250, 210, 75),  (190, 150, 35),  (225, 180, 50))

    # Warna Struktur Kabin/Deckhouse (Putih Bersih)
    CAB_TOP, CAB_LEFT, CAB_RIGHT   = (248, 250, 252), (195, 200, 210), (225, 230, 238)
    ROOF_TOP, ROOF_LEFT, ROOF_RIGHT = (235, 65, 65), (170, 35, 35), (205, 50, 50)
    CRANE_TOP, CRANE_LEFT, CRANE_RIGHT = (245, 145, 50), (190, 100, 25), (220, 120, 35)

    # ==========================================
    # 1. BAGIAN LAMBUNG BAWAH KAPAL (Crimson Waterline)
    # ==========================================
    # Haluan/Moncong Depan Segitiga Lancip
    pygame.draw.polygon(screen, RED_TOP, [iso(0, 1.5, 0.6), iso(3, 0, 0.6), iso(3, 3, 0.6)])
    pygame.draw.polygon(screen, RED_LEFT, [iso(0, 1.5, 0), iso(3, 3, 0), iso(3, 3, 0.6), iso(0, 1.5, 0.6)])
    pygame.draw.polygon(screen, RED_RIGHT, [iso(0, 1.5, 0), iso(3, 0, 0), iso(3, 0, 0.6), iso(0, 1.5, 0.6)])
    # Badan Utama Lambung Bawah
    draw_block(3.0, 0.0, 0.0, 13.0, 3.0, 0.6, RED_TOP, RED_LEFT, RED_RIGHT)

    # ==========================================
    # 2. BAGIAN LAMBUNG ATAS & GELADAK (Main Hull & Deck)
    # ==========================================
    # Haluan/Moncong Depan Atas
    pygame.draw.polygon(screen, HULL_TOP, [iso(0, 1.5, 2.0), iso(3, 0, 2.0), iso(3, 3, 2.0)])
    pygame.draw.polygon(screen, HULL_LEFT, [iso(0, 1.5, 0.6), iso(3, 3, 0.6), iso(3, 3, 2.0), iso(0, 1.5, 2.0)])
    pygame.draw.polygon(screen, HULL_RIGHT, [iso(0, 1.5, 0.6), iso(3, 0, 0.6), iso(3, 0, 2.0), iso(0, 1.5, 2.0)])
    # Badan Utama Lambung Atas
    draw_block(3.0, 0.0, 0.6, 13.0, 3.0, 1.4, HULL_TOP, HULL_LEFT, HULL_RIGHT)
    # Lantai Geladak (Deck Face)
    pygame.draw.polygon(screen, DECK_COLOR, [iso(0, 1.5, 2.0), iso(3, 0, 2.0), iso(16, 0, 2.0), iso(16, 3, 2.0), iso(3, 3, 2.0)])
    pygame.draw.polygon(screen, (35, 40, 45), [iso(0, 1.5, 2.0), iso(3, 0, 2.0), iso(16, 0, 2.0), iso(16, 3, 2.0), iso(3, 3, 2.0)], 2)

    # Dekorasi Garis Putih Pembatas Lambung Atas-Bawah Rapi
    pygame.draw.line(screen, (240, 245, 250), iso(0, 1.5, 0.6), iso(3, 0, 0.6), 2)
    pygame.draw.line(screen, (240, 245, 250), iso(3, 0, 0.6), iso(16, 0, 0.6), 2)

    # ==========================================
    # 3. STRUKTUR ANJUNGAN KABIN BELAKANG (Superstructure)
    # Rapi, bertingkat, diurutkan dari posisi belakang (X terbesar)
    # ==========================================
    # Tier 1: Blok Dasar Putih Besar
    draw_block(12.0, 0.3, 2.0, 3.5, 2.4, 1.5, CAB_TOP, CAB_LEFT, CAB_RIGHT)
    
    # Tier 2: Blok Tengah Putih
    draw_block(12.5, 0.5, 3.5, 2.7, 2.0, 1.3, CAB_TOP, CAB_LEFT, CAB_RIGHT)
    
    # Tier 3: Kabin Kemudi Utama (Atap Komando Merah Terang)
    draw_block(13.0, 0.7, 4.8, 1.8, 1.6, 1.2, ROOF_TOP, ROOF_LEFT, ROOF_RIGHT)
    # Atap Overhang Pelindung
    draw_block(12.8, 0.6, 6.0, 2.1, 1.8, 0.2, CAB_TOP, CAB_LEFT, CAB_RIGHT)

    # Kaca Jendela Mengkilap Biru Cyan pada Kabin Kemudi
    p_window_r = [iso(13.2, 0.7, 5.2), iso(14.6, 0.7, 5.2), iso(14.6, 0.7, 5.7), iso(13.2, 0.7, 5.7)]
    pygame.draw.polygon(screen, (90, 220, 255), p_window_r)
    pygame.draw.polygon(screen, (30, 35, 40), p_window_r, 1)

    # Cerobong Asap (Kuning-Hitam Maskulin di Belakang Kabin)
    draw_block(14.3, 1.1, 6.2, 0.9, 0.8, 1.2, (245, 195, 40), (190, 150, 25), (220, 170, 35))
    draw_block(14.3, 1.1, 7.4, 0.9, 0.8, 0.3, (35, 35, 35), (20, 20, 20), (28, 28, 28))

    # Tiang Antena/Radar Atas Kapal
    draw_block(13.6, 1.4, 6.2, 0.2, 0.2, 1.8, HULL_TOP, HULL_LEFT, HULL_RIGHT)
    pygame.draw.line(screen, (200, 50, 50), iso(13.7, 1.5, 8.0), iso(13.7, 1.5, 8.5), 2)

    # Portholes (Detail jendela lingkaran mini kabin putih bawah)
    for px in [12.6, 13.8, 15.0]:
        w_x, w_y = iso(px, 0.3, 2.7)
        pygame.draw.circle(screen, (40, 50, 60), (int(w_x), int(w_y)), 3)

    # ==========================================
    # 4. SUSUNAN BLOK KONTAINER KARGO (Warna-Warni Dinamis)
    # Diurutkan dari belakang ke depan (Row 3 -> Row 2 -> Row 1)
    # ==========================================
    rows = [
        {"x": 9.2,  "lanes": { "right": C_GREEN, "left": C_YELLOW }}, # Row 3 (Belakang)
        {"x": 6.4,  "lanes": { "right": C_RED,   "left": C_GREEN }},  # Row 2 (Tengah)
        {"x": 3.6,  "lanes": { "right": C_YELLOW,"left": C_BLUE }}   # Row 1 (Depan)
    ]

    for row in rows:
        rx = row["x"]
        
        # --- A. Lajur Kanan (Right Lane / y = 1.6) ---
        # Layer 1 (Bawah)
        draw_container_block(rx, 1.6, 2.0, 2.4, 1.1, 1.2, row["lanes"]["right"])
        # Layer 2 (Atas - Bersilang variasi)
        if rx == 6.4:
            draw_container_block(rx, 1.6, 3.2, 2.4, 1.1, 1.2, C_BLUE)
        elif rx == 3.6:
            draw_container_block(rx, 1.6, 3.2, 2.4, 1.1, 1.2, C_GREEN)
            
        # --- B. Lajur Kiri (Left Lane / y = 0.3) ---
        # Layer 1 (Bawah)
        draw_container_block(rx, 0.3, 2.0, 2.4, 1.1, 1.2, row["lanes"]["left"])
        # Layer 2 (Atas)
        if rx == 9.2:
            draw_container_block(rx, 0.3, 3.2, 2.4, 1.1, 1.2, C_BLUE)
        elif rx == 6.4:
            draw_container_block(rx, 0.3, 3.2, 2.4, 1.1, 1.2, C_YELLOW)
        elif rx == 3.6:
            draw_container_block(rx, 0.3, 3.2, 2.4, 1.1, 1.2, C_RED)

    # ==========================================
    # 5. DEREK MINI DECK KAPAL (Forecastle Crane)
    # Ditempatkan di bagian depan geladak dekat moncong lancip
    # ==========================================
    # Tiang pancang vertikal crane
    draw_block(1.8, 1.3, 2.0, 0.5, 0.5, 1.6, CRANE_TOP, CRANE_LEFT, CRANE_RIGHT)
    # Lengan horizontal penarik kontainer
    draw_block(1.0, 1.3, 3.6, 1.3, 0.4, 0.3, CRANE_TOP, CRANE_LEFT, CRANE_RIGHT)
    # Tali kawat/kabel baja gantung hitam tipis
    pygame.draw.line(screen, (30, 30, 30), iso(1.0, 1.5, 3.6), iso(1.0, 1.5, 2.0), 2)