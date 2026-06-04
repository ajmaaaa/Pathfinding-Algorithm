import unittest
from src.algorithm.min_heap import MinHeap


class TestMinHeap(unittest.TestCase):
    def test_put_and_get(self):
        heap = MinHeap()

        # Memastikan heap kosong saat pertama dibuat
        self.assertTrue(heap.empty())

        # Menambahkan data dengan prioritas berbeda
        heap.put("NodeC", 10)
        heap.put("NodeA", 2)
        heap.put("NodeB", 5)

        self.assertFalse(heap.empty())

        # Data harus keluar berdasarkan prioritas terkecil
        self.assertEqual(heap.get(), "NodeA")
        self.assertEqual(heap.get(), "NodeB")
        self.assertEqual(heap.get(), "NodeC")

        # Heap kembali kosong setelah semua data diambil
        self.assertTrue(heap.empty())
