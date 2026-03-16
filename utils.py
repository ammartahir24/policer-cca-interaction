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

def derivative(time, var):
	var_t, var_t_plus = var[:-1], var[1:]
	time_t, time_t_plus = time[:-1], time[1:]

	var_diff = [v_t_p - v_t for v_t, v_t_p in zip(var_t, var_t_plus)]
	time_diff = [v_t_p - v_t for v_t, v_t_p in zip(time_t, time_t_plus)]

	deriv_var = [dvar / dt for dvar, dt in zip(var_diff, time_diff)]
	return deriv_var