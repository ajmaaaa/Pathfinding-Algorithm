import unittest
from src.core.graph import Node
from src.algorithm.pathfinder import run_astar_anim


class TestAStar(unittest.TestCase):

    def test_astar_finds_path(self):
        # Membuat 3 node yang saling terhubung secara berurutan
        n1 = Node(0, 0)
        n2 = Node(100, 0)
        n3 = Node(200, 0)

        # Membuat koneksi n1 <-> n2
        e1 = [n1, n2]
        n1.edges.append(e1)
        n2.edges.append(e1)

        # Membuat koneksi n2 <-> n3
        e2 = [n2, n3]
        n2.edges.append(e2)
        n3.edges.append(e2)

        # Menjalankan algoritma A* dari node awal ke node tujuan
        se, pe, dist, ms, steps = run_astar_anim(
            n1, n3, [n1, n2, n3]
        )

        # Memastikan jalur ditemukan
        self.assertTrue(len(pe) > 0)

        # Memastikan jalur dimulai dari node awal
        self.assertEqual(pe[0]['from'], n1)

        # Memastikan jalur berakhir di node tujuan
        self.assertEqual(pe[-1]['to'], n3)
