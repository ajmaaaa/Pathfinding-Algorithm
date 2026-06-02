import random
import math
from config import RW, LP, NAME_T1, NAME_T2, NAME_T3, NAME_TREE, C
from assets.components.component_registry import list_by_zone, list_by_kategori

def _point_in_polygon(x, y, polygon):
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        crosses = (yi > y) != (yj > y)
        if crosses:
            x_at_y = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_at_y:
                inside = not inside
        j = i
    return inside

def get_building_radius(tp):
    """Return an approximate collision radius for a given building type."""
    tp_lower = tp.lower()
    if 'stadium' in tp_lower or 'mall' in tp_lower or 'pabrik' in tp_lower:
        return 770
    elif 'sakit' in tp_lower or 'kampus' in tp_lower or 'museum' in tp_lower or 'gedung' in tp_lower:
        return 480
    elif 'apartemen' in tp_lower or 'sekolah' in tp_lower or 'town' in tp_lower or 'polisi' in tp_lower or 'pemadam' in tp_lower:
        return 396
    elif 'pohon' in tp_lower:
        return 176
    elif 'kavling' in tp_lower:
        if 'kecil' in tp_lower:
            return 396
        elif 'sedang' in tp_lower:
            return 836
        elif 'besar' in tp_lower:
            return 1144
        return 396
    else:
        return 308


