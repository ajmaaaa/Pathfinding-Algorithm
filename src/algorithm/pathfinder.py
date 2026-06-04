import math
import time
from src.algorithm.heuristic import euclidean_distance
from src.algorithm.min_heap import MinHeap
from src.core.geometry import cubic_bezier, make_curved_edge_points, polyline_length

def _edge_curve(edge, from_node, edge_curves):
    curve = edge_curves.get(id(edge)) if edge_curves else None
    if not curve:
        # Jalan di peta ini adalah garis lurus (bend=0.0), jadi gunakan
        # garis lurus agar mobil tidak keluar dari aspal
        to_node = edge[1] if edge[0] is from_node else edge[0]
        return [(from_node.x, from_node.y), (to_node.x, to_node.y)]
    if edge[0] is from_node:
        return curve[:]
    return list(reversed(curve))

def _clip_straight_line(curve, r_start, r_end):
    if len(curve) < 2:
        return curve
    p0, p1 = curve[0], curve[-1]
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L <= 0.0001:
        return curve

    if L > r_start + r_end:
        t_start = r_start / L
        t_end = 1.0 - (r_end / L)
    else:
        if r_start + r_end > 0:
            split_t = r_start / (r_start + r_end)
        else:
            split_t = 0.5
        t_start = max(0.0, split_t - 0.01)
        t_end = min(1.0, split_t + 0.01)

    pt_start = (p0[0] + dx * t_start, p0[1] + dy * t_start)
    pt_end = (p0[0] + dx * t_end, p0[1] + dy * t_end)
    return [pt_start, pt_end]

def _unit(dx, dy):
    length = math.hypot(dx, dy)
    if length <= 0.0001:
        return 1.0, 0.0
    return dx / length, dy / length

def _sample_bezier(p0, c1, c2, p3, steps=24):
    return [cubic_bezier(p0, c1, c2, p3, i / float(steps)) for i in range(steps + 1)]

def _arc_points(rb_node, start_ang, end_ang, radius, steps=24):
    cx, cy = rb_node.x, rb_node.y
    delta = (end_ang - start_ang + math.pi * 3) % (math.pi * 2) - math.pi
    if abs(delta) < 0.28:
        delta = 0.28 if delta >= 0 else -0.28

    pts = []
    for i in range(steps + 1):
        a = start_ang + delta * (i / steps)
        # Squish sumbu y sebesar 0.5 agar berbentuk elips isometrik
        pts.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius * 0.5))
    return pts

def _arc_around_roundabout(rb_node, start_pt, end_pt, radius, steps=24):
    cx, cy = rb_node.x, rb_node.y
    # Gunakan sudut eccentric anomaly agar elips isometrik terhubung sempurna ke jalan diagonal
    a1 = math.atan2((start_pt[1] - cy) / 0.5, start_pt[0] - cx)
    a2 = math.atan2((end_pt[1] - cy) / 0.5, end_pt[0] - cx)
    return _arc_points(rb_node, a1, a2, radius, steps)

def _roundabout_turn_curve(rb_node, incoming, outgoing, radius):
    return _arc_around_roundabout(rb_node, incoming[-1], outgoing[0], radius)

def _prepare_drive_curve(path, edge, i, edge_curves, roundabout_radius, blend_radius=None):
    curve = _edge_curve(edge, path[i - 1], edge_curves)
    r_start = 0.0
    # Gunakan radius pemotongan presisi 140.25 untuk persimpangan elips bundaran isometrik
    if path[i - 1].is_roundabout:
        r_start = 140.25
    elif i > 1:
        r_start = 60.0

    r_end = 0.0
    if path[i].is_roundabout:
        r_end = 140.25
    elif i < len(path) - 1:
        r_end = 60.0

    return _clip_straight_line(curve, r_start, r_end)

def forward_search(open_heap, open_set_tracker, visited_self, visited_other, open_set_tracker_other, came_from, came_from_edge, g, f, goal, edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, roundabout_radius=140.25):
    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
        open_set_tracker.remove(cur)
        cur.eval_step = cur.disc_step
        visited_self.add(cur)
        
        if cur in visited_other or cur in open_set_tracker_other:
            return cur
            
        for e in cur.edges:
            nb = e[1] if e[0] is cur else e[0]
            if nb in visited_self:
                continue
            curve = _edge_curve(e, cur, edge_curves)
            edge_dist = polyline_length(curve)
            tg = g[cur] + edge_dist
            
            # Check if this neighbor has already been reached by the other search
            if nb in visited_other or nb in open_set_tracker_other:
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                
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
                if nb.disc_step == float('inf') or (cur.disc_step + dur) < nb.disc_step: 
                    nb.disc_step = cur.disc_step + dur
                return nb
            
            if tg < g[nb]:
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
                f[nb] = tg + euclidean_distance(nb, goal)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                if nb.disc_step == float('inf') or (cur.disc_step + dur) < nb.disc_step: 
                    nb.disc_step = cur.disc_step + dur
        return None
    return None

