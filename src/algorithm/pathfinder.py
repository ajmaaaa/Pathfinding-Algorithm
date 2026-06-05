import math
import time
from src.algorithm.heuristic import euclidean_distance
from src.algorithm.min_heap import MinHeap
from src.core.geometry import cubic_bezier, make_curved_edge_points, polyline_length, _clip_polyline, get_roundabout_clip_distance

def _edge_curve(edge, from_node, edge_curves):
    curve = edge_curves.get(id(edge)) if edge_curves else None
    if not curve:
        to_node = edge[1] if edge[0] is from_node else edge[0]
        return [(from_node.x, from_node.y), (to_node.x, to_node.y)]
    if edge[0] is from_node:
        return curve[:]
    return list(reversed(curve))

def _unit(dx, dy):
    length = math.hypot(dx, dy)
    return (dx / length, dy / length) if length > 0.0001 else (1.0, 0.0)

def _sample_bezier(p0, c1, c2, p3, steps=24):
    return [cubic_bezier(p0, c1, c2, p3, i / float(steps)) for i in range(steps + 1)]

def _arc_points(rb_node, start_ang, end_ang, radius, steps=24):
    cx, cy = rb_node.x, rb_node.y
    delta = (end_ang - start_ang + math.pi * 3) % (math.pi * 2) - math.pi
    if delta > 0:
        delta -= math.pi * 2
    if abs(delta) < 0.28:
        delta = -0.28
    pts = []
    for i in range(steps + 1):
        a = start_ang + delta * (i / steps)
        pts.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius * 0.5))
    return pts

def _arc_around_roundabout(rb_node, start_pt, end_pt, radius, steps=24):
    cx, cy = rb_node.x, rb_node.y
    a1 = math.atan2((start_pt[1] - cy) / 0.5, start_pt[0] - cx)
    a2 = math.atan2((end_pt[1] - cy) / 0.5, end_pt[0] - cx)
    return _arc_points(rb_node, a1, a2, radius, steps)

def _roundabout_turn_curve(rb_node, incoming, outgoing, radius):
    return _arc_around_roundabout(rb_node, incoming[-1], outgoing[0], radius)

def _prepare_drive_curve(path, edge, i, edge_curves, roundabout_radius, blend_radius=None):
    curve = _edge_curve(edge, path[i - 1], edge_curves)
    r_start = get_roundabout_clip_distance(path[i - 1], path[i]) if path[i - 1].is_roundabout else (60.0 if i > 1 else 0.0)
    r_end = get_roundabout_clip_distance(path[i], path[i - 1]) if path[i].is_roundabout else (60.0 if i < len(path) - 1 else 0.0)
    return _clip_polyline(curve, r_start, r_end)

def forward_search(open_heap, open_set_tracker, visited_self, visited_other, open_set_tracker_other, came_from, came_from_edge, g, f, goal, edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, disc_self, eval_self, roundabout_radius=140.25):
    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
        open_set_tracker.remove(cur)
        eval_self[cur] = disc_self[cur]
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
            
            is_meeting = (nb in visited_other or nb in open_set_tracker_other)
            
            r_start = get_roundabout_clip_distance(cur, nb) if cur.is_roundabout else 0.0
            r_end = get_roundabout_clip_distance(nb, cur) if nb.is_roundabout else 0.0
            search_curve = _clip_polyline(curve, r_start, r_end)
            dur_road = polyline_length(search_curve) / SEARCH_SPEED_FACTOR
            dur_turn = 0.0
            
            if cur.is_roundabout:
                parent, e_in = came_from.get(cur), came_from_edge.get(cur)
                if parent and e_in:
                    incoming_raw = _edge_curve(e_in, parent, edge_curves)
                    r_in_start = get_roundabout_clip_distance(parent, cur) if parent.is_roundabout else 0.0
                    r_in_end = get_roundabout_clip_distance(cur, parent)
                    clipped_in = _clip_polyline(incoming_raw, r_in_start, r_in_end)
                    turn_curve = _roundabout_turn_curve(cur, clipped_in[-2:], search_curve[:2], roundabout_radius)
                    dur_turn = polyline_length(turn_curve) / SEARCH_SPEED_FACTOR
            
            dur = dur_turn + dur_road
            
            if cur.is_roundabout and dur_turn > 0.0:
                search_edges_anim.append({
                    'from': cur, 'to': cur, 'target': cur,
                    'start': disc_self[cur], 'end': disc_self[cur] + dur_turn, 'is_optimal': True,
                    'curve': turn_curve, 'dir': 'f'
                })
                
            search_edges_anim.append({
                'from': cur, 'to': nb, 'target': nb,
                'start': disc_self[cur] + dur_turn, 'end': disc_self[cur] + dur_turn + dur_road, 'is_optimal': True,
                'curve': search_curve, 'dir': 'f'
            })
            
            if is_meeting:
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                disc_self[nb] = disc_self[cur] + dur
                return nb
                
            if tg < g[nb]:
                search_edges_anim[:] = [se for se in search_edges_anim if se.get('target') is not nb]
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                f[nb] = tg + euclidean_distance(nb, goal)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                disc_self[nb] = disc_self[cur] + dur
        return None
    return None

