import sympy as sp
import math
from variables import *

class Cubic():
	def __init__(self, rate, RTT, MSS):
		self.rate = rate
		self.RTT = RTT
		self.MSS = MSS
		self.beta = 0.7
		self.C = 0.4
		self.name = "cubic"


	def Inc(self, t):
		ai = (3 * C * ((t - K)**2)) / R

		return ai

	def Dec(self, r):
		return beta * r

	def plug(self, eq):
		w_max = R*r_h
		K_eval = sp.cbrt(w_max * (1 - self.beta) / self.C)
		return eq.subs({beta : self.beta, C : self.C, K:K_eval})

	def Sol(self):
		beta = 1 - self.beta
		G = 3 / (4 * self.C**(1/3))
		G *= (beta / (4 - beta)) ** (4/3)
		B = G / self.RTT
		B *= (self.rate*self.RTT)**(4/3)
		return B * self.MSS