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

	def Inc(self, t):
		alpha = 1 / (R**2)
		return alpha

	def Dec(self, r):
		return beta * r

	def plug(self, eq):
		eq_eval = eq.subs({beta : self.beta})
		return eq_eval

	def Sol(self):
		bdp = self.rate*self.RTT
		pkts = (bdp**2) / 18
		return pkts * self.MSS

