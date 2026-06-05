from assets.components import *

# Mapping of component types to their render functions.
# The render function has the signature: render(screen, x, y)
REGISTRY = {
    # Editor names
    "RumahA": lambda s, x, y: RumahA(x, y).render(s),
    "RumahB": lambda s, x, y: RumahB(x, y).render(s),
    "RumahC": lambda s, x, y: RumahC(x, y).render(s),
    "RumahD": lambda s, x, y: RumahD(x, y).render(s),
    "Gedung": lambda s, x, y: Gedung(x, y).render(s),
    "GedungA": lambda s, x, y: GedungA(x, y).render(s),
    "GedungB": lambda s, x, y: GedungB(x, y).render(s),
    "GedungC": lambda s, x, y: GedungC(x, y).render(s),
    "GedungD": lambda s, x, y: GedungD(x, y).render(s),
    "Apartemen": lambda s, x, y: Apartemen(x, y).render(s),
    "BalaiKota": lambda s, x, y: BalaiKota(x, y).render(s),
    "Sekolah": lambda s, x, y: Sekolah(x, y).render(s),
    "Museum": lambda s, x, y: Museum(x, y).render(s),
    "Masjid": lambda s, x, y: Masjid(x, y).render(s),
    "RumahSakit": lambda s, x, y: RumahSakit(x, y).render(s),
    "Stadion": lambda s, x, y: Stadion(x, y).render(s),
    "PusatPerbelanjaan": lambda s, x, y: PusatPerbelanjaan(x, y).render(s),
    "Minimarket": lambda s, x, y: Minimarket(x, y).render(s),
    "Bank": lambda s, x, y: Bank(x, y).render(s),
    "SPBU": lambda s, x, y: SPBU(x, y).render(s),
    "KantorPolisi": lambda s, x, y: KantorPolisi(x, y).render(s),
    "Pemadam": lambda s, x, y: Pemadam(x, y).render(s),
    "Bandara": lambda s, x, y: Bandara(x, y).render(s),
    "Pelabuhan": lambda s, x, y: render_pelabuhan(s, x, y + 225, 'SE'),
    "Mercusuar": lambda s, x, y: draw_mercusuar(s, x, y),
    "Lampu": lambda s, x, y: render_lampu(s, x, y),
    "KapalKargo": lambda s, x, y: render_kapal_kargo_besar(s, x - 117, y + 85),
    "KapalNelayan": lambda s, x, y: render_kapal_nelayan(s, x - 100, y + 40),
    "KapalLayar": lambda s, x, y: draw_kapal_layar(s, x, y),
    "Speedboat": lambda s, x, y: draw_speedboat(s, x, y),
    "Taman": lambda s, x, y: draw_taman(s, offset_x=x - 400, offset_y=y - 300),
    "Danau": lambda s, x, y: draw_danau(s, x, y - 208),
    "Bianglala": lambda s, x, y: draw_bianglala(s, x, y - 170),
    "PohonBelakang": lambda s, x, y: PohonBelakang(x, y).render(s),
    "PohonDepan": lambda s, x, y: PohonDepan(x, y).render(s),
    "PohonBulat": lambda s, x, y: render_pohon_bulat(s, x, y),
    "PohonPinus": lambda s, x, y: draw_pohon_pinus(s, x, y),
    "LumbaLumba": lambda s, x, y: draw_lumba_lumba(s, x, y),
    "Hiu": lambda s, x, y: draw_hiu(s, x, y),


    # Procedural map generator compatibility names
    "town_hall": lambda s, x, y: BalaiKota(x, y).render(s),
    "rumah1": lambda s, x, y: RumahA(x, y).render(s),
    "rumah2": lambda s, x, y: RumahB(x, y).render(s),
    "rumah3": lambda s, x, y: RumahC(x, y).render(s),
    "rumah4": lambda s, x, y: RumahD(x, y).render(s),
    "sekolah": lambda s, x, y: Sekolah(x, y).render(s),
    "polisi": lambda s, x, y: KantorPolisi(x, y).render(s),
    "stadium": lambda s, x, y: Stadion(x, y).render(s),
    "bank": lambda s, x, y: Bank(x, y).render(s),
    "rumah_sakit2": lambda s, x, y: RumahSakit(x, y).render(s),
    "museum": lambda s, x, y: Museum(x, y).render(s),
    "mall": lambda s, x, y: PusatPerbelanjaan(x, y).render(s),
    "indomaret": lambda s, x, y: Minimarket(x, y).render(s),
    "spbu": lambda s, x, y: SPBU(x, y).render(s),
    "pelab": lambda s, x, y: render_pelabuhan(s, x, y + 225, 'SE'),
    "mersucuar": lambda s, x, y: draw_mercusuar(s, x, y),
    "kapal_kargo": lambda s, x, y: render_kapal_kargo_besar(s, x - 117, y + 85),
    "kapal_kargo2": lambda s, x, y: render_kapal_kargo_besar(s, x - 117, y + 85),
    "pohon_belakang": lambda s, x, y: PohonBelakang(x, y).render(s),
    "pohon_depan": lambda s, x, y: PohonDepan(x, y).render(s),
    "pohon_bulat": lambda s, x, y: render_pohon_bulat(s, x, y),
    "lampu": lambda s, x, y: render_lampu(s, x, y),
}

# Add kavling/plat
REGISTRY['kavling_kecil'] = lambda s, x, y: BasePlatform(x, y, 'kecil', 180, 90).render(s)
REGISTRY['kavling_sedang'] = lambda s, x, y: BasePlatform(x, y, 'sedang', 380, 190).render(s)
REGISTRY['kavling_besar'] = lambda s, x, y: BasePlatform(x, y, 'besar', 520, 260).render(s)
REGISTRY['kavling_kecil_inv'] = lambda s, x, y: BasePlatform(x, y, 'kecil', 90, 180).render(s)
REGISTRY['kavling_sedang_inv'] = lambda s, x, y: BasePlatform(x, y, 'sedang', 190, 380).render(s)
REGISTRY['kavling_besar_inv'] = lambda s, x, y: BasePlatform(x, y, 'besar', 260, 520).render(s)

def get_render_fn(tipe: str):
    # Case insensitive check
    for k, fn in REGISTRY.items():
        if k.lower() == tipe.lower():
            return fn
    # Fallback to empty renderer if not found
    return lambda s, x, y: None

def list_by_zone(zone: str) -> list[str]:
    # Placeholder for zone mapping if needed in visualizer
    return []

def list_by_kategori(kategori: str) -> list[str]:
    # Placeholder for category mapping if needed in visualizer
    return []
