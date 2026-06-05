# ═══════════════════════════════════════════════════════
#  KONFIGURASI GLOBAL
# ═══════════════════════════════════════════════════════
import subprocess
import threading

_current_theme = 'dark'
_theme_lock = threading.Lock()

def _check_theme_worker():
    global _current_theme
    theme = 'dark'
    try:
        # Check GNOME color scheme
        res = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                             capture_output=True, text=True, timeout=1.0)
        if res.returncode == 0:
            val = res.stdout.strip().strip("'").strip('"')
            if 'dark' in val:
                theme = 'dark'
            elif 'light' in val:
                theme = 'light'
            else:
                # Check GTK theme if color-scheme is default/unknown
                res2 = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                                      capture_output=True, text=True, timeout=1.0)
                if res2.returncode == 0:
                    val2 = res2.stdout.strip().lower().strip("'").strip('"')
                    if 'dark' in val2:
                        theme = 'dark'
                    else:
                        theme = 'light'
    except Exception:
        pass
        
    with _theme_lock:
        _current_theme = theme

# Run initial check synchronously at import
_check_theme_worker()

def start_theme_check_thread():
    t = threading.Thread(target=_check_theme_worker, daemon=True)
    t.start()

def get_system_theme():
    with _theme_lock:
        return _current_theme

SCREEN_W  = 1280
SCREEN_H  = 800
RIBBON_H  = 88      
FPS       = 60
RW        = 85      
LP        = 1200    
SEARCH_ANIM_SPEED = 0.0012  # Kecepatan visualisasi pencarian rute (lebih lambat)
DRIVE_ANIM_SPEED = 0.008   # Kecepatan jalannya mobil setelah rute ditemukan

C = {
  'bg'        : (15, 80, 150),    # Lautan / Samudra (Warna BG original)
  'sand'      : (237, 214, 155),   # Pasir pantai
  'grass'     : (125, 206, 116),   # Daratan pulau (rumput)
  'road_shadow': (50, 60, 65),
  'road_outer': (140, 150, 155),   
  'road_inner': (40, 48, 52),     
  'road_line' : (255, 255, 255),   
  'rb_grass'  : (82, 190, 128),    
  'win_light' : (174, 214, 241),
  'win_dark'  : (26, 143, 193),
  'brick'     : (203, 67, 53),
  'conc'      : (242, 243, 244),
  'roof'      : (125, 60, 152),
  'tree_top'  : (82, 190, 128),
  'tree_trunk': (110, 76, 62),
  'apt'       : [(230,126,34),(41,128,185),(26,188,156),(142,68,173),
                 (243,156,18),(231,76,60),(39,174,96)],
  'white'     : (255, 255, 255),
  'black'     : (0, 0, 0),
  'ribbon_bg' : (252, 253, 255),
  'ribbon_top': (255, 255, 255),
  'ribbon_sep': (224, 228, 238),
  'btn_hov'   : (237, 242, 255),
  'btn_act'   : (224, 234, 255),
  'btn_border': (180, 204, 255),
  'txt_dark'  : (30,  41,  82),
  'txt_dim'   : (148, 158, 184),
  'txt_label' : (120, 132, 165),
  'stat_blue' : (37,  99,  235),
  'stat_purp' : (109,  40, 217),
  'stat_teal' : (13,  148, 136),
  'stat_amber': (202,  96,   6),
  'stat_rose' : (220,  38,  72),
}

NAME_T1 = ["Rumah Warga", "Toko Kelontong", "Warung Kopi", "Klinik Desa", "Rumah Budi", "Kios Mini", "Rumah Singgah"]
NAME_T2 = ["Apartemen Mawar", "Sekolah Dasar", "Pusat Perbelanjaan", "Kantor Cabang", "Klinik Utama", "Gedung Serbaguna", "Asrama"]
NAME_T3 = ["Menara Bisnis", "Gedung Kaca Korporat", "Kantor Pusat", "Tower Eksekutif", "Bank Sentral", "Hotel Bintang 5"]
NAME_TREE = ["Taman Kota", "Ruang Terbuka Hijau", "Taman Bermain", "Hutan Lindung", "Pohon Beringin"]
