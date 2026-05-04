import random
import math
from src.core.graph import Node
from config import RW
from src.mapgen.building_placer import place_buildings

class MapGen:
    def generate(self):
        nodes, edges, roundabouts = [], [], []
        centers = [{'x': 0, 'y': 0}]
        
        for _ in range(10):
            p = random.choice(centers)
            a = random.random() * math.pi * 2; d = 400 + random.random() * 500
            centers.append({'x': p['x'] + math.cos(a)*d, 'y': p['y'] + math.sin(a)*d})
            
        for _ in range(350):
            c = random.choice(centers)
            r = random.random() * 700; a = random.random() * math.pi * 2
            nx = c['x'] + r*math.cos(a); ny = c['y'] + r*math.sin(a)
            safe = True
            for n in nodes:
                # Jarak 350px agar blok jalan punya ruang cukup
                if (n.x-nx)**2 + (n.y-ny)**2 < 350**2: safe = False; break
            if safe: nodes.append(Node(nx, ny))
            
        nCS = 400; nGrid = {}
        for n in nodes:
            k = f"{int(n.x//nCS)}_{int(n.y//nCS)}"
            if k not in nGrid: nGrid[k] = []
            nGrid[k].append(n)
            
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                ds = (n1.x-n2.x)**2 + (n1.y-n2.y)**2
                if ds > 1000**2: continue 
                cx = (n1.x+n2.x)/2; cy = (n1.y+n2.y)/2
                rs = ds/4; ok = True; rad = math.sqrt(rs)
                gx0 = int((cx-rad)//nCS); gx1 = int((cx+rad)//nCS)
                gy0 = int((cy-rad)//nCS); gy1 = int((cy+rad)//nCS)
                for gx in range(gx0, gx1+1):
                    for gy in range(gy0, gy1+1):
                        k = f"{gx}_{gy}"
                        if k in nGrid:
                            for nk in nGrid[k]:
                                if nk is n1 or nk is n2: continue
                                if (nk.x-cx)**2 + (nk.y-cy)**2 < rs-1: ok = False; break
                        if not ok: break
                    if not ok: break
                if ok:
                    e = [n1, n2]; edges.append(e); n1.edges.append(e); n2.edges.append(e)

        rem = set()
        for e1 in edges:
            n1, n2 = e1[0], e1[1]
            for e2 in n1.edges:
                if e2 is e1: continue
                n3 = e2[1] if e2[0] is n1 else e2[0]
                e3 = None
                for e in n2.edges:
                    if e[0] is n3 or e[1] is n3: e3 = e; break
                if e3:
                    l1 = (n1.x-n2.x)**2+(n1.y-n2.y)**2; l2 = (n1.x-n3.x)**2+(n1.y-n3.y)**2; l3 = (n2.x-n3.x)**2+(n2.y-n3.y)**2
                    mx = max(l1, l2, l3)
                    rem.add(id(e1 if mx==l1 else (e2 if mx==l2 else e3)))
        rem_edges = [e for e in edges if id(e) in rem]
        for e in rem_edges:
            if e in edges: edges.remove(e)
            a, b = e[0], e[1]
            if e in a.edges: a.edges.remove(e)
            if e in b.edges: b.edges.remove(e)

        # Pemangkasan Sudut (Angle Pruning)
        for n in nodes:
            if len(n.edges) < 2: continue
            n.edges.sort(key=lambda e: math.atan2((e[1] if e[0] is n else e[0]).y - n.y, (e[1] if e[0] is n else e[0]).x - n.x))
            tr = []
            ne = n.edges
            for j in range(len(ne)):
                e1 = ne[j]; e2 = ne[(j+1) % len(ne)]
                n1 = e1[1] if e1[0] is n else e1[0]; n2 = e2[1] if e2[0] is n else e2[0]
                a1 = math.atan2(n1.y-n.y, n1.x-n.x); a2 = math.atan2(n2.y-n.y, n2.x-n.x)
                diff = abs(a1-a2)
                if diff > math.pi: diff = math.pi*2 - diff
                
                # Sudut 60 derajat (pi/3)
                if diff < math.pi/3: 
                    l1 = (n1.x-n.x)**2+(n1.y-n.y)**2; l2 = (n2.x-n.x)**2+(n2.y-n.y)**2
                    tr.append(e1 if l1 > l2 else e2)
            for e in tr:
                if e in edges: edges.remove(e)
                nb = e[1] if e[0] is n else e[0]
                if e in nb.edges: nb.edges.remove(e)
                if e in n.edges:  n.edges.remove(e)

        trimming = True
        while trimming:
            trimming = False
            for i in range(len(nodes)-1, -1, -1):
                n = nodes[i]
                if len(n.edges) <= 1:
                    for e in list(n.edges):
                        if e in edges: edges.remove(e)
                        nb = e[1] if e[0] is n else e[0]
                        if e in nb.edges: nb.edges.remove(e)
                    nodes.pop(i); trimming = True

        # Relaxation diperkecil (0.15)
        for _ in range(8):
            nxs = []; nys = []
            for n in nodes:
                if not n.edges:
                    nxs.append(n.x); nys.append(n.y); continue
                ax = ay = 0
                for e in n.edges:
                    nb = e[1] if e[0] is n else e[0]
                    ax += nb.x; ay += nb.y
                cnt = len(n.edges)
                nxs.append(ax/cnt); nys.append(ay/cnt)
            for i, n in enumerate(nodes):
                n.x = n.x*0.85 + nxs[i]*0.15; n.y = n.y*0.85 + nys[i]*0.15

        hidden_edges = set(); final_nodes = []
        for n in nodes:
            if len(n.edges) >= 4 and random.random() > 0.8:
                roundabouts.append(n); n.is_roundabout = True; ring = []; R = RW * 1.2 
                for i in range(4):
                    a = i * (math.pi * 2 / 4) + (math.pi/4) 
                    rn = Node(n.x + math.cos(a)*R, n.y + math.sin(a)*R)
                    ring.append(rn); final_nodes.append(rn)
                    
                for i in range(4):
                    e = [ring[i], ring[(i+1)%4]]
                    a1 = i * (math.pi * 2 / 4) + (math.pi/4)
                    a2 = (i+1) * (math.pi * 2 / 4) + (math.pi/4)
                    visual_points = []
                    for j in range(1, 20):
                        t = j / 20.0
                        ang = a1 + (a2 - a1) * t
                        visual_points.append({'x': n.x + math.cos(ang)*R, 'y': n.y + math.sin(ang)*R})
                        
                    e.append(visual_points) 
                    edges.append(e); hidden_edges.add(id(e)) 
                    ring[i].edges.append(e); ring[(i+1)%4].edges.append(e)
                    
                for e in list(n.edges):
                    other = e[1] if e[0] is n else e[0]
                    best_rn = min(ring, key=lambda rn: math.hypot(rn.x-other.x, rn.y-other.y))
                    if e[0] is n: e[0] = best_rn
                    else: e[1] = best_rn
                    best_rn.edges.append(e)
                n.edges = []
            else: final_nodes.append(n)
        nodes = final_nodes
        
        # ------------------------------------------------------------------
        # PERBAIKAN: GENERASI LENGKUNGAN ANTI-LANCIP / ANTI-KUSUT (NO CUSPS)
        # ------------------------------------------------------------------
        for e in edges:
            if len(e) > 2: continue 
            
            n1, n2 = e[0], e[1]
            dx = n2.x - n1.x
            dy = n2.y - n1.y
            dist = math.hypot(dx, dy)
            
            if dist > 80: 
                perp_x = -dy / dist
                perp_y = dx / dist
                
                seed = int(n1.x + n2.y + n1.y)
                rnd = random.Random(seed)
                direction = 1 if seed % 2 == 0 else -1
                
                # --- MATEMATIKA ANTI-LANCIP (SAFE MAGNITUDE BOUNDARY) ---
                # Mengunci magnitudo (amplitudo lengkungan) maksimal agar 
                # kemiringan/turunan gelombang tidak pernah melebihi pergerakan 
                # majunya (dist / 2*pi).
                max_safe_mag = dist * 0.12  # Sangat aman dari risiko melipat
                magnitude = max_safe_mag * rnd.uniform(0.4, 1.0) * direction
                
                is_s_curve = rnd.random() > 0.4
                
                visual_points = []
                steps = max(35, int(dist / 4))
                
                for j in range(1, steps):
                    t = j / float(steps)
                    if is_s_curve:
                        # Full Wave (S-Curve): Gunakan 80% dari batas aman agar tidak terlalu tajam di tengah
                        offset = math.sin(t * math.pi * 2.0) * (magnitude * 0.8)
                    else:
                        # Half Wave (C-Curve): Memakai sin^2 agar kurva menyatu SEMPURNA  
                        # dan lurus dengan node di ujung jalan, mencegah patahan bersudut
                        offset = (math.sin(t * math.pi)**2) * magnitude
                        
                    bx = n1.x + dx * t + perp_x * offset
                    by = n1.y + dy * t + perp_y * offset
                    visual_points.append({'x': bx, 'y': by})
                    
                e.append(visual_points) 
        
        buildings = place_buildings(nodes, edges, roundabouts)

        return {'nodes': nodes, 'edges': edges, 'roundabouts': roundabouts, 'buildings': buildings, 'hidden_edges': hidden_edges}
