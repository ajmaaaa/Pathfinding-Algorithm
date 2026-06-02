import pygame

# --- Konstanta & Skala Isometrik ---
TILE_W = 16
TILE_H = 8
Z_SCALE = 8

# --- Palet Warna (Sesuai Gambar) ---
C_WHITE     = (245, 245, 250)
C_ROAD_TOP  = (65, 65, 70)
C_ROAD_SIDE = (45, 45, 50)
C_LINE      = (255, 255, 255)

C_BASE_TOP  = (145, 140, 145)
C_BASE_L    = (125, 115, 115)  # Terang (Kiri)
C_BASE_R    = (100, 90, 90)    # Gelap (Kanan)
C_WIN_L     = (0, 170, 220)
C_WIN_R     = (0, 120, 170)

C_TOWER_TOP = (220, 225, 235)
C_TOWER_L   = (0, 180, 255)    # Biru Kaca Terang
C_TOWER_R   = (0, 115, 210)    # Biru Kaca Gelap
C_GLASS_LIN = (120, 210, 255)

C_TREE_TRNK = (100, 70, 50)
C_TREE_TOP  = (140, 200, 50)
C_TREE_SIDE = (110, 170, 30)

C_CAR_RED_T = (220, 50, 50)
C_CAR_RED_S = (170, 30, 30)
C_CAR_WHT_T = (240, 240, 245)
C_CAR_WHT_S = (190, 190, 195)

def to_iso(x, y, z, anchor_x, anchor_y, scale=1.0):
    """Konversi koordinat 3D ke 2D Layar Isometrik"""
    sx = (x - y) * TILE_W * scale + anchor_x
    sy = (x + y) * TILE_H * scale - z * Z_SCALE * scale + anchor_y
    return sx, sy

class Block3D:
    """Kelas untuk membuat dan merender balok 3D Isometrik secara terstruktur"""
    def __init__(self, x, y, z, w, d, h, c_top, c_left, c_right, style=None):
        self.x, self.y, self.z = x, y, z
        self.w, self.d, self.h = w, d, h
        self.c_top = c_top
        self.c_left = c_left
        self.c_right = c_right
        self.style = style
        # Kunci pengurutan (Painter's Algorithm)
        self.order = self.x + self.y + self.z

    def draw(self, surface, ax, ay, scale=1.0):
        x, y, z = self.x, self.y, self.z
        w, d, h = self.w, self.d, self.h

        # Titik sudut Poligon
        p_top = [to_iso(x, y, z+h, ax, ay, scale), to_iso(x+w, y, z+h, ax, ay, scale), 
                 to_iso(x+w, y+d, z+h, ax, ay, scale), to_iso(x, y+d, z+h, ax, ay, scale)]
        p_left = [to_iso(x, y+d, z, ax, ay, scale), to_iso(x+w, y+d, z, ax, ay, scale), 
                  to_iso(x+w, y+d, z+h, ax, ay, scale), to_iso(x, y+d, z+h, ax, ay, scale)]
        p_right = [to_iso(x+w, y, z, ax, ay, scale), to_iso(x+w, y+d, z, ax, ay, scale), 
                   to_iso(x+w, y+d, z+h, ax, ay, scale), to_iso(x+w, y, z+h, ax, ay, scale)]

        # Gambar sisi dinding dan atap
        pygame.draw.polygon(surface, self.c_left, p_left)
        pygame.draw.polygon(surface, self.c_right, p_right)
        pygame.draw.polygon(surface, self.c_top, p_top)

        # Tambahkan Jendela Kotak (Base Abu-abu)
        if self.style == "square":
            # Jendela Kiri
            for i in range(int(w)):
                for j in range(int(h)):
                    wx1, wx2 = x + i + 0.2, x + i + 0.8
                    wz1, wz2 = z + j + 0.2, z + j + 0.8
                    wy = y + d
                    pts = [to_iso(wx1, wy, wz1, ax, ay, scale), to_iso(wx2, wy, wz1, ax, ay, scale), 
                           to_iso(wx2, wy, wz2, ax, ay, scale), to_iso(wx1, wy, wz2, ax, ay, scale)]
                    pygame.draw.polygon(surface, C_WIN_L, pts)
            
            # Jendela Kanan
            for i in range(int(d)):
                for j in range(int(h)):
                    wy1, wy2 = y + i + 0.2, y + i + 0.8
                    wz1, wz2 = z + j + 0.2, z + j + 0.8
                    wx = x + w
                    pts = [to_iso(wx, wy1, wz1, ax, ay, scale), to_iso(wx, wy2, wz1, ax, ay, scale), 
                           to_iso(wx, wy2, wz2, ax, ay, scale), to_iso(wx, wy1, wz2, ax, ay, scale)]
                    pygame.draw.polygon(surface, C_WIN_R, pts)

        # Tambahkan Garis Kaca (Gedung Biru)
        elif self.style == "glass":
            # Garis Vertikal & Horizontal Kiri
            for i in range(1, int(w)):
                pygame.draw.line(surface, C_GLASS_LIN, to_iso(x+i, y+d, z, ax, ay, scale), to_iso(x+i, y+d, z+h, ax, ay, scale), 1)
            for j in range(2, int(h), 3):
                pygame.draw.line(surface, C_GLASS_LIN, to_iso(x, y+d, z+j, ax, ay, scale), to_iso(x+w, y+d, z+j, ax, ay, scale), max(1, int(2*scale)))
            
            # Garis Vertikal & Horizontal Kanan
            for i in range(1, int(d)):
                pygame.draw.line(surface, C_GLASS_LIN, to_iso(x+w, y+i, z, ax, ay, scale), to_iso(x+w, y+i, z+h, ax, ay, scale), 1)
            for j in range(2, int(h), 3):
                pygame.draw.line(surface, C_GLASS_LIN, to_iso(x+w, y, z+j, ax, ay, scale), to_iso(x+w, y+d, z+j, ax, ay, scale), max(1, int(2*scale)))


