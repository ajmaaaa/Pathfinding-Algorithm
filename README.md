# Pathfinding Algorithm — A\* Visualizer

Visualisasi algoritma pencarian jalur A\* di atas peta kota isometrik yang di-*generate* secara prosedural.

## Cara Menjalankan

```bash
pip install -r requirements.txt
python main.py
```

## Struktur Repository

```
Pathfinding-Algorithm/
│
├── main.py                        # Entry point — jalankan ini
├── config.py                      # Konstanta global (layar, warna, FPS)
├── requirements.txt
│
├── src/
│   ├── core/                      # Logika inti aplikasi
│   │   ├── app.py                 # App loop utama (event, render, kamera)
│   │   ├── city_gen.py            # Generator peta prosedural (node + edge)
│   │   ├── graph.py               # Struktur data Node & Edge
│   │   └── geometry.py            # Utilitas geometri (smooth path, dll.)
│   │
│   ├── algorithm/                 # Implementasi A*
│   │   ├── pathfinder.py          # Algoritma A* + animasi
│   │   ├── heuristic.py           # Fungsi heuristik (Euclidean, Manhattan)
│   │   └── min_heap.py            # Priority queue (min-heap) custom
│   │
│   ├── renderer/                  # Sistem render kamera & layer
│   │   ├── camera.py              # Kamera (pan, zoom, world↔screen)
│   │   ├── static_renderer.py     # Layer statis: background, jalan, graph
│   │   └── dynamic_renderer.py    # Layer dinamis: animasi A*, mobil
│   │
│   ├── mapgen/                    # Penempatan & render bangunan lama
│   │   ├── building_placer.py     # Logika penempatan bangunan di peta
│   │   ├── building_renderer.py   # Render bangunan (dispatcher ke komponen)
│   │   └── else_renderer.py       # Render elemen lain (pin, dll.)
│   │
│   ├── ui/                        # Antarmuka pengguna
│   │   ├── ribbon.py              # Ribbon toolbar atas (tombol, slider)
│   │   ├── hud.py                 # Badge, tooltip, overlay
│   │   └── loading.py             # Layar loading
│   │
│   └── components/                # ★ KOMPONEN VISUAL ISOMETRIK ★
│       ├── component_registry.py  # Registri pusat semua komponen
│       │
│       ├── bangunan/              # Gedung & bangunan buatan manusia
│       │   ├── gedung.py          # Gedung kaca bertingkat + helipad
│       │   ├── rumah.py           # Rumah klasik + atap limas
│       │   ├── sekolah.py         # Sekolah L-shape + jam dinding
│       │   ├── rumah_sakit.py     # RS modern + ambulans
│       │   └── TEMPLATE_KOMPONEN.py # Untuk komponen baru jika ada
│       │
│       ├── alam/                  # Elemen alam
│       │   └── pohon.py           # Pohon isometrik (depan & belakang)
│       │
│       ├── infrastruktur/         # Jalan, jembatan, lampu, rambu
│       │   └── (dalam pengembangan)
│       │
│       └── latar/                 # Tile tanah, laut, langit
│           └── (dalam pengembangan)
│
├── tests/                         # Unit test
│   ├── test_astar.py
│   ├── test_geometry.py
│   ├── test_map_gen.py
│   └── test_min_heap.py
│
├── assets/
│   └── fonts/                     # Font
│
└── docs/                          # Dokumentasi tambahan
```

## Cara Menambah Komponen Baru

1. **Salin template:**
   ```bash
   cp src/components/bangunan/TEMPLATE_KOMPONEN.py src/components/bangunan/masjid.py
   ```

2. **Isi fungsi `render_<nama>(layar, cx, cy)`** di file baru.

3. **Daftarkan di `__init__.py` subfolder:**
   ```python
   # src/components/bangunan/__init__.py
   from .masjid import render_masjid
   __all__ = [..., "render_masjid"]
   ```

4. **Tambahkan ke `component_registry.py`:**
   ```python
   "masjid": {
       "render"   : render_masjid,
       "kategori" : "bangunan",
       "tier"     : 2,
       "walkable" : False,
   }
   ```

## Komponen yang Sudah Ada

| Komponen       | Kategori       | Tier |
|----------------|----------------|------|
| gedung         | bangunan       | 3    |
| sekolah        | bangunan       | 2    |
| rumah_sakit    | bangunan       | 2    |
| rumah          | bangunan       | 1    |
| pohon_belakang | alam           | 1    |
| pohon_depan    | alam           | 1    |

## Komponen yang Direncanakan

- `latar/laut.py` — Tile laut / air dengan efek gelombang
- `latar/pantai.py` — Garis pantai (transisi darat↔laut)
- `alam/sungai.py` — Sungai dengan jembatan
- `infrastruktur/jalan.py` — Segmen jalan isometrik
- `infrastruktur/jembatan.py` — Jembatan
- `bangunan/masjid.py` — Masjid dengan kubah
- `bangunan/toko.py` — Toko/ruko
