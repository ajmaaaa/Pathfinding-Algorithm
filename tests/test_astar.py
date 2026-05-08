import unittest
from src.core.graph import Node
from src.algorithm.pathfinder import run_astar_anim


class TestAStar(unittest.TestCase):

    def buat_edge(self, node_a, node_b):
        edge = [node_a, node_b]
        node_a.edges.append(edge)
        node_b.edges.append(edge)
        return edge

    def ambil_node_jalur(self, path_edges):
        if not path_edges:
            return []

        nodes = [path_edges[0]['from']]

        for edge in path_edges:
            nodes.append(edge['to'])

        return nodes

    def test_astar_finds_path(self):
        n1 = Node(0, 0)
        n2 = Node(100, 0)
        n3 = Node(200, 0)

        self.buat_edge(n1, n2)
        self.buat_edge(n2, n3)

        se, pe, dist, ms, steps = run_astar_anim(n1, n3, [n1, n2, n3])

        self.assertTrue(len(pe) > 0)
        self.assertEqual(pe[0]['from'], n1)
        self.assertEqual(pe[-1]['to'], n3)

    def test_jalur_melewati_node_tengah(self):
        start = Node(0, 0)
        tengah = Node(100, 0)
        goal = Node(200, 0)

        self.buat_edge(start, tengah)
        self.buat_edge(tengah, goal)

        se, pe, dist, ms, steps = run_astar_anim(start, goal, [start, tengah, goal])

        node_jalur = self.ambil_node_jalur(pe)

        self.assertEqual(node_jalur, [start, tengah, goal])

    def test_start_dan_goal_sama(self):
        start = Node(0, 0)

        se, pe, dist, ms, steps = run_astar_anim(start, start, [start])

        self.assertEqual(pe, [])
        self.assertEqual(dist, 0.0)

    def test_tidak_ada_jalur_goal_terisolasi(self):
        start = Node(0, 0)
        tengah = Node(100, 0)
        goal = Node(200, 0)

        self.buat_edge(start, tengah)

        se, pe, dist, ms, steps = run_astar_anim(start, goal, [start, tengah, goal])

        self.assertEqual(pe, [])
        self.assertEqual(dist, 0.0)

    def test_tidak_ada_jalur_antar_komponen_graph(self):
        start = Node(0, 0)
        a = Node(100, 0)

        goal = Node(500, 0)
        b = Node(600, 0)

        self.buat_edge(start, a)
        self.buat_edge(goal, b)

        se, pe, dist, ms, steps = run_astar_anim(start, goal, [start, a, goal, b])

        self.assertEqual(pe, [])
        self.assertEqual(dist, 0.0)

    def test_astar_memilih_jalur_terpendek(self):
        start = Node(0, 0)

        pendek_tengah = Node(100, 0)
        goal = Node(200, 0)

        jauh_1 = Node(0, 200)
        jauh_2 = Node(200, 200)

        self.buat_edge(start, pendek_tengah)
        self.buat_edge(pendek_tengah, goal)

        self.buat_edge(start, jauh_1)
        self.buat_edge(jauh_1, jauh_2)
        self.buat_edge(jauh_2, goal)

        semua_node = [
            start,
            pendek_tengah,
            goal,
            jauh_1,
            jauh_2
        ]

        se, pe, dist, ms, steps = run_astar_anim(start, goal, semua_node)

        node_jalur = self.ambil_node_jalur(pe)

        self.assertEqual(node_jalur, [start, pendek_tengah, goal])
        self.assertAlmostEqual(dist, 200.0, delta=0.01)

    def test_jarak_rute(self):
        n1 = Node(0, 0)
        n2 = Node(100, 0)
        n3 = Node(200, 0)

        self.buat_edge(n1, n2)
        self.buat_edge(n2, n3)

        se, pe, dist, ms, steps = run_astar_anim(n1, n3, [n1, n2, n3])

        self.assertAlmostEqual(dist, 200.0, delta=0.01)


if __name__ == '__main__':
    unittest.main()