def _min_dist_to_road_edges(px, py, edges, edge_curves):
    """Hitung jarak minimum dari titik (px,py) ke edge jalan terdekat."""
    min_d = float('inf')
    for e in edges:
        pts = edge_curves.get(id(e))
        if not pts:
            pts = [(e[0].x, e[0].y), (e[1].x, e[1].y)]
        # Sample setiap ~5 segmen untuk kecepatan
        step = max(1, len(pts) // 8)
        for i in range(step, len(pts), step):
            x1, y1 = pts[i - step]
            x2, y2 = pts[i]
            l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
            if l2 == 0:
                d = math.hypot(px - x1, py - y1)
            else:
                t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
                cpx = x1 + t * (x2 - x1)
                cpy = y1 + t * (y2 - y1)
                d = math.hypot(px - cpx, py - cpy)
            if d < min_d:
                min_d = d
    return min_d


def _find_safe_position(cx, cy, edges, edge_curves, R_building, island_outline=None, max_attempts=24):
    """
    Coba temukan posisi aman yang cukup jauh dari jalan dan berada di dalam pulau.
    """
    safe_dist = (RW * 1.95) + R_building
    d = _min_dist_to_road_edges(cx, cy, edges, edge_curves)
    if d >= safe_dist:
        if island_outline is None or _point_in_polygon(cx, cy, island_outline):
            return cx, cy

    best_x, best_y = cx, cy
    max_d = d if (island_outline is None or _point_in_polygon(cx, cy, island_outline)) else -1

    for ring in range(1, 4):
        radius = safe_dist * (ring * 0.7)
        for attempt in range(max_attempts):
            angle = attempt * (2 * math.pi / max_attempts)
            nx = cx + math.cos(angle) * radius
            ny = cy + math.sin(angle) * radius
            
            # Pastikan berada di dalam pulau
            if island_outline and not _point_in_polygon(nx, ny, island_outline):
                continue
                
            d2 = _min_dist_to_road_edges(nx, ny, edges, edge_curves)
            if d2 >= safe_dist:
                return nx, ny
            if d2 > max_d:
                max_d = d2
                best_x, best_y = nx, ny
                
    return best_x, best_y


def _compute_block_centroids(nodes):
    """
    Hitung titik-titik tengah 'city block' dari posisi node intersection.
    Menggunakan posisi node untuk menentukan area antara jalan.
    """
    if len(nodes) < 4:
        return []

    # Sortir node berdasarkan y (baris), kemudian x (kolom)
    sorted_nodes = sorted(nodes, key=lambda n: (n.y, n.x))

    # Kelompokkan node ke dalam baris berdasarkan jarak y
    rows = []
    current_row = [sorted_nodes[0]]
    for i in range(1, len(sorted_nodes)):
        if abs(sorted_nodes[i].y - current_row[0].y) < 600:
            current_row.append(sorted_nodes[i])
        else:
            rows.append(sorted(current_row, key=lambda n: n.x))
            current_row = [sorted_nodes[i]]
    rows.append(sorted(current_row, key=lambda n: n.x))

    # Hitung centroid dari setiap 4 node yang bertetangga (membentuk blok)
    centroids = []
    for r in range(len(rows) - 1):
        row_top = rows[r]
        row_bot = rows[r + 1]
        min_cols = min(len(row_top), len(row_bot))
        for c in range(min_cols - 1):
            # 4 sudut blok
            n_tl = row_top[c]
            n_tr = row_top[c + 1]
            n_bl = row_bot[c]
            n_br = row_bot[c + 1]
            # Centroid
            cx = (n_tl.x + n_tr.x + n_bl.x + n_br.x) / 4
            cy = (n_tl.y + n_tr.y + n_bl.y + n_br.y) / 4
            centroids.append({
                'x': cx, 'y': cy,
                'row': r, 'col': c,
                'width': abs(n_tr.x - n_tl.x + n_br.x - n_bl.x) / 2,
                'height': abs(n_bl.y - n_tl.y + n_br.y - n_tr.y) / 2
            })

    return centroids


def place_buildings(nodes, edges, roundabouts, edge_curves, island_outline=None):
    """
    Menempatkan bangunan pada titik tengah city-block (antara jalan),
    dengan pengecekan jarak ke jalan agar tidak overlap.
    
    Setiap cluster bangunan diberi alas kavling (tanah hijau/beton)
    agar bangunan terlihat berdiri di atas tanah, bukan mengambang.
    """
    buildings = []
    random.seed(42)  # Konsisten setiap kali dijalankan

    if not nodes or not edges:
        return buildings

    def add_building(tp, x, y, scale=2.2):
        """Tambahkan satu bangunan ke daftar."""
        radius = get_building_radius(tp)
        name = tp.replace('_', ' ').title()
        color = random.choice(C['apt'])
        buildings.append({
            'type': tp, 'x': float(x), 'y': float(y),
            'scale': scale, 'color': color,
            'name': name, 'radius': radius
        })

    def add_kavling(kavling_type, x, y):
        """Tambahkan alas tanah (kavling)."""
        add_building(kavling_type, x, y, scale=2.2)

    # --- FUNGSI SUSUN KOMPLEKS PERUMAHAN (2x2 grid isometrik) ---
    def buat_kompleks_rumah(rumah_type, cx, cy, jumlah=4):
        """Susun rumah dalam formasi 2x2 isometrik dengan kavling alas."""
        # cx, cy sudah dipastikan aman untuk radius kavling_sedang (380)
        add_kavling('kavling_sedang', cx, cy)

        sp_x = 264   # Jarak horizontal isometrik (rapat agar fit di kavling_sedang)
        sp_y = 132   # Jarak vertikal isometrik

        positions = []
        for r in range(2):
            for c in range(2):
                hx = cx + ((c - 0.5) - (r - 0.5)) * sp_x
                hy = cy + ((c - 0.5) + (r - 0.5)) * sp_y
                positions.append((hx, hy))

        for i in range(min(jumlah, len(positions))):
            px, py = positions[i]
            # Pastikan rumah tidak di atas jalan
            safe_x, safe_y = _find_safe_position(px, py, edges, edge_curves, 308, island_outline)
            add_building(rumah_type, safe_x, safe_y)

    # --- FUNGSI SUSUN CLUSTER CBD (3x3 grid isometrik) ---
    def buat_cluster_cbd(types_list, cx, cy):
        """Susun 9 gedung pencakar langit dalam formasi 3x3 dengan kavling beton."""
        # cx, cy sudah dipastikan aman untuk radius kavling_besar (520)
        add_kavling('kavling_besar', cx, cy)

        sp_x = 528   # Jarak isometrik antar gedung
        sp_y = 264

        all_slots = []
        for r in range(3):
            for c in range(3):
                bx = cx + ((c - 1) - (r - 1)) * sp_x
                by = cy + ((c - 1) + (r - 1)) * sp_y
                all_slots.append((bx, by))

        random.shuffle(types_list)

        for i in range(min(9, len(types_list))):
            bx, by = all_slots[i]
            # Menghapus jitter acak agar tertata rapi
            # Pastikan gedung tidak di atas jalan
            safe_x, safe_y = _find_safe_position(bx, by, edges, edge_curves, 484, island_outline)
            add_building(types_list[i], safe_x, safe_y)

    def buat_bangunan_tunggal(tp, cx, cy):
        """Tempatkan 1 bangunan tunggal dengan kavling alas yang sesuai di bawahnya."""
        r_b = get_building_radius(tp)
        tp_lower = tp.lower()
        
        # Tentukan tipe kavling berdasarkan ukuran bangunan dan arah diagonalnya
        if 'stadium' in tp_lower:
            kavling_type = 'kavling_besar_inv' # Memanjang dari kiri bawah ke kanan atas (X axis)
            kav_r = 520
        elif 'mall' in tp_lower:
            kavling_type = 'kavling_besar'
            kav_r = 520
        elif 'sakit' in tp_lower or 'sekolah' in tp_lower:
            kavling_type = 'kavling_sedang_inv' # Memanjang dari kiri bawah ke kanan atas (Y/Z axis)
            kav_r = 380
        elif 'town' in tp_lower or 'balai' in tp_lower:
            kavling_type = 'kavling_sedang'
            kav_r = 380
        else:
            kavling_type = 'kavling_kecil'
            kav_r = 180
            
        # Cari posisi aman dari jalan untuk kavling dan bangunan.
        # Jarak aman minimum didasarkan pada radius minimal default (396), radius bangunan (r_b), 
        # atau radius kavling dengan buffer tambahan (kav_r + 50) agar tidak menimpa jalan.
        safe_r = max(396, r_b, kav_r + 50)
        safe_x, safe_y = _find_safe_position(cx, cy, edges, edge_curves, safe_r, island_outline)
        add_kavling(kavling_type, safe_x, safe_y)
        add_building(tp, safe_x, safe_y)

    # ============================================================
    # HITUNG POSISI CITY-BLOCK DARI JARINGAN JALAN
    # ============================================================
    centroids = _compute_block_centroids(nodes)

    if len(centroids) >= 8:
        # Sortir centroid berdasarkan posisi: kiri-atas ke kanan-bawah
        centroids.sort(key=lambda c: (c['row'], c['col']))

        # Mapping zona — berdasarkan (row, col) dari centroid
        zone_map = {}
        for c in centroids:
            zone_map[(c['row'], c['col'])] = c

        # Inisialisasi daftar isi per blok
        block_contents = {
            (0, 0): [],
            (0, 1): [],
            (0, 2): [],
            (1, 0): [],
            (1, 1): [],
            (1, 2): [],
            (2, 0): [],
            (2, 1): [],
            (2, 2): []
        }

        # Tambahkan block dari centroid yang ada di luar 3x3
        for c in centroids:
            k = (c['row'], c['col'])
            if k not in block_contents:
                block_contents[k] = []

        # 1. Town Hall -> (0, 0)
        block_contents[(0, 0)].append(('town_hall', 'single'))
        
        # 2. Kompleks Perumahan -> (0, 1), (0, 2), (2, 0), (2, 2)
        block_contents[(0, 1)].append(('rumah1', 'complex'))
        block_contents[(0, 2)].append(('rumah2', 'complex'))
        block_contents[(2, 0)].append(('rumah3', 'complex'))
        block_contents[(2, 2)].append(('rumah4', 'complex'))
        
        # 3. CBD -> (1, 1), (1, 2)
        block_contents[(1, 1)].append(('cbd_1', 'cbd'))
        block_contents[(1, 2)].append(('cbd_2', 'cbd'))
        
        # 4. Bangunan Publik Lainnya
        col3_keys = [k for k in block_contents.keys() if k[1] >= 3]
        
        if (0, 3) in col3_keys:
            block_contents[(0, 3)].append(('sekolah', 'single'))
            block_contents[(0, 3)].append(('polisi', 'single'))
        else:
            block_contents[(0, 0)].append(('sekolah', 'single'))
            block_contents[(0, 0)].append(('polisi', 'single'))
            
        if (1, 3) in col3_keys:
            block_contents[(1, 3)].append(('stadium', 'single'))
        else:
            block_contents[(2, 1)].append(('stadium', 'single'))
            
        if (2, 3) in col3_keys:
            block_contents[(2, 3)].append(('bank', 'single'))
        else:
            block_contents[(1, 0)].append(('bank', 'single'))
            
        block_contents[(1, 0)].append(('rumah_sakit2', 'single'))
        block_contents[(1, 0)].append(('museum', 'single'))
        
        block_contents[(2, 1)].append(('mall', 'single'))
        block_contents[(2, 1)].append(('indomaret', 'single'))
        block_contents[(2, 1)].append(('spbu', 'single'))

        # Gambar per blok
        for k, items in block_contents.items():
            if k not in zone_map:
                continue
            b = zone_map[k]
            cx, cy = b['x'], b['y']
            
            center_item = None
            singles = []
            for it, style in items:
                if style in ['complex', 'cbd']:
                    center_item = (it, style)
                else:
                    singles.append(it)
                    
            if center_item:
                it, style = center_item
                if style == 'complex':
                    # Radius kompleks sedang = 836
                    scx, scy = _find_safe_position(cx, cy, edges, edge_curves, 836, island_outline)
                    buat_kompleks_rumah(it, scx, scy)
                    # Tempatkan bangunan tunggal di pinggiran kompleks
                    for s_idx, s_type in enumerate(singles):
                        angle = s_idx * (2 * math.pi / max(1, len(singles))) + (math.pi / 4)
                        dist = 550
                        sx = scx + math.cos(angle) * dist
                        sy = scy + math.sin(angle) * dist * 0.5
                        buat_bangunan_tunggal(s_type, sx, sy)
                elif style == 'cbd':
                    # Radius kompleks besar = 1144
                    scx, scy = _find_safe_position(cx, cy, edges, edge_curves, 1144, island_outline)
                    if it == 'cbd_1':
                        cbd_list = ['gedung', 'gedungA', 'gedungB', 'gedungC', 'gedungD', 'apartemen', 'gedungA', 'gedungB', 'gedungC']
                    else:
                        cbd_list = ['gedungC', 'apartemen', 'gedungD', 'gedung', 'gedungB', 'gedungA', 'apartemen', 'gedungC', 'gedungD']
                    buat_cluster_cbd(cbd_list, scx, scy)
                    # Tempatkan bangunan tunggal di pinggiran CBD
                    for s_idx, s_type in enumerate(singles):
                        angle = s_idx * (2 * math.pi / max(1, len(singles))) + (math.pi / 4)
                        dist = 650
                        sx = scx + math.cos(angle) * dist
                        sy = scy + math.sin(angle) * dist * 0.5
                        buat_bangunan_tunggal(s_type, sx, sy)
            else:
                # Hanya bangunan tunggal, susun rapi dalam block
                if len(singles) == 1:
                    buat_bangunan_tunggal(singles[0], cx, cy)
                elif len(singles) == 2:
                    buat_bangunan_tunggal(singles[0], cx - 250, cy - 125)
                    buat_bangunan_tunggal(singles[1], cx + 250, cy + 125)
                elif len(singles) >= 3:
                    for s_idx, s_type in enumerate(singles):
                        angle = s_idx * (2 * math.pi / len(singles))
                        dist = 300
                        sx = cx + math.cos(angle) * dist
                        sy = cy + math.sin(angle) * dist * 0.5
                        buat_bangunan_tunggal(s_type, sx, sy)

    else:
        # ============================================================
        # FALLBACK: Grid isometrik tetap (jika node terlalu sedikit)
        # ============================================================
        origin_x, origin_y = -400, -1200
        STEP_W, STEP_H = 1600, 800

        def grid_pos(col, row):
            return (origin_x + (col - row) * STEP_W // 2,
                    origin_y + (col + row) * STEP_H // 2)

        fallback_placements = [
            ('town_hall', grid_pos(0, 1), 'single'),
            ('cbd_1', grid_pos(1, 1), 'cbd'),
            ('cbd_2', grid_pos(2, 1), 'cbd'),
            ('rumah1', grid_pos(0, 2), 'complex'),
            ('rumah2', grid_pos(2, 0), 'complex'),
            ('rumah3', grid_pos(3, 2), 'complex'),
            ('rumah4', grid_pos(1, 3), 'complex'),
            ('sekolah', grid_pos(1, 0), 'single'),
            ('polisi', grid_pos(0, 0), 'single'),
            ('stadium', grid_pos(3, 0), 'single'),
            ('rumah_sakit2', grid_pos(2, 2), 'single'),
            ('mall', grid_pos(1, 2), 'single'),
            ('bank', grid_pos(3, 1), 'single'),
            ('museum', grid_pos(0, 3), 'single'),
            ('spbu', grid_pos(2, 3), 'single'),
            ('indomaret', grid_pos(3, 3), 'single'),
        ]

        for tp, (cx, cy), style in fallback_placements:
            if style == 'single':
                buat_bangunan_tunggal(tp, cx, cy)
            elif style == 'complex':
                scx, scy = _find_safe_position(cx, cy, edges, edge_curves, 836, island_outline)
                buat_kompleks_rumah(tp, scx, scy)
            elif style == 'cbd':
                scx, scy = _find_safe_position(cx, cy, edges, edge_curves, 1144, island_outline)
                if tp == 'cbd_1':
                    cbd_list = ['gedung', 'gedungA', 'gedungB', 'gedungC', 'gedungD', 'apartemen', 'gedungA', 'gedungB', 'gedungC']
                else:
                    cbd_list = ['gedungC', 'apartemen', 'gedungD', 'gedung', 'gedungB', 'gedungA', 'apartemen', 'gedungC', 'gedungD']
                buat_cluster_cbd(cbd_list, scx, scy)

    # ============================================================
    # ZONA 5: PELABUHAN & LAUT (selalu di tepi/luar pulau)
    # ============================================================
    if island_outline:
        east_pt = max(island_outline, key=lambda p: p[0])
        add_building('pelab', east_pt[0] - 300, east_pt[1])
        add_building('mersucuar', island_outline[0][0] + 100, island_outline[0][1] + 200)
    else:
        add_building('pelab', 3200, 200)
        add_building('mersucuar', -3200, -200)

    if island_outline:
        max_x = max(p[0] for p in island_outline)
        add_building('kapal_kargo', max_x + 800, -200)
        add_building('kapal_kargo2', max_x + 1200, 600)
        add_building('kapal_kargo', max_x + 700, 1400)
        add_building('kapal_kargo2', max_x + 1100, 2000)
    else:
        add_building('kapal_kargo', 4500, 600)
        add_building('kapal_kargo2', 4800, 1200)
        add_building('kapal_kargo', 4200, 1800)
        add_building('kapal_kargo2', 4600, 2400)

    # ============================================================
    # DEKORASI: Pohon & Lampu di pinggiran kota (jauh dari jalan)
    # ============================================================
    deko_positions = [
        ('pohon_belakang', -1800, -1600),
        ('pohon_bulat', 800, -1400),
        ('pohon_belakang', 1800, -800),
        ('pohon_bulat', -2600, 0),
        ('pohon_depan', -1800, 800),
        ('pohon_bulat', 300, 1600),
        ('pohon_belakang', 1600, 1200),
        ('pohon_bulat', -3000, -1000),
        ('pohon_depan', 2400, 0),
        ('pohon_belakang', -1200, 1800),
        ('pohon_bulat', 2000, 1600),
    ]
    for tp, dx, dy in deko_positions:
        if island_outline and not _point_in_polygon(dx, dy, island_outline):
            continue
        d = _min_dist_to_road_edges(dx, dy, edges, edge_curves)
        if d > RW * 1.5:
            add_building(tp, dx, dy)

    for n in nodes[:8]:
        lx = n.x + random.choice([-120, 120])
        ly = n.y + random.choice([-60, 60])
        d = _min_dist_to_road_edges(lx, ly, edges, edge_curves)
        if RW < d < RW * 3:
            add_building('lampu', lx, ly)

    # Sort berdasarkan depth (x + y) untuk urutan render isometrik yang benar
    buildings.sort(key=lambda b: b['x'] + b['y'])
    return buildings
