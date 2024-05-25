import pytest
from triangle_class import Triangle, IncorrectTriangleSides

def test_positive():
    triangle = Triangle(3, 4, 5)
    assert triangle.triangle_type() == "nonequilateral"
    assert triangle.perimeter() == 12

    triangle = Triangle(2, 2, 3)
    assert triangle.triangle_type() == "isosceles"
    assert triangle.perimeter() == 7

    triangle = Triangle(3, 3, 3)
    assert triangle.triangle_type() == "equilateral"
    assert triangle.perimeter() == 9

def test_negative():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 5)

    with pytest.raises(ValueError):
        Triangle(0, 2, 3)

    with pytest.raises(ValueError):
        Triangle(-1, 2, 3)