import sympy as sp
from latex2sympy.process_latex import process_sympy
import re
import shelve


class EQ:
    @staticmethod
    def examine(input_line):
        i = input_line
        j = re.sub(r'\s', '', i)
        return j


class Test:
    def __init__(self):
        print(process_sympy("\\frac{d}{dx} x^{2}"))
        x = sp.Symbol('x')
        y = sp.Symbol('y')
        a = 1/((x+2)*(x+1))
        b = 1/((y-4)*(sp.exp(2)-1))
        print(sp.pretty(a))
        print(sp.pretty(b))
        print(sp.pretty(sp.exp(3).evalf()))
        print(sp.pretty(sp.exp(x).subs({x: 3})))
        x, y, z = sp.symbols('x, y, z')
        f = (80 - sp.sin(x*y) + sp.cos(y*z))
        print(sp.pretty(f))
        res = sp.integrate(f, x)
        print(sp.pretty(sp.latex(res)))


if __name__ == "__main__":
    Test()