def backward_search(open_heap, open_set_tracker, visited_self, visited_other, open_set_tracker_other, came_from, came_from_edge, g, f, goal, edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, roundabout_radius=140.25):
    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
        open_set_tracker.remove(cur)
        cur.eval_step = cur.disc_step
        visited_self.add(cur)
        
        if cur in visited_other or cur in open_set_tracker_other:
            return cur
            
        for e in cur.edges:
            nb = e[1] if e[0] is cur else e[0]
            if nb in visited_self:
                continue
            curve = _edge_curve(e, cur, edge_curves)
            edge_dist = polyline_length(curve)
            tg = g[cur] + edge_dist
            
            # Check if this neighbor has already been reached by the other search
            if nb in visited_other or nb in open_set_tracker_other:
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                
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
                if nb.disc_step == float('inf') or (cur.disc_step + dur) < nb.disc_step: 
                    nb.disc_step = cur.disc_step + dur
                return nb
            
            if tg < g[nb]:
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
                f[nb] = tg + euclidean_distance(nb, goal)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                if nb.disc_step == float('inf') or (cur.disc_step + dur) < nb.disc_step: 
                    nb.disc_step = cur.disc_step + dur
        return None
    return None

def run_astar_anim(start, end, nodes, edge_curves=None, roundabout_radius=140.25):
    t0 = time.perf_counter()
    for n in nodes: n.eval_step = float('inf'); n.disc_step = float('inf')

    open_heap_f = MinHeap()
    open_set_tracker_f = set([start])
    visited_f = set()
    g_f = {n: float('inf') for n in nodes}
    f_f = {n: float('inf') for n in nodes}
    came_from_f = {}
    came_from_edge_f = {}
    
    g_f[start] = 0
    f_f[start] = euclidean_distance(start, end)
    start.disc_step = 0.0
    open_heap_f.put(start, f_f[start])

    open_heap_b = MinHeap()
    open_set_tracker_b = set([end])
    visited_b = set()
    g_b = {n: float('inf') for n in nodes}
    f_b = {n: float('inf') for n in nodes}
    came_from_b = {}
    came_from_edge_b = {}
    
    g_b[end] = 0
    f_b[end] = euclidean_distance(end, start)
    end.disc_step = 0.0
    open_heap_b.put(end, f_b[end])

    search_edges_anim = []
    final_path_anim = []
    found = False
    meeting_node = None

    SEARCH_SPEED_FACTOR = 200.0  # Kecepatan rambat gelombang pencarian (piksel per step)

    while not open_heap_f.empty() and not open_heap_b.empty():
        meeting_node = forward_search(
            open_heap_f, open_set_tracker_f, visited_f, visited_b, open_set_tracker_b,
            came_from_f, came_from_edge_f, g_f, f_f, end,
            edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, roundabout_radius
        )
        if meeting_node is not None:
            found = True
            break

        meeting_node = backward_search(
            open_heap_b, open_set_tracker_b, visited_b, visited_f, open_set_tracker_f,
            came_from_b, came_from_edge_b, g_b, f_b, start,
            edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, roundabout_radius
        )
        if meeting_node is not None:
            found = True
            break

    ms = (time.perf_counter()-t0)*1000

    max_search_step = max([se['end'] for se in search_edges_anim] + [0.0])

    if not found or meeting_node is None: return search_edges_anim, [], 0.0, ms, max_search_step

    path_f = []
    path_edges_f = []
    curr = meeting_node
    while curr is not None:
        path_f.append(curr)
        if curr in came_from_edge_f:
            path_edges_f.append(came_from_edge_f[curr])
        curr = came_from_f.get(curr)
    path_f.reverse()
    path_edges_f.reverse()

    path_b = []
    path_edges_b = []
    curr = meeting_node
    while curr is not None:
        path_b.append(curr)
        if curr in came_from_edge_b:
            path_edges_b.append(came_from_edge_b[curr])
        curr = came_from_b.get(curr)

    path = path_f + path_b[1:]
    path_edges = path_edges_f + path_edges_b

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
