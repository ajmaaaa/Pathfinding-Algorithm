import pygame
import sys

# --- PALET WARNA (Sesuai Karakteristik Gambar Referensi) ---
ROAD_COLOR      = (84, 89, 95)       # Abu-abu gelap aspal jalanan
SIDEWALK_COLOR  = (215, 218, 222)    # Abu-abu lantai trotoar / halaman ruko
STRIPE_YELLOW   = (240, 180, 40)     # Garis marka parkir & pembatas roda kuning
WALL_FRONT_LIGHT= (243, 245, 247)    # Tembok depan (terkena cahaya terang)
WALL_SIDE_SHADOW= (182, 189, 198)    # Tembok samping kanan/dalam (bayangan)
ROOF_BLUE_TOP   = (38, 118, 194)     # Warna biru terang penutup atap atas
ROOF_BLUE_INNER = (26, 88, 153)      # Sisi dalam atap yang lebih gelap
GLASS_COLOR     = (165, 212, 232)    # Kaca biru transparan muda
GLASS_FRAME     = (58, 64, 70)       # Bingkai aluminium kusen jendela abu tua
CANOPY_LINE_1   = (232, 236, 240)    # Tekstur kanopi putih terang
CANOPY_LINE_2   = (205, 210, 216)    # Tekstur kanopi putih bayangan
CHAIR_COLOR     = (32, 35, 38)       # Kursi dan meja hitam luar ruko

# Identitas Warna Korporat Indomaret
INDO_BLUE       = (12, 76, 154)
INDO_RED        = (225, 38, 38)
INDO_YELLOW     = (252, 185, 22)

def get_iso_point(x, y, z, origin_x, origin_y, scale=1.0):
    """
    Fungsi Proyeksi Isometrik Murni Tanpa Math Library.
    Mengubah titik koordinat 3D ruang ruko (x, y, z) menjadi 2D piksel layar.
    """
    # Matriks transformasi proyeksi miring standar 2:1 isometrik 
    iso_x = (x - y) * 1.0 * scale
    iso_y = ((x + y) * 0.5 - z) * scale
    return (origin_x + iso_x, origin_y + iso_y)

def draw_iso_polygon(surface, points_3d, color, origin_x, origin_y, scale=1.0):
    """Menggambar satu bidang permukaan di ruang 3D"""
    points_2d = [get_iso_point(p[0], p[1], p[2], origin_x, origin_y, scale) for p in points_3d]
    pygame.draw.polygon(surface, color, points_2d)
    pygame.draw.aalines(surface, color, True, points_2d)

def draw_iso_block(surface, x, y, z, dx, dy, dz, color_top, color_left, color_right, origin_x, origin_y, scale=1.0):
    """
    Menggambar sebuah Balok 3D Isometrik yang Solid dengan 3 Sisi Pewarnaan Gradasi.
    Ini memberikan efek kedalaman optik ruko (Seni 3D Tidak Flat).
    """
    # Titik sudut bawah (z)
    p0 = (x, y, z)
    p1 = (x + dx, y, z)
    p2 = (x + dx, y + dy, z)
    p3 = (x, y + dy, z)
    
    # Titik sudut atas (z + dz)
    p4 = (x, y, z + dz)
    p5 = (x + dx, y, z + dz)
    p6 = (x + dx, y + dy, z + dz)
    p7 = (x, y + dy, z + dz)
    
    # Urutan penggambaran sisi balok dari belakang ke depan (Painter's Algorithm)
    # Sisi Kiri (Front-Left)
    draw_iso_polygon(surface, [p3, p2, p6, p7], color_left, origin_x, origin_y, scale)
    # Sisi Kanan (Front-Right)
    draw_iso_polygon(surface, [p1, p2, p6, p5], color_right, origin_x, origin_y, scale)
    # Sisi Atas Atap Balok
    draw_iso_polygon(surface, [p4, p5, p6, p7], color_top, origin_x, origin_y, scale)

