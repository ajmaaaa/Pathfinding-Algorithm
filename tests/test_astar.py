import unittest
from src.core.graph import Node
from src.algorithm.pathfinder import run_astar_anim

class TestAStar(unittest.TestCase):
    def test_astar_finds_path(self):
        n1 = Node(0, 0)
        n2 = Node(100, 0)
        n3 = Node(200, 0)
        e1 = [n1, n2]
        n1.edges.append(e1); n2.edges.append(e1)
        e2 = [n2, n3]
        n2.edges.append(e2); n3.edges.append(e2)
        
        se, pe, dist, ms, steps = run_astar_anim(n1, n3, [n1, n2, n3])
        self.assertTrue(len(pe) > 0)
        self.assertEqual(pe[0]['from'], n1)
        self.assertEqual(pe[-1]['to'], n3)