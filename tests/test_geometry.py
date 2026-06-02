import unittest
from src.core.geometry import catmull_rom


class TestGeometry(unittest.TestCase):

    def test_catmull_rom(self):
        # Empat titik kontrol untuk membentuk kurva Catmull-Rom
        p0 = (0, 0)
        p1 = (1, 1)
        p2 = (2, 0)
        p3 = (3, -1)

        # Menghitung titik kurva pada parameter t = 0.5
        res = catmull_rom(p0, p1, p2, p3, 0.5)

        # Memastikan hasil perhitungan valid
        self.assertIsNotNone(res)

        # Hasil harus berupa koordinat (x, y)
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 2)


if __name__ == "__main__":
    unittest.main()