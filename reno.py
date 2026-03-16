import sympy as sp
import math
from variables import *

class Reno():
	def __init__(self, rate, RTT, MSS):
		self.rate = rate
		self.RTT = RTT
		self.MSS = MSS
		self.beta = 0.5
		self.name = "reno"

	def reset(self, mode = "policer"):
		return

	def initial_cwnd(self, mode = "policer"):
		if mode == "policer":
			return self.rate * self.RTT * (2/3)
		else:
			return self.rate * self.RTT

	def Inc(self, t):
		# r'(t), where r(t) = w(t) / RTT(t)
		# r'(t) = (w'(t) * RTT(t) - RTT'(t) * w(t)) / RTT^2(t)
		# note that RTT'(t) = 0 for a policer because RTT(t) is a fixed propagation delay denoted by R below.
		# also for reno, w'(t) = 1 / RTT(t)
		alpha = 1 / (R**2)
		return alpha

	def Dec(self, r):
		return beta * r

	def increment_cwnd(self, cwnd, t):
		return cwnd + 1

	def decrement_cwnd(self, cwnd, t):
		return cwnd * self.beta

	def plug(self, eq):
		eq_eval = eq.subs({beta : self.beta})
		return eq_eval

	def Sol(self):
		bdp = self.rate*self.RTT
		pkts = (bdp**2) / 18
		return pkts * self.MSS

