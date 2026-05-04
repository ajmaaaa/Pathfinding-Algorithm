import random
import math
from config import RW, LP, NAME_T1, NAME_T2, NAME_T3, NAME_TREE, C

def place_buildings(nodes, edges, roundabouts):
    buildings = []
    if not nodes:
        return buildings

    min_x = min(n.x for n in nodes) - 1500; max_x = max(n.x for n in nodes) + 1500
    min_y = min(n.y for n in nodes) - 1500; max_y = max(n.y for n in nodes) + 1500

    CS = 500; e_grid = {}
    for e in edges:
        x0 = int((min(e[0].x,e[1].x)-150)//CS); x1 = int((max(e[0].x,e[1].x)+150)//CS)
        y0 = int((min(e[0].y,e[1].y)-150)//CS); y1 = int((max(e[0].y,e[1].y)+150)//CS)
        for bx in range(x0, x1+1):
            for by in range(y0, y1+1):
                k = (bx, by)
                if k not in e_grid: e_grid[k] = []
                e_grid[k].append(e)

    # PERBAIKAN: Scannya diperbesar agar jarak antar titik cek lebih jauh (Bangunan lebih sedikit)
    sc = 115
    sRS = (RW*1.1 + 25)**2 # Jarak aman dengan aspal diperlebar sedikit
    mBS = (LP/2 - 200)**2
    absMaxSq = (LP/2 - 50)**2
    b_grid = {}
    
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            bx, by = float(x), float(y)
            sx = int(bx//CS); sy = int(by//CS)
            nearby = set()
            for cx in range(sx-1, sx+2):
                for cy in range(sy-1, sy+2):
                    k = (cx, cy)
                    if k in e_grid:
                        for e in e_grid[k]: nearby.add(id(e))
            if not nearby: y += sc; continue

            nearby_edges = [e for e in edges if id(e) in nearby]
            cRd = float('inf'); safe = True; angs = []
            
            # --- Mengecek Tabrakan dengan Jalan Melengkung ---
            for e in nearby_edges:
                pts = [{'x': e[0].x, 'y': e[0].y}]
                if len(e) > 2:
                    pts.extend(e[2]) # Membaca data lengkungan jalan jika ada
                pts.append({'x': e[1].x, 'y': e[1].y})
                
                for i in range(len(pts)-1):
                    p1x, p1y = pts[i]['x'], pts[i]['y']
                    p2x, p2y = pts[i+1]['x'], pts[i+1]['y']
                    
                    l2 = (p1x-p2x)**2 + (p1y-p2y)**2
                    if l2 > 0:
                        t = max(0, min(1, ((bx-p1x)*(p2x-p1x) + (by-p1y)*(p2y-p1y))/l2))
                        cpx = p1x + t*(p2x-p1x)
                        cpy = p1y + t*(p2y-p1y)
                    else:
                        cpx, cpy = p1x, p1y
                        
                    dSq = (bx-cpx)**2 + (by-cpy)**2
                    if dSq < sRS: 
                        safe = False; break
                    if dSq < cRd: 
                        cRd = dSq
                    if dSq < 640000: 
                        angs.append(math.atan2(cpy-by, cpx-bx))
                if not safe: break

            if not safe or cRd > absMaxSq: y += sc; continue

            for rb in roundabouts:
                if (rb.x-bx)**2 + (rb.y-by)**2 < (RW*3.5)**2: safe = False; break
            if not safe: y += sc; continue

            out = True
            if angs:
                angs.sort(); mg = angs[0] + math.pi*2 - angs[-1]
                for i in range(len(angs)-1):
                    g = angs[i+1]-angs[i]
                    if g > mg: mg = g
                if mg < math.pi*1.4: out = False

            if out and cRd > mBS: y += sc; continue

            df = math.sqrt(cRd) - RW/2
            
            # PERBAIKAN: Peluang spawn diturunkan agar jauh lebih santai (tidak padat)
            sp = (0.35 if df < 100 else 0.1) if out else 1.0
            if random.random() > sp: y += sc; continue

            # PERBAIKAN: JARAK ANTAR BANGUNAN DIJAUHKAN (95px)
            bk = (int(bx//300), int(by//300)); bs = True
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    ck = (int(bx//300)+di, int(by//300)+dj)
                    if ck in b_grid:
                        for b in b_grid[ck]:
                            # Syarat jarak dikembalikan ke 95px agar bangunan tidak menempel
                            if math.hypot(b['x'] - bx, b['y'] - by) < 95: bs = False; break
                if not bs: break
            if not bs: y += sc; continue

            r = random.random()
            if out: tp = 't1' if r < .15 else ('t2' if r < .25 else 'tree')
            else: tp = 't1' if r < .1 else ('t2' if r < .5 else 't3') if df > 150 else ('t1' if r < .15 else ('t2' if r < .6 else ('t3' if r < .95 else 'tree')))

            b_name = random.choice(NAME_T1) if tp == 't1' else random.choice(NAME_T2) if tp == 't2' else random.choice(NAME_T3) if tp == 't3' else random.choice(NAME_TREE)

            # SKALA KEMBALI NORMAL
            rand_scale = random.choice([0.65, 0.7, 0.75])
            bd = {'type': tp, 'x': bx, 'y': by, 'scale': rand_scale, 'color': random.choice(C['apt']), 'name': b_name}
            
            buildings.append(bd)
            if bk not in b_grid: b_grid[bk] = []
            b_grid[bk].append(bd)
            y += sc
        x += sc

    buildings.sort(key=lambda b: b['y'])
    return buildings
