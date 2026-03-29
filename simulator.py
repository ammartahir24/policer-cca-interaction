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


	def simulate_shaper(self, n, plot=True):
		Q = 0
		t = 0
		drops = 0
		cwnd = self.qsize

		times = []
		cwnds = []
		rates = []
		queues = []
		drop_ts = []
		rtts = []
		
		self.cca.reset(mode = "shaper")
		cwnd = self.cca.initial_cwnd(mode = "shaper")
		last_dt = 0

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

			times.append(t - self.D)
			cwnds.append(sent)
			rate = sent / (self.D + last_dt)
			rates.append(rate)
			rtts.append(self.D + last_dt)
			queues.append(Q)

			t += dt	
			Q -= max(0, self.rate * (dt))
			Q = max(0, Q)
			last_dt = dt

		if plot:
			self.plot(times, cwnds, rates, queues, drop_ts, rtts, "shaper")
		self.changes(times, cwnds, rates, rtts, queues)
		return times, cwnds, rates, queues, drop_ts, rtts


	def simulate_phantom(self, n, plot=True):
		Q = 0
		t = 0
		drops = 0
		cwnd = self.qsize

		times = []
		cwnds = []
		rates = []
		queues = []
		drop_ts = []
		rtts = []

		self.cca.reset()
		cwnd = self.cca.initial_cwnd(mode = "policer")

		while (drops < n):
			Q += cwnd
			Q -= (self.rate * self.D)
			Q = max(0, Q)

			t += self.D
			dt = 0
			sent = cwnd

			if Q > self.qsize:
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
			rtts.append(self.D)
			queues.append(Q)

			t += dt	
			Q -= max(0, self.rate * (dt))
			Q = max(0, Q)
		if plot:
			self.plot(times, cwnds, rates, queues, drop_ts, rtts, "phantom")
		return times, cwnds, rates, queues, drop_ts, rtts

	def plot(self, t, cwnd, rate, queue, drops, rtts, bn):
		plt.figure(figsize=(7, 3)) 
		plt.plot(t, cwnd, label='Congestion Window $\omega(t)$', color="k")
		plt.axhline(self.rate * self.D, label='$BDP = rD$', linestyle='--', color="k")
		drops_ys = [1 for d in drops]
		# plt.scatter(drops, drops_ys, label="Drops", marker="x", color="r")
		plt.xlabel('Time ($t$)')
		plt.ylabel('# Packets')
		plt.legend()
		plt.grid(True)
		plt.ylim(0, 200)
		plt.xlim(0, 28)
		plt.savefig(f"figs/{self.cca.name}_{bn}_cwnd.png")
		plt.savefig(f"pdfs/{self.cca.name}_{bn}_cwnd.pdf")

		plt.figure(figsize=(7, 3)) 
		plt.plot(t, rtts, label='RTT $R(t)$', color="k")
		plt.axhline(self.D, label='Propagation Delay $D$', linestyle='--', color="k")
		plt.fill_between(t, self.D, rtts, label="Queuing Delay $Q(t) / r$", color="r", alpha=0.1, hatch="//")
		plt.xlabel('Time ($t$)')
		plt.ylabel('Seconds')
		plt.legend()
		plt.grid(True)
		plt.ylim(0, 0.3)
		plt.xlim(0, 28)
		plt.savefig(f"figs/{self.cca.name}_{bn}_rtt.png")
		plt.savefig(f"pdfs/{self.cca.name}_{bn}_rtt.pdf")

		rate = np.array([bytes_to_mbps() * self.MSS * r for r in rate])
		plt.figure(figsize=(7, 3)) 
		plt.plot(t, rate, label='CCA Sending Rate $r(t)$', color="k")
		dqrate = self.rate * self.MSS * bytes_to_mbps()
		# plt.scatter(drops, drops_ys, label="Drops", marker="x", color="r")
		plt.axhline(dqrate, label='Bottleneck Dequeue Rate $r$', linestyle='--', color="k")
		plt.fill_between(t, rate, dqrate, where=(rate < dqrate), label="Deficit", color="g", alpha=0.2, hatch="//", interpolate=True)
		plt.fill_between(t, dqrate, rate, where=(rate > dqrate), label="Overshoot", color="r", alpha=0.2, hatch="\\\\", interpolate=True)
		plt.xlabel('Time ($t$)')
		plt.ylabel('Mbps')
		plt.legend()
		plt.grid(True)
		plt.ylim(0, 20)
		plt.xlim(0, 28)
		plt.savefig(f"figs/{self.cca.name}_{bn}_rate.png")
		plt.savefig(f"pdfs/{self.cca.name}_{bn}_rate.pdf")

		plt.figure(figsize=(7, 3))
		# queue = [q*self.MSS for q in queue]
		if bn == "shaper":
			plt.fill_between(t, 0, queue, label='Queue Occupancy $Q(t)$', color='gray', alpha=0.4, hatch="\\\\\\")
			plt.axhline(self.qsize, label='Queue Size $Q_{max}$', linestyle='--', color="k")
		else:
			plt.fill_between(t, 0, queue, label='Phantom Queue Occupancy $Q(t)$', color='gray', alpha=0.4, hatch="\\\\\\")
			plt.axhline(self.qsize, label='Queue Size $Q_{max}$', linestyle='--', color="k")
		plt.xlabel('Time ($t$)')
		plt.ylabel('# Packets')
		plt.legend()
		plt.grid(True)
		plt.ylim(0, 500)
		plt.xlim(0, 28)
		plt.savefig(f"figs/{self.cca.name}_{bn}_queue.png")
		plt.savefig(f"pdfs/{self.cca.name}_{bn}_queue.pdf")


	def changes(self, times, cwnds, rates, rtts, queues):
		cwnds_deriv = derivative(times, cwnds)
		rates_deriv = derivative(times, rates)
		rtts_deriv = derivative(times, rtts)
		queues_deriv = derivative(times, queues)

		print(self.cca.name)

		print("t:", times[:10])
		print("w(t):", cwnds[:10])
		print("w'(t):", cwnds_deriv[:10])

		print("r(t):", rates[:10])
		print("r'(t):", rates_deriv[:10])
		calc_rates_deriv = [(-1 * r_) / (r**2) for r, r_ in zip(rtts, rtts_deriv)]
		print("r'(t) calculated:", calc_rates_deriv[:10])

		print("R(t):", rtts[:10])
		print("R'(t):", rtts_deriv[:10])

		print("Q(t):", queues[:10])
		print("Q'(t):", queues_deriv[:10])

	def plot_difference_queue_growth(self):
		shaper_data = self.simulate_shaper(n=1, plot=False)
		phantom_data = self.simulate_phantom(n=1, plot=False)

		shaper_t, phantom_t = shaper_data[0], phantom_data[0]
		shaper_cwnd, phantom_cwnd = shaper_data[1], phantom_data[1]
		shaper_rtt, phantom_rtt = shaper_data[5], phantom_data[5]
		shaper_q, phantom_q = shaper_data[3], phantom_data[3]

		# plot RTT difference
		plt.figure(figsize=(6, 4)) 
		plt.plot(phantom_t, phantom_rtt, label='Policer RTT $R_p(t)$', color="r")
		plt.plot(shaper_t, shaper_rtt, label='Shaper RTT $R_s(t)$', color="g")
		plt.xlabel('Time ($t$)')
		plt.ylabel('Seconds')
		plt.legend()
		plt.grid(True)
		# plt.ylim(0, 0.17)
		# plt.xlim(0, 6)
		plt.savefig(f"figs/{self.cca.name}_rtt_diff.png")
		plt.savefig(f"pdfs/{self.cca.name}_rtt_diff.pdf")

		# plot queue difference
		plt.figure(figsize=(6, 4)) 
		plt.plot(phantom_t, phantom_q, label='Policer Queue Occupancy $Q_p(t)$', color="r")
		plt.plot(shaper_t, shaper_q, label='Shaper Queue Occupancy $Q_s(t)$', color="g")
		plt.xlabel('Time ($t$)')
		plt.ylabel('# Packets')
		plt.legend()
		plt.grid(True)
		# plt.ylim(0, 0.16)
		# plt.xlim(0, 6)
		plt.savefig(f"figs/{self.cca.name}_queue_diff.png")
		plt.savefig(f"pdfs/{self.cca.name}_queue_diff.pdf")

		# plot cwnds
		min_s_cwnd, min_ph_cwnd = min(shaper_cwnd), min(phantom_cwnd)
		min_s_t, min_ph_t = min(shaper_t), min(phantom_t)
		shaper_cwnd = [s - min_s_cwnd for s in shaper_cwnd]
		phantom_cwnd = [s - min_ph_cwnd for s in phantom_cwnd]
		shaper_t = [s - min_s_t for s in shaper_t]
		phantom_t = [s - min_ph_t for s in phantom_t]
		
		plt.figure(figsize=(12, 4)) 
		plt.plot(phantom_t, phantom_cwnd, label='Policer cwnd $\omega_p(t)$', color="r")
		plt.plot(shaper_t, shaper_cwnd, label='Shaper cwnd $\omega_s(t)$', color="g")

		t = 0
		for r_p, c_p in zip(phantom_rtt, phantom_cwnd):
			plt.vlines(x=t, ymin=0, ymax=c_p, color="r", linestyle='-', linewidth=1, alpha=0.4)
			plt.hlines(y=c_p, xmin=0, xmax=t, color="r", linestyle='-', linewidth=0.5, alpha=0.4)
			t += r_p
		
		t = 0
		for r_s, c_s in zip(shaper_rtt, shaper_cwnd):
			plt.vlines(x=t, ymin=0, ymax=c_s, color="g", linestyle='-', linewidth=1, alpha=0.4)
			plt.hlines(y=c_s, xmin=0, xmax=t, color="g", linestyle='-', linewidth=0.5, alpha=0.4)
			t += r_s

		plt.xlabel('Time ($t$)')
		plt.ylabel('# Packets')
		plt.legend()
		# plt.grid(True)
		plt.xlim(0, 17)
		# plt.ylim(0, 60)
		plt.savefig(f"figs/{self.cca.name}_cwnd_diff.png")
		plt.savefig(f"pdfs/{self.cca.name}_cwnd_diff.pdf")
