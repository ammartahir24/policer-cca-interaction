import sympy as sp
import math
from variables import *

class Gcc():
	def __init__(self, rate, RTT, MSS):
		self.rate = rate
		self.RTT = RTT
		self.MSS = MSS
		self.avg_loss = 1.5 # based on observation that we continue to have losses resulting in more than 1 rate reduction from ecn exps
		self.beta = 1 - (self.avg_loss)*0.5
		self.alpha = 1.05
		self.name = "gcc"
		self.dt = 0.1


	def Inc(self, t):
		### r(t_k) = 1.05 * r(t_{k-1})
		### r(t) = r(0) * (1.05)^(t/d)
		### r(t) = r(0) * (e^kt) with k = ln(1.05) / d
		### r'(t) = r(t) x k
		alpha = r_l * sp.exp(K * t) * K
		return alpha

	def Dec(self, r):
		return beta * r

	def plug(self, eq):
		K_eval = math.log(self.alpha) / self.dt
		eq_eval = eq.subs({beta : self.beta, K : K_eval, C : r_l})
		return eq_eval

	def Sol(self):
		
		return None

