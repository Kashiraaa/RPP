import unittest  # Импортирование модуля для написания тестов unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides  # Импортирование функции и исключения для тестирования

class TestGetTriangleType(unittest.TestCase):  # Создание класса для тестирования функции
    def test_positive(self):  # Определение метода тестирования с положительными случаями
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")  # Проверка для неравностороннего треугольника
        self.assertEqual(get_triangle_type(2, 2, 3), "isosceles")  # Проверка для равнобедренного треугольника
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")  # Проверка для равностороннего треугольника

    def test_negative(self):  # Определение метода тестирования с отрицательными случаями
        with self.assertRaises(IncorrectTriangleSides):  # Проверка исключения для некорректных сторон треугольника
            get_triangle_type(1, 2, 5)
        with self.assertRaises(ValueError):  # Проверка исключения для некорректных значений сторон треугольника
            get_triangle_type(0, 2, 3)
        with self.assertRaises(ValueError):  # Проверка исключения для отрицательных значений сторон треугольника
            get_triangle_type(-1, 2, 3)

if __name__ == "__main__":  # Проверка, что скрипт запущен напрямую
    unittest.main()  # Запуск модуля unittest для выполнения тестов