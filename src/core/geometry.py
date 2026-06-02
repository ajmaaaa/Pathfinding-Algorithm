def catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    f1 = -0.5*t3 + t2 - 0.5*t
    f2 =  1.5*t3 - 2.5*t2 + 1.0
    f3 = -1.5*t3 + 2.0*t2 + 0.5*t
    f4 =  0.5*t3 - 0.5*t2
    x = p0[0]*f1 + p1[0]*f2 + p2[0]*f3 + p3[0]*f4
    y = p0[1]*f1 + p1[1]*f2 + p2[1]*f3 + p3[1]*f4
    return x, y


def cubic_bezier(p0, p1, p2, p3, t):
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    x = uuu*p0[0] + 3*uu*t*p1[0] + 3*u*tt*p2[0] + ttt*p3[0]
    y = uuu*p0[1] + 3*uu*t*p1[1] + 3*u*tt*p2[1] + ttt*p3[1]
    return x, y


def uniform_bspline(points, samples_per_segment=10):
    if len(points) < 4:
        return points[:]

    out = []
    for i in range(len(points) - 3):
        p0, p1, p2, p3 = points[i:i+4]
        for s in range(samples_per_segment):
            t = s / float(samples_per_segment)
            t2 = t * t
            t3 = t2 * t

            x = ((-t3 + 3*t2 - 3*t + 1) * p0[0] +
                 (3*t3 - 6*t2 + 4) * p1[0] +
                 (-3*t3 + 3*t2 + 3*t + 1) * p2[0] +
                 t3 * p3[0]) / 6.0

            y = ((-t3 + 3*t2 - 3*t + 1) * p0[1] +
                 (3*t3 - 6*t2 + 4) * p1[1] +
                 (-3*t3 + 3*t2 + 3*t + 1) * p2[1] +
                 t3 * p3[1]) / 6.0

            out.append((x, y))

    out.append(points[-2])
    return out


def make_curved_edge_points(a, b, bend=0.115, steps=72, use_bspline=False):
    p0 = (a.x, a.y)
    p3 = (b.x, b.y)

    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]

    dist = max(1.0, (dx*dx + dy*dy) ** 0.5)

    nx = -dy / dist
    ny = dx / dist

    key = int(abs(a.x + b.x) * 0.17 + abs(a.y + b.y) * 0.29)
    sign = 1.0 if key % 2 == 0 else -1.0

    amp = min(175.0, max(36.0, dist * bend)) * sign

    c1 = (
        p0[0] + dx * 0.38 + nx * amp,
        p0[1] + dy * 0.38 + ny * amp
    )

    c2 = (
        p0[0] + dx * 0.62 + nx * amp,
        p0[1] + dy * 0.62 + ny * amp
    )

    if use_bspline:
        controls = [p0, p0, c1, c2, p3, p3]
        pts = uniform_bspline(controls, max(4, steps // 3))
        pts[0] = p0
        pts[-1] = p3
        return pts

    return [
        cubic_bezier(p0, c1, c2, p3, i / float(steps))
        for i in range(steps + 1)
    ]


def polyline_length(points):
    total = 0.0

    for i in range(1, len(points)):
        dx = points[i][0] - points[i-1][0]
        dy = points[i][1] - points[i-1][1]
        total += (dx*dx + dy*dy) ** 0.5

    return total