def backward_search(open_heap, open_set_tracker, visited_self, visited_other, open_set_tracker_other, came_from, came_from_edge, g, f, goal, edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR, disc_self, eval_self, roundabout_radius=140.25):
    while not open_heap.empty():
        cur = open_heap.get()
        if cur not in open_set_tracker:
            continue
        open_set_tracker.remove(cur)
        eval_self[cur] = disc_self[cur]
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
            
            is_meeting = (nb in visited_other or nb in open_set_tracker_other)
            
            r_start = get_roundabout_clip_distance(cur, nb) if cur.is_roundabout else 0.0
            r_end = get_roundabout_clip_distance(nb, cur) if nb.is_roundabout else 0.0
            search_curve = _clip_polyline(curve, r_start, r_end)
            dur_road = polyline_length(search_curve) / SEARCH_SPEED_FACTOR
            dur_turn = 0.0
            
            if cur.is_roundabout:
                parent, e_in = came_from.get(cur), came_from_edge.get(cur)
                if parent and e_in:
                    incoming_raw = _edge_curve(e_in, parent, edge_curves)
                    r_in_start = get_roundabout_clip_distance(parent, cur) if parent.is_roundabout else 0.0
                    r_in_end = get_roundabout_clip_distance(cur, parent)
                    clipped_in = _clip_polyline(incoming_raw, r_in_start, r_in_end)
                    turn_curve = _roundabout_turn_curve(cur, clipped_in[-2:], search_curve[:2], roundabout_radius)
                    dur_turn = polyline_length(turn_curve) / SEARCH_SPEED_FACTOR
            
            dur = dur_turn + dur_road
            
            if cur.is_roundabout and dur_turn > 0.0:
                search_edges_anim.append({
                    'from': cur, 'to': cur, 'target': cur,
                    'start': disc_self[cur], 'end': disc_self[cur] + dur_turn, 'is_optimal': True,
                    'curve': turn_curve, 'dir': 'b'
                })
                
            search_edges_anim.append({
                'from': cur, 'to': nb, 'target': nb,
                'start': disc_self[cur] + dur_turn, 'end': disc_self[cur] + dur_turn + dur_road, 'is_optimal': True,
                'curve': search_curve, 'dir': 'b'
            })
            
            if is_meeting:
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                disc_self[nb] = disc_self[cur] + dur
                return nb
                
            if tg < g[nb]:
                search_edges_anim[:] = [se for se in search_edges_anim if se.get('target') is not nb]
                came_from[nb] = cur
                came_from_edge[nb] = e
                g[nb] = tg
                f[nb] = tg + euclidean_distance(nb, goal)
                open_set_tracker.add(nb)
                open_heap.put(nb, f[nb])
                disc_self[nb] = disc_self[cur] + dur
        return None
    return None

def _clip_curve_to_fraction(curve, p):
    if not curve or p <= 0.0:
        return curve[:1] if curve else []
    if p >= 1.0:
        return curve[:]
    total_len = 0.0
    for i in range(1, len(curve)):
        total_len += math.hypot(curve[i][0] - curve[i-1][0], curve[i][1] - curve[i-1][1])
    target = total_len * p
    walked = 0.0
    pts = [curve[0]]
    for i in range(1, len(curve)):
        p0, p1 = curve[i-1], curve[i]
        seg_len = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if walked + seg_len >= target:
            t = (target - walked) / seg_len if seg_len > 0 else 0.0
            pts.append((p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1])))
            break
        else:
            pts.append(p1)
            walked += seg_len
    return pts

