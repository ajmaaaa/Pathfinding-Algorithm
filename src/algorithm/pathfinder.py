import math
import time
from src.algorithm.heuristic import euclidean_distance
from src.algorithm.min_heap import MinHeap


def run_astar_anim(start, end, nodes):
    t0 = time.perf_counter()

    # Reset atribut animasi node
    for n in nodes:
        n.eval_step = float('inf')
        n.disc_step = float('inf')

    # Kondisi aman jika start/end tidak valid
    if start is None or end is None:
        ms = (time.perf_counter() - t0) * 1000
        return [], [], 0.0, ms, 0.0

    # Jika start dan tujuan sama
    if start is end:
        start.disc_step = 0
        start.eval_step = 0
        ms = (time.perf_counter() - t0) * 1000
        return [], [], 0.0, ms, 0.0

    open_heap = MinHeap()
    open_set = set()
    closed_set = set()
    came_from = {}

    g_cost = {start: 0.0}

    start.disc_step = 0
    open_heap.put(start, euclidean_distance(start, end))
    open_set.add(start)

    search_edges_anim = []
    final_path_anim = []

    step = 0.0
    found = False

    while not open_heap.empty():
        current = open_heap.get()

        if current not in open_set:
            continue

        open_set.remove(current)

        if current in closed_set:
            continue

        closed_set.add(current)
        current.eval_step = step

        if current is end:
            found = True
            break

        advanced = False

        for edge in current.edges:
            if edge[0] is current:
                neighbor = edge[1]
            elif edge[1] is current:
                neighbor = edge[0]
            else:
                continue

            if neighbor in closed_set:
                continue

            edge_dist = math.hypot(current.x - neighbor.x, current.y - neighbor.y)
            new_g = g_cost[current] + edge_dist

            old_g = g_cost.get(neighbor, float('inf'))
            better_path = new_g < old_g

            if better_path or neighbor.disc_step == float('inf'):
                search_edges_anim.append({
                    'from': current,
                    'to': neighbor,
                    'target': neighbor,
                    'start': step,
                    'end': step + 1,
                    'is_optimal': better_path
                })
                advanced = True

            if better_path:
                came_from[neighbor] = current
                g_cost[neighbor] = new_g

                f_cost = new_g + euclidean_distance(neighbor, end)

                open_heap.put(neighbor, f_cost)
                open_set.add(neighbor)

                if neighbor.disc_step == float('inf'):
                    neighbor.disc_step = step + 1

        if advanced:
            step += 1
        else:
            step += 0.5

    ms = (time.perf_counter() - t0) * 1000

    # Jika tidak ditemukan jalur
    if not found:
        return search_edges_anim, [], 0.0, ms, step

    # Backtracking jalur dari end ke start
    path = []
    current = end

    while current is not None:
        path.append(current)

        if current is start:
            break

        current = came_from.get(current)

    path.reverse()

    if not path or path[0] is not start:
        return search_edges_anim, [], 0.0, ms, step

    # Membuat animasi jalur akhir
    dist = 0.0
    path_step = step + 1
    car_speed_factor = 25.0

    for i in range(1, len(path)):
        from_node = path[i - 1]
        to_node = path[i]

        edge_dist = math.hypot(from_node.x - to_node.x, from_node.y - to_node.y)
        dist += edge_dist

        time_cost = max(0.5, edge_dist / car_speed_factor)

        final_path_anim.append({
            'from': from_node,
            'to': to_node,
            'start': path_step,
            'end': path_step + time_cost
        })

        path_step += time_cost

    total_steps = path_step + 2

    return search_edges_anim, final_path_anim, dist, ms, total_steps