def draw_minimarket(surface, origin_x, origin_y, scale=0.6):
    """
    Fungsi Utama Render Bangunan Indomaret Isometrik 3D.
    Dipanggil langsung di main.py.
    """
    
    # ----------------------------------------------------
    # 1. LAYER BASE (ASPAL DAN MARKA JALAN)
    # ----------------------------------------------------
    # Plat dasar aspal parkiran ruko
    plat_aspal = [(-250, -250, 0), (250, -250, 0), (250, 250, 0), (-250, 250, 0)]
    draw_iso_polygon(surface, plat_aspal, ROAD_COLOR, origin_x, origin_y, scale)
    
    # Garis Kuning Lajur Parkir Depan Toko (Render berulang)
    for i in range(6):
        start_x = -180 + (i * 35)
        line_p = [
            (start_x, 100, 0),
            (start_x + 5, 100, 0),
            (start_x - 45, 230, 0),
            (start_x - 50, 230, 0)
        ]
        draw_iso_polygon(surface, line_p, STRIPE_YELLOW, origin_x, origin_y, scale)

    # Blok Pembatas Roda Mobil Kuning (Kiri dan Kanan)
    draw_iso_block(surface, -200, 60, 0, 12, 40, 10, STRIPE_YELLOW, (190,140,20), (210,155,25), origin_x, origin_y, scale)
    draw_iso_block(surface, 210, -180, 0, 40, 12, 10, STRIPE_YELLOW, (190,140,20), (210,155,25), origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 2. LAYER TROTOAR SEMEN & LANTAI UTAMA TOKO
    # ----------------------------------------------------
    draw_iso_block(surface, -150, -150, 0, 310, 310, 14, SIDEWALK_COLOR, (170,175,180), (190,195,200), origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 3. (Meja Kursi Dihapus)
    # ----------------------------------------------------

    # ----------------------------------------------------
    # 4. STRUKTUR INTI RUMAH GEDUNG (DINDING UTAMA)
    # ----------------------------------------------------
    # Tembok fondasi dalam
    draw_iso_block(surface, -110, -110, 14, 240, 240, 130, WALL_FRONT_LIGHT, WALL_SIDE_SHADOW, WALL_FRONT_LIGHT, origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 5. AREA BINGKAI KUSAIN & PANEL KACA JENDELA 3D
    # ----------------------------------------------------
    # Kusen Jendela Sisi Kiri Depan
    draw_iso_block(surface, -90, 128, 40, 50, 4, 85, GLASS_FRAME, GLASS_FRAME, GLASS_FRAME, origin_x, origin_y, scale)
    draw_iso_block(surface, -86, 129, 44, 42, 2, 77, GLASS_COLOR, (130,180,205), GLASS_COLOR, origin_x, origin_y, scale)

    # Kusen Jendela Sisi Kanan Samping
    draw_iso_block(surface, 128, -70, 40, 4, 50, 85, GLASS_FRAME, GLASS_FRAME, GLASS_FRAME, origin_x, origin_y, scale)
    draw_iso_block(surface, 129, -66, 44, 2, 42, 77, GLASS_COLOR, (130,180,205), GLASS_COLOR, origin_x, origin_y, scale)

    # Pintu Kaca Geser Utama Masuk Toko (Tengah)
    draw_iso_block(surface, -20, 128, 14, 55, 4, 111, GLASS_FRAME, GLASS_FRAME, GLASS_FRAME, origin_x, origin_y, scale)
    draw_iso_block(surface, -16, 129, 14, 47, 2, 107, (210, 238, 248), (170,210,230), (210, 238, 248), origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 6. KANOPI GARIS STRIP TOKO (Pilar Dihapus)
    # ----------------------------------------------------

    # Struktur Kanopi Bergelombang di atas jendela depan (Pola pengulangan garis mikro)
    for k in range(16):
        pos_k = -100 + (k * 14)
        color_toggle = CANOPY_LINE_1 if k % 2 == 0 else CANOPY_LINE_2
        draw_iso_block(surface, pos_k, 128, 134, 12, 22, 6, color_toggle, (170,175,180), color_toggle, origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 7. MAHKOTA ATAP (LIS STRIP TRIWARNA INDOMARET)
    # ----------------------------------------------------
    # Balok Dudukan Atap Utama
    draw_iso_block(surface, -130, -130, 144, 265, 265, 30, WALL_FRONT_LIGHT, WALL_SIDE_SHADOW, WALL_FRONT_LIGHT, origin_x, origin_y, scale)

    # Lapisan Garis Indomaret Atap - SISI DEPAN (Kuning, Merah, Biru bertumpuk tegak)
    draw_iso_block(surface, -131, 133, 148, 267, 3, 8, INDO_YELLOW, INDO_YELLOW, INDO_YELLOW, origin_x, origin_y, scale)
    draw_iso_block(surface, -131, 133, 156, 267, 3, 8, INDO_RED, INDO_RED, INDO_RED, origin_x, origin_y, scale)
    draw_iso_block(surface, -131, 133, 164, 267, 3, 12, INDO_BLUE, INDO_BLUE, INDO_BLUE, origin_x, origin_y, scale)

    # Lapisan Garis Indomaret Atap - SISI KANAN
    draw_iso_block(surface, 133, -131, 148, 3, 267, 8, INDO_YELLOW, INDO_YELLOW, INDO_YELLOW, origin_x, origin_y, scale)
    draw_iso_block(surface, 133, -131, 156, 3, 267, 8, INDO_RED, INDO_RED, INDO_RED, origin_x, origin_y, scale)
    draw_iso_block(surface, 133, -131, 164, 3, 267, 12, INDO_BLUE, INDO_BLUE, INDO_BLUE, origin_x, origin_y, scale)

    # Cekungan Parapet Dinding Pembatas Atap Atas (Berwarna Biru Luar Dalam)
    draw_iso_block(surface, -130, -130, 174, 265, 265, 12, ROOF_BLUE_TOP, ROOF_BLUE_INNER, ROOF_BLUE_TOP, origin_x, origin_y, scale)
    # Lantai Atap bagian dalam yang tenggelam
    draw_iso_block(surface, -124, -124, 172, 253, 253, 2, ROOF_BLUE_INNER, ROOF_BLUE_INNER, ROOF_BLUE_INNER, origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 8. LOGO / PAPAN EMBLEM INDOMARET UTAMA DI ATAS PINTU
    # ----------------------------------------------------
    # Dudukan Panel Papan Nama Putih Melayang sedikit ke depan
    draw_iso_block(surface, -35, 136, 150, 80, 2, 34, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, origin_x, origin_y, scale)
    # Lis Garis Merah Dalam Papan Nama
    draw_iso_block(surface, -31, 137, 153, 72, 1, 28, INDO_RED, INDO_RED, INDO_RED, origin_x, origin_y, scale)
    # Inti teks area Putih
    draw_iso_block(surface, -28, 137, 155, 66, 1, 24, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, origin_x, origin_y, scale)
    
    # Sketsa bentuk huruf logo "Indomaret" berwarna Biru di dalam papan
    draw_iso_block(surface, -18, 138, 163, 40, 1, 8, INDO_BLUE, INDO_BLUE, INDO_BLUE, origin_x, origin_y, scale)

    # ----------------------------------------------------
    # 9. PLANG TOWER LOGO INDOMARET BESAR (SISI KIRI)
    # ----------------------------------------------------
    # Tiang Besi Penopang Utama Segitiga/Kotak Hitam Tinggi
    draw_iso_block(surface, -190, 160, 0, 14, 14, 210, (50,54,58), (35,38,40), (45,48,52), origin_x, origin_y, scale)
    
    # Kepala Plang Atas (Bingkai Kotak Putih Besar)
    draw_iso_block(surface, -230, 162, 165, 65, 12, 45, WALL_FRONT_LIGHT, WALL_SIDE_SHADOW, WALL_FRONT_LIGHT, origin_x, origin_y, scale)
    # Isian Konten Plang (Kombinasi Blok Biru, Merah, Kuning Logo Mini)
    draw_iso_block(surface, -226, 163, 170, 57, 10, 35, INDO_BLUE, INDO_BLUE, INDO_BLUE, origin_x, origin_y, scale)
    draw_iso_block(surface, -226, 163, 170, 57, 10, 16, INDO_YELLOW, INDO_YELLOW, INDO_YELLOW, origin_x, origin_y, scale)
    draw_iso_block(surface, -226, 163, 186, 57, 10, 10, INDO_RED, INDO_RED, INDO_RED, origin_x, origin_y, scale)
    
    # Tiga Kotak Kecil di Bawah Plang Utama (Ciri khas Plang Indomaret)
    draw_iso_block(surface, -225, 162, 140, 55, 12, 18, INDO_BLUE, (10,55,120), INDO_BLUE, origin_x, origin_y, scale)
    draw_iso_block(surface, -215, 163, 144, 10, 10, 10, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, origin_x, origin_y, scale)
    draw_iso_block(surface, -200, 163, 144, 10, 10, 10, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, origin_x, origin_y, scale)
    draw_iso_block(surface, -185, 163, 144, 10, 10, 10, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, WALL_FRONT_LIGHT, origin_x, origin_y, scale)