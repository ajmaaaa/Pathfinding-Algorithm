import unittest
from src.core.geometry import catmull_rom

class TestGeometry(unittest.TestCase):
    def test_catmull_rom(self):
        p0 = (0, 0)
        p1 = (1, 1)
        p2 = (2, 0)
        p3 = (3, -1)
        # Evaluasi spline di tengah p1 dan p2 (t=0.5)
        res = catmull_rom(p0, p1, p2, p3, 0.5)
        
        self.assertIsNotNone(res)
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 2)