def _get_wave_start_time(u, v, edge, came_from, came_from_edge, disc_dict, edge_curves, SEARCH_SPEED_FACTOR, roundabout_radius=140.25):
    if not u.is_roundabout:
        return disc_dict.get(u, 0.0)
    parent = came_from.get(u)
    e_in = came_from_edge.get(u)
    if parent is None or e_in is None:
        return disc_dict.get(u, 0.0)
    r_in_start = get_roundabout_clip_distance(parent, u) if parent.is_roundabout else 0.0
    r_in_end = get_roundabout_clip_distance(u, parent)
    clipped_in = _clip_polyline(_edge_curve(e_in, parent, edge_curves), r_in_start, r_in_end)
    
    r_out_start = 0.0
    r_out_end = get_roundabout_clip_distance(v, u) if v.is_roundabout else 0.0
    clipped_out = _clip_polyline(_edge_curve(edge, u, edge_curves), r_out_start, r_out_end)
    
    turn_curve = _roundabout_turn_curve(u, clipped_in[-2:], clipped_out[:2], roundabout_radius)
    dur_turn = polyline_length(turn_curve) / SEARCH_SPEED_FACTOR
    t_entry = disc_dict.get(parent, 0.0) + (polyline_length(clipped_in) / SEARCH_SPEED_FACTOR)
    return t_entry + dur_turn

