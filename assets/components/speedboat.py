import pygame
import sys

# ==========================================
# PALET WARNA 3D KAPAL CEPAT (Sesuai Gambar)
# ==========================================
# Warna Lambung Merah (Gradasi Bayangan)
RED_BRIGHT   = (225, 35, 45)    # Merah utama terkena cahaya
RED_MED      = (185, 20, 30)    # Merah medium (sisi samping)
RED_SHADOW   = (130, 10, 20)    # Merah gelap (bayangan lambung bawah)

# Warna Lambung Putih & Deck
WHITE_DECK   = (245, 248, 252)  # Putih bersih (permukaan atas)
WHITE_SHADOW = (195, 205, 215)  # Abu-abu kebiruan (bayangan putih bawah)
WHITE_MID    = (220, 228, 238)  # Warna transisi lambung putih

# Komponen Interior & Kaca
ORANGE_SEAT  = (235, 75, 35)    # Objek/kursi oranye di dalam cockpit
GLASS_BLUE   = (160, 210, 235)  # Kaca depan kaca transparan
GLASS_FRAME  = (70, 80, 90)     # Bingkai kaca gelap
METAL_RAIL   = (180, 190, 200)  # Pagar stainless depan

# Mesin Tempel (Outboard Motor)
MOTOR_BLUE   = (0, 105, 185)    # Biru mesin utama
MOTOR_DARK   = (0, 70, 135)     # Biru bayangan mesin
MOTOR_LINE   = (20, 30, 45)     # Garis grill mesin

# Warna yang dipertahankan untuk perahu
WATER_LIGHT  = (135, 215, 235)  # Cyan muda (Digunakan untuk highlight mesin)


