import pygame

KAYU_KIRI, KAYU_KANAN = (75, 50, 35), (105, 75, 55)
DAUN_KIRI, DAUN_KANAN = (60, 110, 55), (85, 145, 80)

def gambar_poligon(layar, warna, titik, ketebalan=0):
    pygame.draw.polygon(layar, warna, titik, ketebalan)
    if ketebalan == 0:
        pygame.draw.aalines(layar, warna, True, titik)

def gambar_blok(layar, x, y, dx, dy, tinggi, w_kiri, w_kanan, w_atas):
    gambar_poligon(layar, w_kiri, [(x, y), (x-dx, y-dy), (x-dx, y-dy-tinggi), (x, y-tinggi)])
    gambar_poligon(layar, w_kanan, [(x, y), (x+dx, y-dy), (x+dx, y-dy-tinggi), (x, y-tinggi)])
    gambar_poligon(layar, w_atas, [(x, y-tinggi), (x-dx, y-dy-tinggi), (x, y-dy*2-tinggi), (x+dx, y-dy-tinggi)])

def buat_sebatang_pohon(layar, x, y, scale=2.2):
    gambar_blok(layar, x, y, 6*scale, 3*scale, 15*scale, KAYU_KIRI, KAYU_KANAN, (120, 90, 70))
    def daun(bx, by, lbr, tgg):
        gambar_poligon(layar, DAUN_KIRI, [(bx, by), (bx-lbr, by-lbr/2), (bx, by-tgg)])
        gambar_poligon(layar, DAUN_KANAN, [(bx, by), (bx+lbr, by-lbr/2), (bx, by-tgg)])
        pygame.draw.aaline(layar, (40, 80, 40), (bx, by), (bx, by-tgg))
    
    daun(x, y-10*scale, 25*scale, 30*scale)
    daun(x, y-22*scale, 20*scale, 28*scale)
    daun(x, y-35*scale, 15*scale, 25*scale) 

def render_pohon_belakang(layar, cx, cy):
    buat_sebatang_pohon(layar, cx, cy, scale=2.2)

def render_pohon_depan(layar, cx, cy):
    buat_sebatang_pohon(layar, cx, cy, scale=1.7)


# --- CLASS WRAPPER UNTUK OOP ---
class PohonBelakang:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def render(self, screen):
        render_pohon_belakang(screen, self.x, self.y)

class PohonDepan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def render(self, screen):
        render_pohon_depan(screen, self.x, self.y)
