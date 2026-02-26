import sympy as sp

def simplify(eq):
	return sp.nsimplify(eq).simplify()


def solve_real(eq, var):
	solution = sp.solve(eq, var)
	solution = [simplify(sol) for sol in solution]
	solution = [sol for sol in solution if not sol.has(sp.I)]
	return solution[-1]


def bytes_to_mbps():
	return 8 / (1024 * 1024)

def mbps_to_bytes():
	return 1 / bytes_to_mbps()