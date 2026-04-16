import unittest
from src.algorithm.min_heap import MinHeap

class TestMinHeap(unittest.TestCase):
    def test_put_and_get(self):
        heap = MinHeap()
        self.assertTrue(heap.empty())
        
        heap.put("NodeC", 10)
        heap.put("NodeA", 2)
        heap.put("NodeB", 5)
        
        self.assertFalse(heap.empty())
        
        # Harus mengembalikan sesuai prioritas terendah
        self.assertEqual(heap.get(), "NodeA")
        self.assertEqual(heap.get(), "NodeB")
        self.assertEqual(heap.get(), "NodeC")
        self.assertTrue(heap.empty())