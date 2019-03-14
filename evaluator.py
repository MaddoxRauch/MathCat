import sympy as sp
from latex2sympy.process_latex import process_sympy


x = sp.Symbol('x')
a = 1/((x+2)*(x+1))
print(sp.pretty(a))
print(sp.pretty('\\frac{1}{\\left(x + 1\\right) \\left(x + 2\\right)}'))
print(process_sympy('\\frac{1}{\\left(x + 1\\right) \\left(x + 2\\right)}'))
