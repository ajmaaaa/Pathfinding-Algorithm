import math
import time
from src.algorithm.heuristic import euclidean_distance
from src.algorithm.min_heap import MinHeap
from src.core.geometry import cubic_bezier, make_curved_edge_points, polyline_length

def run_astar_anim(start, end, nodes, edge_curves=None, roundabout_radius=140.25):
    t0 = time.perf_counter()
    for n in nodes: n.eval_step = float('inf'); n.disc_step = float('inf')

    open_heap = MinHeap()
    open_set_tracker = set([start])
    
    g = {n: float('inf') for n in nodes}
    f = {n: float('inf') for n in nodes}
    came_from = {}
    came_from_edge = {}
    
    g[start] = 0
    f[start] = euclidean_distance(start, end)
    start.disc_step = 0.0
    open_heap.put(start, f[start])

    search_edges_anim = []
    final_path_anim = []
    found = False

    SEARCH_SPEED_FACTOR = 200.0  # Kecepatan rambat gelombang pencarian (piksel per step)

    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
            
        open_set_tracker.remove(cur)
        cur.eval_step = cur.disc_step

        if cur is end: 
            found = True; break

        for e in cur.edges:
            nb = e[1] if e[0] is cur else e[0]
            curve = _edge_curve(e, cur, edge_curves)
            edge_dist = polyline_length(curve)
            tg = g[cur] + edge_dist
            optimal = tg < g[nb]

            if optimal:
                # Buat kurva pencarian (search path) melengkung untuk bundaran
                search_curve = list(curve)
                r_start = 140.25 if cur.is_roundabout else 0.0
                r_end = 140.25 if nb.is_roundabout else 0.0
                search_curve = _clip_straight_line(curve, r_start, r_end)
                
                if cur.is_roundabout:
                    parent = came_from.get(cur)
                    e_in = came_from_edge.get(cur)
                    if parent is not None and e_in is not None:
                        incoming_raw = _edge_curve(e_in, parent, edge_curves)
                        r_in_start = 140.25 if parent.is_roundabout else 0.0
                        incoming_curve = _clip_straight_line(incoming_raw, r_in_start, 140.25)
                        turn_curve = _roundabout_turn_curve(cur, incoming_curve[-2:], search_curve[:2], roundabout_radius)
                        search_curve = turn_curve + search_curve[1:]

                dur = edge_dist / SEARCH_SPEED_FACTOR
                search_edges_anim.append({
                    'from': cur, 'to': nb, 'target': nb, 
                    'start': cur.disc_step, 'end': cur.disc_step + dur, 'is_optimal': True,
                    'curve': search_curve
                })

                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                f[nb] = tg + euclidean_distance(nb, end)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                if nb.disc_step == float('inf') or (cur.disc_step + dur) < nb.disc_step: 
                    nb.disc_step = cur.disc_step + dur

    ms = (time.perf_counter()-t0)*1000

    max_search_step = max([se['end'] for se in search_edges_anim] + [0.0])

    if not found: return search_edges_anim, [], 0.0, ms, max_search_step

    path = []; path_edges = []; cur_node = end
    while cur_node:
        path.insert(0, cur_node)
        if cur_node in came_from_edge:
            path_edges.insert(0, came_from_edge[cur_node])
        cur_node = came_from.get(cur_node)

    dist = 0.0; p_step = max_search_step + 1
    CAR_SPEED_FACTOR = 24.0  
    TURN_SPEED_FACTOR = 20.0
    ROUNDABOUT_SPEED_FACTOR = 18.0
    for i in range(1, len(path)):
        curve = _prepare_drive_curve(path, path_edges[i - 1], i, edge_curves, roundabout_radius, roundabout_radius)
        edge_dist = polyline_length(curve)
        dist += edge_dist
        time_cost = max(0.05, edge_dist / CAR_SPEED_FACTOR) 
        
        final_path_anim.append({'from': path[i-1], 'to': path[i], 'start': p_step, 'end': p_step + time_cost, 'curve': curve})
        p_step += time_cost

        if i < len(path) - 1:
            if path[i].is_roundabout:
                next_curve = _prepare_drive_curve(
                    path,
                    path_edges[i],
                    i + 1,
                    edge_curves,
                    roundabout_radius,
                    roundabout_radius
                )
                turn_curve = _roundabout_turn_curve(path[i], curve[-2:], next_curve[:2], roundabout_radius)
                turn_dist = polyline_length(turn_curve)
                dist += turn_dist
                turn_cost = max(0.05, turn_dist / ROUNDABOUT_SPEED_FACTOR)
            else:
                next_curve = _prepare_drive_curve(path, path_edges[i], i + 1, edge_curves, roundabout_radius, roundabout_radius)
                
                p0 = curve[-1]
                p3 = next_curve[0]
                
                dx1 = curve[-1][0] - curve[-2][0]
                dy1 = curve[-1][1] - curve[-2][1]
                len1 = max(0.0001, math.hypot(dx1, dy1))
                t1x, t1y = dx1/len1, dy1/len1
                
                dx2 = next_curve[1][0] - next_curve[0][0]
                dy2 = next_curve[1][1] - next_curve[0][1]
                len2 = max(0.0001, math.hypot(dx2, dy2))
                t2x, t2y = dx2/len2, dy2/len2
                
                dist_pts = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
                
                dist_to_int1 = math.hypot(path[i].x - p0[0], path[i].y - p0[1])
                dist_to_int2 = math.hypot(path[i].x - p3[0], path[i].y - p3[1])
                
                handle1 = min(dist_pts * 0.45, dist_to_int1 * 0.5)
                handle2 = min(dist_pts * 0.45, dist_to_int2 * 0.5)
                
                p1 = (p0[0] + t1x * handle1, p0[1] + t1y * handle1)
                p2 = (p3[0] - t2x * handle2, p3[1] - t2y * handle2)
                
                turn_curve = _sample_bezier(p0, p1, p2, p3, steps=24)
                turn_dist = polyline_length(turn_curve)
                dist += turn_dist
                turn_cost = max(0.05, turn_dist / TURN_SPEED_FACTOR)
                
            final_path_anim.append({'from': path[i], 'to': path[i], 'start': p_step, 'end': p_step + turn_cost, 'curve': turn_curve})
            p_step += turn_cost

    total_steps = p_step + 2
    return search_edges_anim, final_path_anim, dist, ms, total_steps
