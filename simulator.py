import numpy as np
import matplotlib.pyplot as plt
from reno import Reno
from cubic import Cubic
from utils import *

class Simulator(object):
	def __init__(self, cca, rate, RTT, MSS):
		self.cca = cca
		self.rate = rate
		self.D = RTT
		self.MSS = MSS

		self.qsize = self.D * self.rate
		self.phqsize = self.cca.Sol() / self.MSS


	def simulate_shaper(self, n):
		Q = 0
		t = 0
		drops = 0
		cwnd = self.qsize

		times = []
		cwnds = []
		rates = []
		queues = []
		drop_ts = []
		
		self.cca.reset()

		while (drops < n):
			Q += cwnd
			Q -= (self.rate * self.D)
			Q = max(0, Q)

			t += self.D
			dt = (Q / self.rate)

			sent = cwnd
			if Q > self.qsize:
				drops += 1
				cwnd = self.cca.decrement_cwnd(cwnd, t + dt)
				drop_ts.append(t + dt)
				Q = min(Q, self.qsize)

			else:
				cwnd = self.cca.increment_cwnd(cwnd, t + dt)

			times.append(t)
			cwnds.append(sent)
			rate = sent / (self.D + dt)
			rates.append(rate)
			queues.append(Q)

			t += dt	
			Q -= max(0, self.rate * (dt))
			Q = max(0, Q)

		self.plot(times, cwnds, rates, queues, drop_ts, "shaper")
		return


	def simulate_phantom(self, n):
		Q = 0
		t = 0
		drops = 0
		cwnd = self.qsize

		times = []
		cwnds = []
		rates = []
		queues = []
		drop_ts = []

		self.cca.reset()
		while (drops < n):
			Q += cwnd
			Q -= (self.rate * self.D)
			Q = max(0, Q)

			t += self.D
			dt = 0
			sent = cwnd

			if Q > self.phqsize:
				drops += 1
				cwnd = self.cca.decrement_cwnd(cwnd, t)
				drop_ts.append(t)
				Q = min(Q, self.phqsize)

			else:
				cwnd = self.cca.increment_cwnd(cwnd, t)

			times.append(t)
			cwnds.append(sent)
			rate = sent / (self.D + dt)
			rates.append(rate)
			queues.append(Q)

			t += dt	
			Q -= max(0, self.rate * (dt))
			Q = max(0, Q)

		self.plot(times, cwnds, rates, queues, drop_ts, "phantom")
		return

	def plot(self, t, cwnd, rate, queue, drops, bn):


		plt.figure(figsize=(10, 4)) 
		plt.plot(t, cwnd, label='$w(t)$ (Congestion Window)')
		plt.axhline(self.rate * self.D, label='BDP', linestyle='--')
		drops_ys = [1 for d in drops]
		plt.scatter(drops, drops_ys, label="Drops", marker="x", color="r")
		plt.xlabel('Time ($t$)')
		plt.ylabel('MSS Packets')
		plt.legend()
		plt.grid(True)
		plt.ylim(0)
		plt.savefig(f"figs/{self.cca.name}_{bn}_cwnd.png")

		rate = [bytes_to_mbps() * self.MSS * r for r in rate]
		plt.figure(figsize=(10, 4)) 
		plt.plot(t, rate, label='$r(t)$ (Arrival Rate)')
		plt.scatter(drops, drops_ys, label="Drops", marker="x", color="r")
		plt.axhline(self.rate * self.MSS * bytes_to_mbps(), label='$dq(t)$ (Service Rate)', linestyle='--')
		plt.xlabel('Time ($t$)')
		plt.ylabel('MSS Packets')
		plt.legend()
		plt.grid(True)
		plt.ylim(0)
		plt.savefig(f"figs/{self.cca.name}_{bn}_rate.png")

		plt.figure(figsize=(10, 4))
		queue = [q*self.MSS for q in queue]
		plt.plot(t, queue, label='$Q(t)$ (Queue Size)', color='orange')
		plt.scatter(drops, drops_ys, label="Drops", marker="x", color="r")
		plt.xlabel('Time ($t$)')
		plt.ylabel('Bytes')
		plt.legend()
		plt.grid(True)
		plt.ylim(0)
		plt.savefig(f"figs/{self.cca.name}_{bn}_queue.png")




