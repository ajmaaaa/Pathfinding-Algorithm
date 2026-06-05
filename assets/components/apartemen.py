import pygame

# --- PALET WARNA (LUXURY MODERN APARTMENT) ---
WALL_L = (245, 250, 255)     # Dinding kiri cerah
WALL_R = (215, 220, 225)     # Dinding kanan bayangan
WALL_TOP = (230, 235, 240)   # Atap
GLASS_L = (160, 220, 245)    # Kaca cyan terang
GLASS_R = (130, 190, 215)    # Kaca cyan gelap
WOOD_L = (160, 110, 80)      # Aksen kayu terang
WOOD_R = (130, 85, 60)       # Aksen kayu gelap
WOOD_TOP = (180, 130, 95)
BALCONY_L = (255, 255, 255)  # Plat balkon cerah
BALCONY_R = (225, 230, 235)  # Plat balkon gelap
RAILING_L = (180, 240, 255)  # Kaca balkon kiri
RAILING_R = (140, 210, 235)  # Kaca balkon kanan
PLANT_TOP = (110, 190, 90)   # Daun atas
PLANT_L = (80, 150, 60)      # Daun kiri
PLANT_R = (50, 120, 40)      # Daun kanan
LINE_COL = (60, 70, 80)      # Outline hitam kebiruan
FOUNDATION = (120, 125, 130) # Beton bawah

