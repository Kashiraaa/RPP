class IncorrectTriangleSides(Exception):  # Объявление пользовательского исключения для случая неверных сторон треугольника
    pass

class Triangle:
    def __init__(self, a, b, c):  # Метод инициализации класса Triangle
        if a <= 0 or b <= 0 or c <= 0:  # Проверка на положительность сторон треугольника
            raise ValueError("Side lengths must be positive")  # Вызов ошибки, если стороны не положительные
        if a + b <= c or a + c <= b or b + c <= a:  # Проверка на корректность сторон треугольника
            raise IncorrectTriangleSides("Incorrect triangle sides")  # Вызов пользовательской ошибки для некорректных сторон
        self.a = a  # Инициализация стороны a
        self.b = b  # Инициализация стороны b
        self.c = c  # Инициализация стороны c

    def triangle_type(self):  # Метод определения типа треугольника
        if self.a == self.b == self.c:  # Проверка на равносторонний треугольник
            return "equilateral"  # Возвращение типа "равносторонний"
        elif self.a == self.b or self.a == self.c or self.b == self.c:  # Проверка на равнобедренный треугольник
            return "isosceles"  # Возвращение типа "равнобедренный"
        else:
            return "nonequilateral"  # Возвращение типа "неравносторонний"

    def perimeter(self):  # Метод вычисления периметра треугольника
        return self.a + self.b + self.c  # Возвращение суммы сторон треугольника