import sympy as sp

def simplify(eq):
	eq = sp.expand_log(eq, force=True)
	return sp.nsimplify(eq).simplify().evalf()


def solve_real(eq, var):

	try:
		return sp.nsolve(eq, var, 0)
	except:
		pass

	try:
		solution = sp.solve(eq.evalf(), var)
		real_solutions = [sol for sol in solution if not sol.has(sp.I)]
		if real_solutions:
			return simplify(real_solutions[-1])
		
	except (sp.SympifyError, ValueError, NotImplementedError):
		return None


def bytes_to_mbps():
	return 8 / (1024 * 1024)

def mbps_to_bytes():
	return 1 / bytes_to_mbps()