def draw_gedungB(screen, anchor_x, anchor_y, scale=1.0):
    blocks = []

    # (Base slab, taman, dan pohon dihapus agar tidak tumpang tindih di klaster CBD)
    # CBD base sudah menyediakan alas bersama.

    # 4. Podium Dasar (Lantai Bawah)
    blocks.append(Block3D(6, 4, 0.2, 9, 9, 4, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))

    # 5. Menara Kaca Biru Utama
    blocks.append(Block3D(6, 4, 4.2, 6, 6, 26, C_TOWER_TOP, C_TOWER_L, C_TOWER_R, "glass"))
    # Detail Atap Menara (Rim)
    blocks.append(Block3D(6.2, 4.2, 30.2, 5.6, 5.6, 0.5, C_BASE_TOP, C_BASE_L, C_BASE_R))

    # 6. Podium Bertingkat Kanan (Samping Menara)
    blocks.append(Block3D(12, 4, 4.2, 3, 3, 16, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))
    blocks.append(Block3D(12, 7, 4.2, 3, 3, 10, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))
    blocks.append(Block3D(12, 10, 4.2, 3, 3, 5, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))

    # 7. Podium Bertingkat Depan Kiri
    blocks.append(Block3D(6, 10, 4.2, 3, 3, 13, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))
    blocks.append(Block3D(9, 10, 4.2, 3, 3, 7, C_BASE_TOP, C_BASE_L, C_BASE_R, "square"))

    # Pintu Masuk (Garis Gelap)
    blocks.append(Block3D(10, 12.8, 0.2, 1.5, 0.3, 2.0, (40,40,40), (30,30,30), (30,30,30)))

    # Urutkan blok dari belakang ke depan (Painter's Algorithm)
    blocks.sort(key=lambda b: b.order)

    # Render semua blok
    for block in blocks:
        block.draw(screen, anchor_x, anchor_y, scale)