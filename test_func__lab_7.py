import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestGetTriangleType(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")
        self.assertEqual(get_triangle_type(2, 2, 3), "isosceles")
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")

    def test_negative(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 5)
        with self.assertRaises(ValueError):
            get_triangle_type(0, 2, 3)
        with self.assertRaises(ValueError):
            get_triangle_type(-1, 2, 3)

if __name__ == "__main__":
    unittest.main()