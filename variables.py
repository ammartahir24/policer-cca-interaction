# variables
import sympy as sp

t = sp.Symbol('t', real=True, positive=True) # time variable of integration
T = sp.Symbol('T', real=True, positive=True) # time variable for upper limit of integral
T_s = sp.Symbol('T_s', real=True, positive=True) # time variable for upper limit of integral
r = sp.Symbol('r', real=True, positive=True) # set rate
r_l = sp.Symbol('r_l', real=True, positive=True) # in stable state, CCA's lowest rate (right after a rate/cwnd reduction)
r_h = sp.Symbol('r_h', real=True, positive=True) # in stable state, CCA's highest rate (right before a rate/cwnd reduction)
R = sp.Symbol('RTT', real=True, positive=True) # RTT of the flow
K = sp.Symbol('K', real=True, positive=True) # Cubic param K
C = sp.Symbol('C', real=True, positive=True) # Cubic param C
beta = sp.Symbol('beta', real=True, positive=True) # CCA param beta