def draw_speedboat(surface, cx, cy):
    """
    Menggambar Speedboat 3D artistik sesuai gambar referensi.
    cx, cy: Titik koordinat pusat jangkar posisi kapal.
    """

    # ==========================================
    # 1. EFFECT CIPRATAN AIR & OMBAK (DIPERBAIKI: DIHAPUS)
    # ==========================================
    # Bagian ini telah dihapus sesuai permintaan untuk menghilangkan alas air.


    # ==========================================
    # 2. LAMBUNG BAWAH PUTIH (White Lower Hull)
    # ==========================================
    # Poligon shading bawah untuk memberikan efek melengkung 3D miring
    hull_white_shadow = [
        (cx - 160, cy - 10),  # Ujung depan (Haluan)
        (cx - 100, cy + 18),  # Lengkungan bawah kiri
        (cx + 10,  cy + 24),  # Dasar lambung tengah
        (cx + 120, cy + 12),  # Lambung belakang bawah
        (cx + 140, cy - 5),   # Buritan kanan
        (cx + 40,  cy + 10),  # Garis tengah transisi shadow
        (cx - 60,  cy + 2)
    ]
    pygame.draw.polygon(surface, WHITE_SHADOW, hull_white_shadow)

    hull_white_main = [
        (cx - 160, cy - 10),
        (cx - 60,  cy + 2),
        (cx + 40,  cy + 10),
        (cx + 140, cy - 5),
        (cx + 145, cy - 15),  # Naik ke perbatasan lis merah
        (cx + 30,  cy + 0),
        (cx - 70,  cy - 10)
    ]
    pygame.draw.polygon(surface, WHITE_MID, hull_white_main)


    # ==========================================
    # 3. LAMBUNG UTAMA MERAH (Red Main Hull)
    # ==========================================
    # Terdiri dari 3 warna untuk efek pencahayaan dari atas-depan
    
    # Sisi bayangan merah bawah
    hull_red_shadow = [
        (cx - 165, cy - 15),  # Moncong paling depan
        (cx - 70,  cy - 10),
        (cx + 30,  cy + 0),
        (cx + 145, cy - 15),
        (cx + 143, cy - 23),  # Ketebalan strip shadow merah
        (cx + 30,  cy - 7),
        (cx - 70,  cy - 17)
    ]
    pygame.draw.polygon(surface, RED_SHADOW, hull_red_shadow)

    # Sisi tubuh merah utama (Red Center Body)
    hull_red_main = [
        (cx - 165, cy - 15),
        (cx - 70,  cy - 17),
        (cx + 30,  cy - 7),
        (cx + 143, cy - 23),
        (cx + 138, cy - 42),  # Sisi atas buritan belakang
        (cx + 15,  cy - 35),  # Garis dek samping
        (cx - 95,  cy - 38)   # Lekukan ke arah haluan depan
    ]
    pygame.draw.polygon(surface, RED_MED, hull_red_main)

    # Kilauan highlight merah atas (Top Red Rim)
    hull_red_bright = [
        (cx - 165, cy - 15),
        (cx - 95,  cy - 38),
        (cx + 15,  cy - 35),
        (cx + 138, cy - 42),
        (cx + 135, cy - 45),  # Garis bibir kapal paling atas
        (cx + 10,  cy - 38),
        (cx - 98,  cy - 41)
    ]
    pygame.draw.polygon(surface, RED_BRIGHT, hull_red_bright)


    # ==========================================
    # 4. DECK ATAS & INTERIOR (White Deck & Cockpit)
    # ==========================================
    # Permukaan lantai atas kapal tempat pengemudi
    deck_surface = [
        (cx - 160, cy - 18),  # Ujung lantai depan
        (cx - 98,  cy - 41),
        (cx + 10,  cy - 38),
        (cx + 135, cy - 45),
        (cx + 120, cy - 50),  # Batas dalam dinding buritan
        (cx - 10,  cy - 42),
        (cx - 90,  cy - 43)
    ]
    pygame.draw.polygon(surface, WHITE_DECK, deck_surface)

    # Efek Garis Hiasan Biru di Moncong Depan Kapal (Stripe Accent)
    blue_stripe = [
        (cx - 150, cy - 20),
        (cx - 110, cy - 29),
        (cx - 60,  cy - 31),
        (cx - 65,  cy - 34),
        (cx - 112, cy - 32)
    ]
    pygame.draw.polygon(surface, MOTOR_BLUE, blue_stripe)


    # ==========================================
    # 5. COCKPIT INTERIOR & OBJEK ORANJE
    # ==========================================
    # Kursi/Komponen Oranje melingkar di dalam lambung tengah
    orange_object = [
        (cx - 10,  cy - 42),
        (cx + 55,  cy - 45),
        (cx + 70,  cy - 30),
        (cx + 50,  cy - 18),
        (cx + 10,  cy - 25)
    ]
    pygame.draw.polygon(surface, ORANGE_SEAT, orange_object)
    
    # Bayangan silinder oranje (Efek 3D Tabung)
    pygame.draw.polygon(surface, (190, 45, 15), [
        (cx + 40, cy - 21), (cx + 50, cy - 18), (cx + 70, cy - 30), (cx + 60, cy - 33)
    ])


    # ==========================================
    # 6. KACA DEPAN BELOK (3D Windshield Glass)
    # ==========================================
    # Kaca pelindung depan (Sisi Kiri/Depan)
    glass_front = [
        (cx - 75, cy - 40),   # Pangkal kiri depan
        (cx - 30, cy - 41),   # Pusat tengah bawah
        (cx - 15, cy - 68),   # Pusat tengah atas
        (cx - 55, cy - 65)    # Kiri atas
    ]
    pygame.draw.polygon(surface, GLASS_BLUE, glass_front)
    
    # Kaca Pelindung Samping (Sisi Kanan menyudut)
    glass_side = [
        (cx - 30, cy - 41),
        (cx + 25, cy - 38),   # Ujung kaca belakang
        (cx + 30, cy - 58),   # Kaca belakang atas
        (cx - 15, cy - 68)
    ]
    pygame.draw.polygon(surface, WHITE_DECK, glass_side) # Efek refleksi putih susu di samping
    pygame.draw.polygon(surface, GLASS_BLUE, [
        (cx - 25, cy - 43), (cx + 20, cy - 40), (cx + 25, cy - 56), (cx - 12, cy - 65)
    ])

    # Bingkai Hitam Kaca (Windshield Frame)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 75, cy - 40), (cx - 55, cy - 65), 3)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 55, cy - 65), (cx - 15, cy - 68), 3)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 15, cy - 68), (cx + 30, cy - 58), 3)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 30, cy - 41), (cx - 15, cy - 68), 2) # Pilar Tengah


    # ==========================================
    # 7. MESIN TEMPEL 3D (Outboard Motor Box)
    # ==========================================
    # Blok mesin tempel biru besar di bagian belakang buritan kapal
    
    # Sisi bayangan kiri mesin (Dark side)
    motor_left = [
        (cx + 100, cy - 48),
        (cx + 125, cy - 51),
        (cx + 122, cy - 92),
        (cx + 98,  cy - 88)
    ]
    pygame.draw.polygon(surface, MOTOR_DARK, motor_left)

    # Sisi kanan terang mesin (Bright side)
    motor_right = [
        (cx + 125, cy - 51),
        (cx + 148, cy - 42),
        (cx + 145, cy - 80),
        (cx + 122, cy - 92)
    ]
    pygame.draw.polygon(surface, MOTOR_BLUE, motor_right)

    # Top Cap Mesin (Kepala Bulat Mesin)
    motor_top = [
        (cx + 98,  cy - 88),
        (cx + 122, cy - 92),
        (cx + 145, cy - 80),
        (cx + 135, cy - 74),
        (cx + 110, cy - 78)
    ]
    pygame.draw.polygon(surface, WATER_LIGHT, motor_top) # Highlight atas terang

    # Garis ventilasi udara mesin (Grill Lines hitam)
    pygame.draw.line(surface, MOTOR_LINE, (cx + 128, cy - 68), (cx + 143, cy - 62), 2)
    pygame.draw.line(surface, MOTOR_LINE, (cx + 127, cy - 63), (cx + 142, cy - 57), 2)


    # ==========================================
    # 8. PAGAR STAINLESS DEPAN (Bow Railings)
    # ==========================================
    # Pagar besi pelindung melengkung mengikuti bentuk moncong depan kapal
    rail_points = [
        (cx - 155, cy - 22),
        (cx - 120, cy - 32),
        (cx - 85,  cy - 36),
        (cx - 55,  cy - 37)
    ]
    # Menggambar rel atas pagar
    for i in range(len(rail_points) - 1):
        pygame.draw.line(surface, METAL_RAIL, rail_points[i], rail_points[i+1], 3)
    
    # Tiang-tiang penyangga vertikal rel pagar ke dek kapal
    pygame.draw.line(surface, GLASS_FRAME, (cx - 155, cy - 22), (cx - 155, cy - 19), 2)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 120, cy - 32), (cx - 120, cy - 27), 2)
    pygame.draw.line(surface, GLASS_FRAME, (cx - 85,  cy - 36), (cx - 85,  cy - 32), 2)

    # Teks Registrasi Lambung "NC41205" (Digantikan garis faset estetik putih tipis)
    pygame.draw.line(surface, WHITE_DECK, (cx - 135, cy - 18), (cx - 100, cy - 13), 1)