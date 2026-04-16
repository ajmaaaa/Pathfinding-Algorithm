import math
import time
from src.algorithm.heuristic import euclidean_distance
from src.algorithm.min_heap import MinHeap

def run_astar_anim(start, end, nodes):
    t0 = time.perf_counter()
    for n in nodes: n.eval_step = float('inf'); n.disc_step = float('inf')

    open_heap = MinHeap()
    open_set_tracker = set([start])
    
    g = {n: float('inf') for n in nodes}
    f = {n: float('inf') for n in nodes}
    came_from = {}
    
    g[start] = 0
    f[start] = euclidean_distance(start, end)
    start.disc_step = 0
    open_heap.put(start, f[start])

    search_edges_anim = []
    final_path_anim = []
    step = 0; found = False

    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
            
        open_set_tracker.remove(cur)
        cur.eval_step = step

        if cur is end: 
            found = True; break

        advanced = False
        for e in cur.edges:
            nb = e[1] if e[0] is cur else e[0]
            tg = g[cur] + math.hypot(cur.x-nb.x, cur.y-nb.y)
            optimal = tg < g[nb]

            if optimal or nb.eval_step == float('inf'):
                search_edges_anim.append({
                    'from': cur, 'to': nb, 'target': nb, 
                    'start': step, 'end': step + 1, 'is_optimal': optimal
                })
                advanced = True

            if optimal:
                came_from[nb] = cur
                g[nb] = tg
                f[nb] = tg + euclidean_distance(nb, end)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                if nb.disc_step == float('inf'): 
                    nb.disc_step = step + 1

        if advanced: step += 1
        else: step += 0.5

    ms = (time.perf_counter()-t0)*1000

    if not found: return search_edges_anim, [], 0.0, ms, step

    max_search_step = step; path = []; cur_node = end
    while cur_node:
        path.insert(0, cur_node)
        cur_node = came_from.get(cur_node)

    dist = 0.0; p_step = max_search_step + 1
    CAR_SPEED_FACTOR = 25.0  
    
    for i in range(1, len(path)):
        edge_dist = math.hypot(path[i].x-path[i-1].x, path[i].y-path[i-1].y)
        dist += edge_dist
        time_cost = max(0.5, edge_dist / CAR_SPEED_FACTOR) 
        
        final_path_anim.append({'from': path[i-1], 'to': path[i], 'start': p_step, 'end': p_step + time_cost})
        p_step += time_cost

    total_steps = p_step + 2
    return search_edges_anim, final_path_anim, dist, ms, total_steps