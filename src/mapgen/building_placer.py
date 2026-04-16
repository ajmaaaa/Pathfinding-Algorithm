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

    sc = 115; sRS = (RW*1.1 + 35)**2; mBS = (LP/2 - 200)**2; absMaxSq = (LP/2 - 50)**2; b_grid = {}
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
            for e in nearby_edges:
                l2 = (e[0].x-e[1].x)**2+(e[0].y-e[1].y)**2
                cp = {'x': e[0].x, 'y': e[0].y}
                if l2 > 0:
                    t = max(0, min(1, ((bx-e[0].x)*(e[1].x-e[0].x)+(by-e[0].y)*(e[1].y-e[0].y))/l2))
                    cp = {'x': e[0].x+t*(e[1].x-e[0].x), 'y': e[0].y+t*(e[1].y-e[0].y)}
                dSq = (bx-cp['x'])**2+(by-cp['y'])**2
                if dSq < sRS: safe = False; break
                if dSq < cRd: cRd = dSq
                if dSq < 640000: angs.append(math.atan2(cp['y']-by, cp['x']-bx))

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
            sp = (0.30 if df < 100 else 0.01) if out else 1.0
            if random.random() > sp: y += sc; continue

            bk = (int(bx//300), int(by//300)); bs = True
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    ck = (int(bx//300)+di, int(by//300)+dj)
                    if ck in b_grid:
                        for b in b_grid[ck]:
                            if math.hypot(b['x'] - bx, b['y'] - by) < 105: bs = False; break
                if not bs: break
            if not bs: y += sc; continue

            r = random.random()
            if out: tp = 't1' if r < .15 else ('t2' if r < .25 else 'tree')
            else: tp = 't1' if r < .1 else ('t2' if r < .5 else 't3') if df > 150 else ('t1' if r < .15 else ('t2' if r < .6 else ('t3' if r < .95 else 'tree')))

            b_name = random.choice(NAME_T1) if tp == 't1' else random.choice(NAME_T2) if tp == 't2' else random.choice(NAME_T3) if tp == 't3' else random.choice(NAME_TREE)

            bd = {'type': tp, 'x': bx, 'y': by, 'scale': 0.7, 'color': random.choice(C['apt']), 'name': b_name}
            buildings.append(bd)
            if bk not in b_grid: b_grid[bk] = []
            b_grid[bk].append(bd)
            y += sc
        x += sc

    buildings.sort(key=lambda b: b['y'])
    return buildings