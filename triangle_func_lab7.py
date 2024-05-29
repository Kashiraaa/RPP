class IncorrectTriangleSides(Exception): pass  # Определение пользовательского исключения для случая неверных сторон треугольника

def get_triangle_type(a, b, c):  # Определение функции get_triangle_type с параметрами a, b, c
    if a <= 0 or b <= 0 or c <= 0:  # Проверка на положительность сторон треугольника
        raise ValueError("Side lengths must be positive")  # Вызов исключения ValueError, если стороны не положительные
    if a + b <= c or a + c <= b or b + c <= a:  # Проверка на невозможность построения треугольника
        raise IncorrectTriangleSides("Incorrect triangle sides")  # Вызов пользовательского исключения при неверных сторонах треугольника
    if a == b == c:  # Проверка на равносторонний треугольник
        return "equilateral"  # Возвращаем "equilateral" если треугольник равносторонний
    elif a == b or a == c or b == c:  # Проверка на равнобедренный треугольник
        return "isosceles"  # Возвращаем "isosceles" если треугольник равнобедренный
    else:  # Если не равносторонний и не равнобедренный
        return "nonequilateral"  # Возвращаем "nonequilateral"