def render_apartemen(screen, cx, cy, scale=1.0):
    # Proyeksi Isometrik
    def iso(x, y, z):
        scale_x, scale_y = 1.6 * scale, 0.8 * scale
        sx = cx + (x - y) * scale_x
        sy = cy + ((x + y) * 0.8 - z) * scale
        return sx, sy

    # Fungsi gambar poligon dengan outline
    def draw_poly(points_3d, color, outline=True, thickness=1):
        pts_2d = [iso(x, y, z) for x, y, z in points_3d]
        pygame.draw.polygon(screen, color, pts_2d)
        if outline:
            pygame.draw.polygon(screen, LINE_COL, pts_2d, thickness)

    # Fungsi gambar balok 3D standar (Atap, Kiri, Kanan)
    def draw_block(x1, x2, y1, y2, z1, z2, c_top, c_front, c_side):
        draw_poly([(x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)], c_top)
        draw_poly([(x1, y2, z1), (x2, y2, z1), (x2, y2, z2), (x1, y2, z2)], c_front)
        draw_poly([(x2, y1, z1), (x2, y2, z1), (x2, y2, z2), (x2, y1, z2)], c_side)

    def draw_tree(x, y, z):
        # Pot
        draw_block(x-4, x+4, y-4, y+4, z, z+4, (120, 120, 120), (100, 100, 100), (80, 80, 80))
        # Daun
        draw_block(x-8, x+8, y-8, y+8, z+4, z+25, PLANT_TOP, PLANT_L, PLANT_R)

    # =========================================================================
    # RENDER TOWER (Bawah ke Atas)
    # Tower berbentuk kotak solid (X: 20-140, Y: 20-140) agar tidak ada bug Z-sorting
    # Semua balkon dan aksesoris diletakkan di sisi depan (Y=140 dan X=140)
    # =========================================================================

    # --- TOWER UTAMA (Z=0..120) ---
    floor_h = 30
    total_floors = 10

    for i in range(total_floors):
        z_fl = i * floor_h
        
        # --- LOBBY (Lantai 1) ---
        if i == 0:
            # Dinding kaca full untuk lobby
            draw_block(20, 140, 20, 140, z_fl, z_fl + floor_h, WALL_TOP, GLASS_L, GLASS_R)
            
            # Tiang pilar lobby
            draw_block(20, 30, 140, 145, z_fl, z_fl + floor_h, WALL_TOP, WALL_L, WALL_R)
            draw_block(130, 140, 140, 145, z_fl, z_fl + floor_h, WALL_TOP, WALL_L, WALL_R)
            draw_block(140, 145, 20, 30, z_fl, z_fl + floor_h, WALL_TOP, WALL_L, WALL_R)
            draw_block(140, 145, 130, 140, z_fl, z_fl + floor_h, WALL_TOP, WALL_L, WALL_R)
            
            # Tiang kanopi (DIGAMBAR SEBELUM KANOPI AGAR TIDAK MENIMPA)
            draw_block(62, 66, 153, 157, z_fl, z_fl + 20, WALL_TOP, WALL_L, WALL_R)
            draw_block(94, 98, 153, 157, z_fl, z_fl + 20, WALL_TOP, WALL_L, WALL_R)
            # Kanopi Pintu Masuk (Kiri / Y=140)
            draw_block(60, 100, 140, 160, z_fl + 20, z_fl + 25, WOOD_TOP, WOOD_L, WOOD_R)
            
            # Pintu Kaca Lobby Utama (Di bawah kanopi)
            draw_block(70, 90, 140, 142, z_fl, z_fl + 20, WALL_TOP, (100, 150, 180), GLASS_R)
            pygame.draw.line(screen, LINE_COL, iso(80, 142, z_fl), iso(80, 142, z_fl+20), 2)
            continue
            
        # --- LANTAI APARTEMEN (Lantai 2 - 10) ---
        
        # Blok bangunan utama (Putih)
        draw_block(20, 140, 20, 140, z_fl, z_fl + floor_h, WALL_TOP, WALL_L, WALL_R)
        
        # Aksen Pilar Kayu Besar di sudut depan (X=130-142, Y=130-142)
        draw_block(125, 142, 125, 142, z_fl, z_fl + floor_h, WOOD_TOP, WOOD_L, WOOD_R)
        
        # Jendela Kaca Kiri (Front-Left, Y=140)
        draw_block(30, 115, 140, 141, z_fl + 5, z_fl + 25, WALL_TOP, GLASS_L, GLASS_R)
        # Pintu Balkon Kiri
        draw_block(70, 85, 140, 142, z_fl, z_fl + 20, WALL_TOP, (110, 160, 190), GLASS_R)
        pygame.draw.line(screen, LINE_COL, iso(77, 142, z_fl), iso(77, 142, z_fl+20), 1)
        
        # Jendela Kaca Kanan (Front-Right, X=140)
        draw_block(140, 141, 30, 115, z_fl + 5, z_fl + 25, WALL_TOP, GLASS_L, GLASS_R)
        # Pintu Balkon Kanan
        draw_block(140, 142, 70, 85, z_fl, z_fl + 20, WALL_TOP, GLASS_L, (110, 160, 190))
        pygame.draw.line(screen, LINE_COL, iso(142, 77, z_fl), iso(142, 77, z_fl+20), 1)
        
        # Balkon Kiri (Front-Left, Y menonjol keluar)
        bx1, bx2 = 30, 115
        by1, by2 = 140, 155
        # Plat lantai balkon
        draw_block(bx1, bx2, by1, by2, z_fl, z_fl + 3, WALL_TOP, BALCONY_L, BALCONY_R)
        # Pembatas Samping Kiri Balkon
        draw_block(bx1, bx1+2, by1, by2, z_fl+3, z_fl+15, WALL_TOP, WALL_L, WALL_R)
        # Pembatas Samping Kanan Balkon
        draw_block(bx2-2, bx2, by1, by2, z_fl+3, z_fl+15, WALL_TOP, WALL_L, WALL_R)
        # Kaca Railing Depan Balkon (menggunakan block agar berdimensi)
        draw_block(bx1, bx2, by2-2, by2, z_fl+3, z_fl+15, RAILING_L, RAILING_L, RAILING_R)
        
        # Balkon Kanan (Front-Right, X menonjol keluar)
        rx1, rx2 = 140, 155
        ry1, ry2 = 30, 115
        draw_block(rx1, rx2, ry1, ry2, z_fl, z_fl + 3, WALL_TOP, BALCONY_L, BALCONY_R)
        # Pembatas Samping Belakang Balkon
        draw_block(rx1, rx2, ry1, ry1+2, z_fl+3, z_fl+15, WALL_TOP, WALL_L, WALL_R)
        # Pembatas Samping Depan Balkon
        draw_block(rx1, rx2, ry2-2, ry2, z_fl+3, z_fl+15, WALL_TOP, WALL_L, WALL_R)
        # Kaca Railing Kanan Balkon
        draw_block(rx2-2, rx2, ry1, ry2, z_fl+3, z_fl+15, RAILING_L, RAILING_L, RAILING_R)
        
        # Tanaman Hias Balkon (Berselang-seling setiap lantai)
        if i % 2 == 0:
            draw_block(bx1+4, bx1+25, by2-6, by2-2, z_fl+3, z_fl+12, PLANT_TOP, PLANT_L, PLANT_R)
        else:
            draw_block(rx2-6, rx2-2, ry2-25, ry2-4, z_fl+3, z_fl+12, PLANT_TOP, PLANT_L, PLANT_R)

    # 2. ROOFTOP (Z_TOP = 300)
    z_roof = total_floors * floor_h
    
    # Menara Lift / Tangga di atap (Kayu)
    draw_block(40, 70, 40, 70, z_roof, z_roof + 35, WOOD_TOP, WOOD_L, WOOD_R)
    # Pintu Menara Atap (Menghadap Kiri/Depan)
    draw_block(50, 60, 69, 71, z_roof, z_roof + 18, (100, 100, 100), (80, 80, 80), (60, 60, 60))
    pygame.draw.line(screen, LINE_COL, iso(58, 71, z_roof), iso(58, 71, z_roof+18), 1)
    
    # Infinity Pool (Kolam renang tanpa batas di sudut depan)
    draw_block(80, 135, 80, 135, z_roof, z_roof + 8, (220, 230, 240), WALL_L, WALL_R)
    # Air kolam
    draw_poly([(82, 82, z_roof+7), (133, 82, z_roof+7), (133, 133, z_roof+7), (82, 133, z_roof+7)], (80, 200, 240), outline=False)
    
    # Pohon Hias di Rooftop
    draw_tree(100, 50, z_roof)
    draw_tree(120, 50, z_roof)
    draw_tree(50, 100, z_roof)
    draw_tree(50, 120, z_roof)

    # Pagar kaca keliling Rooftop
    draw_poly([(20, 140, z_roof), (140, 140, z_roof), (140, 140, z_roof+12), (20, 140, z_roof+12)], RAILING_L, outline=False)
    draw_poly([(140, 20, z_roof), (140, 140, z_roof), (140, 140, z_roof+12), (140, 20, z_roof+12)], RAILING_R, outline=False)

class Apartemen:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0

    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_apartemen(screen, self.x, self.y - 128 * scale, scale=scale)
