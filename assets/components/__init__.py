import pygame
import math

# Import classes directly
from assets.components.gedung import render_gedung
from assets.components.pohon import PohonBelakang, PohonDepan
from assets.components.rumah_a import RumahA
from assets.components.rumah_b import RumahB
from assets.components.rumah_c import RumahC
from assets.components.rumah_d import RumahD
from assets.components.sekolah import Sekolah
from assets.components.museum import Museum
from assets.components.balai_kota import BalaiKota
from assets.components.spbu import SPBU
from assets.components.apartemen import Apartemen
from assets.components.pemadam import Pemadam
from assets.components.bandara import Bandara
from assets.components.pulau import Pulau

# Import raw drawing functions
from assets.components.rumah_sakit import draw_rumah_sakit
from assets.components.stadion import draw_stadion
from assets.components.pusat_perbelanjaan import draw_pusat_perbelanjaan
from assets.components.minimarket import draw_minimarket
from assets.components.kantor_polisi import render_kantor_polisi
from assets.components.kapal_nelayan import render_kapal_nelayan
from assets.components.lampu import render_lampu
from assets.components.pohon_bulat import render_pohon as render_pohon_bulat
from assets.components.mercusuar import draw_mercusuar
from assets.components.bank import draw_bank
from assets.components.gedung_a import draw_gedungA
from assets.components.gedung_b import draw_gedungB
from assets.components.gedung_c import draw_gedungC
from assets.components.gedung_d import draw_gedungD
from assets.components.kapal_kargo_besar import render_kapal_kargo_besar
from assets.components.pelabuhan import render_pelabuhan
from assets.components.bianglala import draw_bianglala
from assets.components.taman import draw_taman
from assets.components.speedboat import draw_speedboat
def draw_lumba_lumba(screen, x, y): pass

from assets.components.hiu import draw_hiu
from assets.components.kapal_layar import draw_kapal_layar
from assets.components.masjid import draw_masjid
from assets.components.danau import draw_danau
from assets.components.pohon_pinus import draw_pohon as draw_pohon_pinus

from assets.components.terrain import TerrainSystem
from assets.components.alas import BasePlatform
from assets.components.jalan import RoadSegment, RoadCorner90, Roundabout, screen_to_grid, grid_to_screen

# --- WRAPPER CLASSES FOR FUNCTION-BASED COMPONENTS ---

class RumahSakit:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_rumah_sakit(screen, self.x + 20 * scale, self.y - 179 * scale, scale=scale)

class Stadion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_stadion(screen, self.x, self.y - 32 * scale, width=int(1000 * scale), height=int(800 * scale))

class PusatPerbelanjaan:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_pusat_perbelanjaan(screen, self.x, self.y - 136 * scale, scale=scale)

class Minimarket:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_minimarket(screen, self.x, self.y, scale=0.6 * scale)

class KantorPolisi:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_kantor_polisi(screen, self.x, self.y, scale=scale)

class Hiu:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_hiu(screen, self.x, self.y)

class KapalNelayan:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        render_kapal_nelayan(screen, self.x - 100, self.y + 40)

class Lampu:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, "scale", 1.0)
        render_lampu(screen, self.x, self.y, scale=scale * 0.4)

class PohonBulat:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        render_pohon_bulat(screen, self.x, self.y)

class Mercusuar:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_mercusuar(screen, self.x, self.y)

class Bank:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_bank(screen, self.x - 40 * scale, self.y - 100 * scale, scale=scale)

class Gedung:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_gedung(screen, self.x, self.y + 150 * scale, scale=scale)

class GedungA:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_gedungA(screen, self.x, self.y - 108 * scale, scale=scale)

class GedungB:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_gedungB(screen, self.x - 32 * scale, self.y - 152 * scale, scale=scale)

class GedungC:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_gedungC(screen, self.x, self.y - 168 * scale, scale=scale)

class GedungD:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_gedungD(screen, self.x, self.y, scale=scale)

class KapalKargo:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        render_kapal_kargo_besar(screen, self.x - 117, self.y + 85)

class Pelabuhan:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.direction = 'SE'
    def render(self, screen):
        render_pelabuhan(screen, self.x, self.y + 225, self.direction)

class Bianglala:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_bianglala(screen, self.x, self.y - 170)

class Taman:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_taman(screen, offset_x=self.x - 400, offset_y=self.y - 300)

class Speedboat:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_speedboat(screen, self.x, self.y)

class LumbaLumba:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_lumba_lumba(screen, self.x, self.y)



class KapalLayar:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_kapal_layar(screen, self.x, self.y)

class Masjid:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_masjid(screen, self.x, self.y, scale=scale)

class Danau:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        draw_danau(screen, self.x, self.y - 208)

class PohonPinus:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def render(self, screen):
        draw_pohon_pinus(screen, self.x, self.y)
