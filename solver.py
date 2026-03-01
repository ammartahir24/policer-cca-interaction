import numpy as np
import matplotlib.pyplot as plt

from variables import *
from utils import *
from cubic import Cubic
from reno import Reno


class Solver():
	def __init__(self, cca, rate, RTT, MSS):
		self.cca = cca
		self.rate = rate
		self.RTT = RTT
		self.MSS = MSS


		### rate equation to model how rate changes over time with Additive Increments

		# r(t) = r_l + integral(0, T) Inc(t) dt
		add_incr = sp.integrate(cca.Inc(t), t)
		val_at_zero = add_incr.subs(t, 0)
		self.r_t = (r_l - val_at_zero) + add_incr
		print("r(t): ", self.r_t)
		print("======")

		### bytes sent as rate goes from r_l  to r_h over time T_expr

		# A(t) = integral(0, T) r(t) dt

		self.A = sp.integrate(self.r_t, (t, T_s, T))
		print("A(t): ", self.A)

		self.find_rh_rl()
		self.find_queue_size()

		self.r_t_solved = self.plug(self.cca.plug(self.r_t))

		Qsize = sp.integrate(sp.Max(0, self.r_t_solved - self.rate), (t, T_s, T))
		self.A_solved = self.plug(self.cca.plug(Qsize))


	def find_rh_rl(self):

		# Find time taken to go from r_l (lower rate at start of saw-tooth) to r_h (highest rate before loss leading to window reduction)

		r_expr = self.r_t.subs(t, T)
		equation_T = sp.Eq(r_expr, r_h)
		T_h = solve_real(equation_T, T) # should be only 1 solution?
		T_h = T_h.subs({r_l : self.cca.Dec(r_h)})
		T_h = simplify(self.cca.plug(T_h))



		### r_l is related to r_h based on CCA's multiplicative decrease

		A_h = self.A.subs({r_l : self.cca.Dec(r_h)})
		A_h = A_h.subs({T_s: 0})
		A_h = A_h.subs({T: T_h})

		### while CCA's rate goes from r_l to r_h, bottleneck continues to dequeue at rate r
		### assuming r_l was rate right after previous loss and r_h is rate right before current loss
		### we should have A == r*T

		equation_A_h = sp.Eq(A_h, r * T_h)
		equation_A_h = equation_A_h.subs({r_l : self.cca.Dec(r_h)})

		### From above we can solve for r_l and r_h
		r_h_expr = solve_real(self.cca.plug(equation_A_h), r_h)
		r_l_expr = self.cca.Dec(r_h_expr)

		print("r_l, r_h, r")
		print(self.cca.plug(r_l_expr).evalf(), 1.0*self.cca.plug(r_h_expr).evalf(), r)
		print("======")

		self.r_l = self.cca.plug(r_l_expr)
		self.r_h = self.cca.plug(r_h_expr)


	def time_to_r(self, r_):
		
		r_expr = self.r_t.subs(t, T)

		equation_T_r = sp.Eq(r_expr / r, r_ / r)
		equation_T_r = equation_T_r.subs({r_l : self.r_l})
		equation_T_r = equation_T_r.subs({r_h : self.r_h})
		equation_T_r = self.cca.plug(equation_T_r)
		equation_T_r = equation_T_r.subs({r_h : self.r_h})

		print(equation_T_r)
		T_r = solve_real(equation_T_r, T)
		T_r = T_r.subs({r_l : self.r_l})
		T_r = simplify(self.cca.plug(T_r))
		T_r = T_r.subs({r_h : self.cca.plug(self.r_h)})

		return T_r

	def area_under_rt(self, T_l, T_h):
		A_Tl_Th = self.A.subs({T_s : T_l, T : T_h})
		A_Tl_Th = A_Tl_Th.subs({r_l : self.r_l, r_h : self.r_h})
		A_Tl_Th = self.cca.plug(A_Tl_Th)
		return A_Tl_Th

	def find_queue_size(self):

		### find the time taken for rate to go from 0 to r, i.e. time when CCA reaches rate r
		T_r = self.time_to_r(r)
		print("T (to reach r): ", T_r)

		### time to reach r_h
		T_h = self.time_to_r(self.r_h)
		print("T (to reach r_h): ", T_h)

		### time taken to go from rate r to r_h
		T_T_r = T_h - T_r
		print("T (to reach r_h from r): ", simplify(T_T_r))


		### bytes sent between T_r and T_h
		A_Tr_T = self.area_under_rt(T_r, T_h)

		print("A(Tr, T): ", A_Tr_T)
		print("======")


		### bytes between time 0 and T_r
		A_Tr = self.area_under_rt(0, T_r)

		print("A(0, Tr): ", A_Tr)
		print("======")

		### subtract r*(dT) for this duration to find excess bytes sent by the CCA

		dequeues_Tr_T = r * (T_T_r)
		overshoots = A_Tr_T - dequeues_Tr_T
		overshoots = self.cca.plug(overshoots)

		overshoots = overshoots.subs({r_h : self.r_h})
		overshoots = overshoots.subs({r : self.rate, R : self.RTT}).evalf()

		print("Overshoot Bytes (r -> r_h): ", overshoots * self.MSS)

		dequeues_Tr = r * (T_r)
		undershoots = dequeues_Tr - A_Tr
		undershoots = self.cca.plug(undershoots)

		undershoots = undershoots.subs({r_h : self.r_h})
		undershoots = undershoots.subs({r : self.rate, R : self.RTT}).evalf()

		print("Undershoot Bytes (r_l -> r): ", undershoots * self.MSS)

		self.T_r = T_r.subs({r : self.rate, R : self.RTT}).evalf()
		self.T_h = T_h.subs({r : self.rate, R : self.RTT}).evalf()

		self.phq_max = max(undershoots, overshoots) * self.MSS
		print("Phantom Queue Size: ", self.phq_max)
		print("Solution (cmp): ", self.cca.Sol())


	def plot_cycles(self, cycles):
		samples = 500
		cycle_time_len = float(self.T_h)
		dt = cycle_time_len / samples

		time = np.linspace(0, cycle_time_len, 500)
		time_normed_r = np.linspace(0, cycle_time_len, 500)
		for i in range(1, cycles):
			time_i = np.linspace(0, cycle_time_len, 500)
			time_i_ = [t_ + i*cycle_time_len for t_ in time_i]
			time = np.concatenate((time, time_i_))
			time_normed_r = np.concatenate((time_normed_r, time_i))

		r_t = sp.lambdify(t, (bytes_to_mbps() * self.MSS * self.r_t_solved), 'numpy')

		rs = r_t(time_normed_r)


		qsize = []

		if cycles == 1:
			A_t = sp.lambdify((T_s, T), ((self.MSS / 1024) * self.A_solved), 'numpy')
			qsize = A_t(0, time)

		else:
			q_occup = 0
			for r_s in rs:
				q_occup += (dt * r_s)
				q_occup -= (dt * self.rate * self.MSS * bytes_to_mbps())
				q_occup = max(0, q_occup)
				qsize.append((q_occup * mbps_to_bytes() / 1024))

		plt.figure(figsize=(10, 4)) 
		plt.plot(time, rs, label='$r(t)$ (Arrival Rate)')
		plt.axhline(self.rate * self.MSS * bytes_to_mbps(), label='$dq(t)$ (Service Rate)', linestyle='--')
		plt.xlabel('Time ($t$)')
		plt.ylabel('Mbps')
		plt.legend()
		plt.grid(True)
		plt.savefig(self.cca.name + '_rates_plot.png')

		plt.figure(figsize=(10, 4)) 
		plt.plot(time, qsize, label='$Q(t)$ (Queue Size)', color='orange')
		plt.xlabel('Time ($t$)')
		plt.ylabel('KiloBytes')
		plt.legend()
		plt.grid(True)
		plt.savefig(self.cca.name + '_qsize_plot.png')



	def plug(self, eq):
		eq = eq.subs({r_h : self.r_h, r_l : self.r_l})
		eq = eq.subs({r : self.rate, R : self.RTT}).evalf()
		return eq


