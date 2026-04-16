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
                if (n.x-nx)**2 + (n.y-ny)**2 < 280**2: safe = False; break
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
                if diff < math.pi/4:
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

        for _ in range(3): 
            current_edges = list(edges)
            for e in current_edges:
                n1, n2 = e[0], e[1]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist > 80: 
                    edges.remove(e); n1.edges.remove(e); n2.edges.remove(e)
                    mid_x = (n1.x + n2.x) / 2; mid_y = (n1.y + n2.y) / 2
                    angle = math.atan2(n2.y - n1.y, n2.x - n1.x)
                    offset = (random.random() - 0.5) * dist * 0.2
                    mid_x += math.cos(angle + math.pi/2) * offset; mid_y += math.sin(angle + math.pi/2) * offset
                    mid_node = Node(mid_x, mid_y); nodes.append(mid_node)
                    e1 = [n1, mid_node]; e2 = [mid_node, n2]
                    edges.extend([e1, e2])
                    n1.edges.append(e1); mid_node.edges.extend([e1, e2]); n2.edges.append(e2)

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
                n.x = n.x*0.3 + nxs[i]*0.7; n.y = n.y*0.3 + nys[i]*0.7

        hidden_edges = set(); final_nodes = []
        for n in nodes:
            if len(n.edges) >= 4 and random.random() > 0.8:
                roundabouts.append(n); n.is_roundabout = True; ring = []; R = RW * 1.2 
                for i in range(8):
                    a = i * (math.pi * 2 / 8)
                    rn = Node(n.x + math.cos(a)*R, n.y + math.sin(a)*R)
                    ring.append(rn); final_nodes.append(rn)
                for i in range(8):
                    e = [ring[i], ring[(i+1)%8]]; edges.append(e); hidden_edges.add(id(e)) 
                    ring[i].edges.append(e); ring[(i+1)%8].edges.append(e)
                for e in list(n.edges):
                    other = e[1] if e[0] is n else e[0]
                    best_rn = min(ring, key=lambda rn: math.hypot(rn.x-other.x, rn.y-other.y))
                    if e[0] is n: e[0] = best_rn
                    else: e[1] = best_rn
                    best_rn.edges.append(e)
                n.edges = []
            else: final_nodes.append(n)
        nodes = final_nodes
        
        buildings = place_buildings(nodes, edges, roundabouts)

        return {'nodes': nodes, 'edges': edges, 'roundabouts': roundabouts, 'buildings': buildings, 'hidden_edges': hidden_edges}