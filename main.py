from variables import *
from utils import *
from cubic import Cubic
from reno import Reno
from gcc import Gcc
from solver import Solver
from simulator import Simulator


MSS = 1464 # bytes
rate = 10 # Mbps

rate_MSS = (rate*1024*1024/8) / MSS # pkts / second
RTT = 0.1 # seconds


## CCA models

reno = Reno(rate_MSS, RTT, MSS)
cubic = Cubic(rate_MSS, RTT, MSS)
gcc = Gcc(rate_MSS, RTT, MSS)

## Mathematical solvers

sol1 = Solver(reno, rate_MSS, RTT, MSS)
sol1.plot_cycles(5)
sol2 = Solver(cubic, rate_MSS, RTT, MSS)
sol2.plot_cycles(5)


sol3 = Solver(gcc, rate_MSS, RTT, MSS)
sol3.plot_cycles(5)


## Simulators


reno_simulator = Simulator(reno, rate_MSS, RTT, MSS)

reno_simulator.simulate_shaper(3)
reno_simulator.simulate_phantom(3)
reno_simulator.plot_difference_queue_growth()

cubic_simulator = Simulator(cubic, rate_MSS, RTT, MSS)

cubic_simulator.simulate_shaper(3)
cubic_simulator.plot_difference_queue_growth()
cubic_simulator.simulate_phantom(3)