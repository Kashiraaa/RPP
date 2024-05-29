import pytest  # импортируем библиотеку pytest для написания тестов

from triangle_class import Triangle, IncorrectTriangleSides  # импортируем класс Triangle и исключение IncorrectTriangleSides из модуля triangle_class

def test_positive():  # объявляем функцию для позитивного тестирования
    triangle = Triangle(3, 4, 5)  # создаем объект треугольника со сторонами 3, 4, 5
    assert triangle.triangle_type() == "nonequilateral"  # проверяем тип треугольника
    assert triangle.perimeter() == 12  # проверяем периметр треугольника

    triangle = Triangle(2, 2, 3)  # создаем объект треугольника со сторонами 2, 2, 3
    assert triangle.triangle_type() == "isosceles"  # проверяем тип треугольника
    assert triangle.perimeter() == 7  # проверяем периметр треугольника

    triangle = Triangle(3, 3, 3)  # создаем объект треугольника со сторонами 3, 3, 3
    assert triangle.triangle_type() == "equilateral"  # проверяем тип треугольника
    assert triangle.perimeter() == 9  # проверяем периметр треугольника

def test_negative():  # объявляем функцию для негативного тестирования
    with pytest.raises(IncorrectTriangleSides):  # проверяем срабатывание исключения IncorrectTriangleSides
        Triangle(1, 2, 5)  # пытаемся создать треугольник с невалидными сторонами

    with pytest.raises(ValueError):  # проверяем срабатывание исключения ValueError
        Triangle(0, 2, 3)  # пытаемся создать треугольник с невалидными сторонами

    with pytest.raises(ValueError):  # проверяем срабатывание исключения ValueError
        Triangle(-1, 2, 3)  # пытаемся создать треугольник с невалидными сторонами