def run_astar_anim(start, end, nodes, edge_curves=None, roundabout_radius=140.25):
    t0 = time.perf_counter()
    for n in nodes: n.eval_step = float('inf'); n.disc_step = float('inf')

    open_heap_f, open_heap_b = MinHeap(), MinHeap()
    open_set_tracker_f, open_set_tracker_b = set([start]), set([end])
    visited_f, visited_b = set(), set()
    g_f, g_b = {n: float('inf') for n in nodes}, {n: float('inf') for n in nodes}
    f_f, f_b = {n: float('inf') for n in nodes}, {n: float('inf') for n in nodes}
    came_from_f, came_from_b = {}, {}
    came_from_edge_f, came_from_edge_b = {}, {}
    
    g_f[start] = 0; f_f[start] = euclidean_distance(start, end); disc_f = {start: 0.0}; eval_f = {}
    open_heap_f.put(start, f_f[start])

    g_b[end] = 0; f_b[end] = euclidean_distance(end, start); disc_b = {end: 0.0}; eval_b = {}
    open_heap_b.put(end, f_b[end])

    search_edges_anim = []
    final_path_anim = []
    found = False
    meeting_node = None
    SEARCH_SPEED_FACTOR = 200.0

    while not open_heap_f.empty() and not open_heap_b.empty():
        f_top = open_heap_f.elements[0][2]
        b_top = open_heap_b.elements[0][2]
        
        if disc_f[f_top] <= disc_b[b_top]:
            meeting_node = forward_search(
                open_heap_f, open_set_tracker_f, visited_f, visited_b, open_set_tracker_b,
                came_from_f, came_from_edge_f, g_f, f_f, end,
                edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR,
                disc_f, eval_f, roundabout_radius
            )
        else:
            meeting_node = backward_search(
                open_heap_b, open_set_tracker_b, visited_b, visited_f, open_set_tracker_f,
                came_from_b, came_from_edge_b, g_b, f_b, start,
                edge_curves, search_edges_anim, SEARCH_SPEED_FACTOR,
                disc_b, eval_b, roundabout_radius
            )
            
        if meeting_node is not None:
            found = True
            break

    ms = (time.perf_counter()-t0)*1000
    max_search_step = max([se['end'] for se in search_edges_anim] + [0.0])

    if not found or meeting_node is None:
        return search_edges_anim, [], 0.0, ms, max_search_step

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

    T_meet = max_search_step
    if found and path:
        candidates = []
        t_f = {n: disc_f[n] for n in path if n in came_from_f or n is start}
        t_b = {n: disc_b[n] for n in path if n in came_from_b or n is end}
        
        for i in range(len(path)):
            n = path[i]
            if n in t_f and n in t_b:
                candidates.append((max(t_f[n], t_b[n]), 'node', n))
            if i < len(path) - 1:
                u, v = path[i], path[i+1]
                if u in t_f and v in t_b:
                    edge = path_edges[i]
                    t_start_f = _get_wave_start_time(u, v, edge, came_from_f, came_from_edge_f, disc_f, edge_curves, SEARCH_SPEED_FACTOR, roundabout_radius)
                    t_start_b = _get_wave_start_time(v, u, edge, came_from_b, came_from_edge_b, disc_b, edge_curves, SEARCH_SPEED_FACTOR, roundabout_radius)
                    r_start = get_roundabout_clip_distance(u, v) if u.is_roundabout else 0.0
                    r_end = get_roundabout_clip_distance(v, u) if v.is_roundabout else 0.0
                    clipped = _clip_polyline(_edge_curve(edge, u, edge_curves), r_start, r_end)
                    dur = polyline_length(clipped) / SEARCH_SPEED_FACTOR
                    t_meet_edge = (t_start_f + t_start_b + dur) / 2.0
                    if t_start_f <= t_meet_edge <= t_start_f + dur and t_start_b <= t_meet_edge <= t_start_b + dur:
                        candidates.append((t_meet_edge, 'edge', (u, v, edge, dur)))
                        
        if candidates:
            T_meet = min(c[0] for c in candidates)
        elif meeting_node:
            if meeting_node.is_roundabout:
                pf, pb = came_from_f.get(meeting_node), came_from_b.get(meeting_node)
                ef, eb = came_from_edge_f.get(meeting_node), came_from_edge_b.get(meeting_node)
                if pf and pb and ef and eb:
                    cf = _clip_polyline(_edge_curve(ef, pf, edge_curves), get_roundabout_clip_distance(pf, meeting_node) if pf.is_roundabout else 0.0, get_roundabout_clip_distance(meeting_node, pf))
                    cb = _clip_polyline(_edge_curve(eb, pb, edge_curves), get_roundabout_clip_distance(pb, meeting_node) if pb.is_roundabout else 0.0, get_roundabout_clip_distance(meeting_node, pb))
                    t_f_entry = disc_f[pf] + (polyline_length(cf) / SEARCH_SPEED_FACTOR)
                    t_b_exit = disc_b[pb] + (polyline_length(cb) / SEARCH_SPEED_FACTOR)
                    turn_curve = _roundabout_turn_curve(meeting_node, cf[-2:], cb[-2:], roundabout_radius)
                    dur_turn = polyline_length(turn_curve) / SEARCH_SPEED_FACTOR
                    T_meet = (t_f_entry + t_b_exit + dur_turn) / 2.0
                else:
                    T_meet = max(disc_f.get(meeting_node, 0.0), disc_b.get(meeting_node, 0.0))
            else:
                T_meet = max(disc_f.get(meeting_node, 0.0), disc_b.get(meeting_node, 0.0))
            
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge = path_edges[i]
            for src, dst, t_dict, came, came_edge, disc_dict, wave_dir in [
                (u, v, t_f, came_from_f, came_from_edge_f, disc_f, 'f'),
                (v, u, t_b, came_from_b, came_from_edge_b, disc_b, 'b')
            ]:
                if src in t_dict:
                    t_start = _get_wave_start_time(src, dst, edge, came, came_edge, disc_dict, edge_curves, SEARCH_SPEED_FACTOR, roundabout_radius)
                    r_start = get_roundabout_clip_distance(src, dst) if src.is_roundabout else 0.0
                    r_end = get_roundabout_clip_distance(dst, src) if dst.is_roundabout else 0.0
                    clipped = _clip_polyline(_edge_curve(edge, src, edge_curves), r_start, r_end)
                    dur = polyline_length(clipped) / SEARCH_SPEED_FACTOR
                    if not any(se['from'] is src and se['to'] is dst for se in search_edges_anim):
                        search_edges_anim.append({
                            'from': src, 'to': dst, 'target': dst,
                            'start': t_start, 'end': t_start + dur, 'is_optimal': True,
                            'curve': clipped, 'dir': wave_dir
                        })
                        
        for n in path:
            if n.is_roundabout:
                pf, pb = came_from_f.get(n), came_from_b.get(n)
                ef, eb = came_from_edge_f.get(n), came_from_edge_b.get(n)
                if pf and pb and ef and eb:
                    cf = _clip_polyline(_edge_curve(ef, pf, edge_curves), get_roundabout_clip_distance(pf, n) if pf.is_roundabout else 0.0, get_roundabout_clip_distance(n, pf))
                    cb = _clip_polyline(_edge_curve(eb, pb, edge_curves), get_roundabout_clip_distance(pb, n) if pb.is_roundabout else 0.0, get_roundabout_clip_distance(n, pb))
                    t_f_entry = disc_f[pf] + (polyline_length(cf) / SEARCH_SPEED_FACTOR)
                    t_b_exit = disc_b[pb] + (polyline_length(cb) / SEARCH_SPEED_FACTOR)
                    turn_curve = _roundabout_turn_curve(n, cf[-2:], cb[-2:], roundabout_radius)
                    dur_turn = polyline_length(turn_curve) / SEARCH_SPEED_FACTOR
                    for t_start, curve_pts, d_val in [(t_f_entry, turn_curve, 'f'), (t_b_exit, list(reversed(turn_curve)), 'b')]:
                        if not any(se['from'] is n and se['to'] is n and abs(se['start'] - t_start) < 0.0001 for se in search_edges_anim):
                            search_edges_anim.append({
                                'from': n, 'to': n, 'target': n,
                                'start': t_start, 'end': t_start + dur_turn, 'is_optimal': True,
                                'curve': curve_pts, 'dir': d_val
                            })

    for n in nodes:
        f_time = disc_f.get(n, float('inf'))
        b_time = disc_b.get(n, float('inf'))
        if f_time < b_time:
            n.search_dir = 'f'
            n.disc_step = f_time
        elif b_time < f_time:
            n.search_dir = 'b'
            n.disc_step = b_time
        else:
            n.search_dir = 'f'
            n.disc_step = f_time
        n.eval_step = min(eval_f.get(n, float('inf')), eval_b.get(n, float('inf')))
        if n.disc_step > T_meet:
            n.disc_step = float('inf')
        if n.eval_step > T_meet:
            n.eval_step = float('inf')

    clipped_search_edges = []
    for se in search_edges_anim:
        se['orig_end'] = se['end']
        if se['start'] >= T_meet:
            continue
        if se['start'] < T_meet < se['end']:
            p = (T_meet - se['start']) / (se['end'] - se['start'])
            se['end'] = T_meet
            if 'curve' in se and se['curve']:
                se['curve'] = _clip_curve_to_fraction(se['curve'], p)
        clipped_search_edges.append(se)
    search_edges_anim = clipped_search_edges

    max_search_step = T_meet
    dist = 0.0; p_step = max_search_step + 1
    CAR_SPEED_FACTOR, TURN_SPEED_FACTOR, ROUNDABOUT_SPEED_FACTOR = 24.0, 20.0, 18.0
    for i in range(1, len(path)):
        curve = _prepare_drive_curve(path, path_edges[i - 1], i, edge_curves, roundabout_radius, roundabout_radius)
        edge_dist = polyline_length(curve)
        dist += edge_dist
        time_cost = max(0.05, edge_dist / CAR_SPEED_FACTOR)
        final_path_anim.append({'from': path[i-1], 'to': path[i], 'start': p_step, 'end': p_step + time_cost, 'curve': curve})
        p_step += time_cost

        if i < len(path) - 1:
            if path[i].is_roundabout:
                next_curve = _prepare_drive_curve(path, path_edges[i], i + 1, edge_curves, roundabout_radius, roundabout_radius)
                turn_curve = _roundabout_turn_curve(path[i], curve[-2:], next_curve[:2], roundabout_radius)
                turn_dist = polyline_length(turn_curve)
                dist += turn_dist
                turn_cost = max(0.05, turn_dist / ROUNDABOUT_SPEED_FACTOR)
            else:
                next_curve = _prepare_drive_curve(path, path_edges[i], i + 1, edge_curves, roundabout_radius, roundabout_radius)
                p0, p3 = curve[-1], next_curve[0]
                dx1, dy1 = curve[-1][0] - curve[-2][0], curve[-1][1] - curve[-2][1]
                len1 = max(0.0001, math.hypot(dx1, dy1))
                t1x, t1y = dx1/len1, dy1/len1
                
                dx2, dy2 = next_curve[1][0] - next_curve[0][0], next_curve[1][1] - next_curve[0][1]
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

    return search_edges_anim, final_path_anim, dist, ms, p_step + 2
