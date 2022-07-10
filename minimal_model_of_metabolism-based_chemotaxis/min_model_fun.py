import numpy as np


# Probability of tumbling
def p_tumble(C):
  return 1e-5 + (C*0.01)


# Rate of transport of chemicals from environment into bacteria
def D_in(pos, offsetX=0, offsetY=0):
  coef = 0.2

  dist = np.sqrt((pos[0]-offsetX)*(pos[0]-offsetX) + (pos[1]-offsetY)*(pos[1]-offsetY))
  return coef * np.exp(-dist**2 / 2000)


# System of ODE's
def ode_sys(t, z, kf, kb, k_degC, k_degW, pos):
  E, M, MC, C, W = z
  f = [
    -kf[1]*MC*E + kb[1]*C**2*W/2 + D_in(pos, 100, 0),
    -kf[0]*M*C + kb[0]*MC + D_in(pos, 100, 0),
    -kb[0]*MC + kf[0]*M*C - kf[1]*E*MC + kb[1]*C**2*W/2,
    -kf[0]*M*C + kb[0]*MC - 2*kb[1]*C**2*W/2 + 2*kf[1]*E*MC - 2*kb[3]*C**2*W/2 - k_degC*C,
    -kb[1]*C**2*W/2 + kf[1]*E*MC - kb[3]*C**2*W/2 - k_degW*W
  ]
  return f


def euler(y0, h, kf, kb, k_degC, k_degW, pos):
  E, M, MC, C, W = y0
  f = [
    -kf[1]*MC*E + kb[1]*C**2*W/2 + D_in(pos, 100, 0),
    -kf[0]*M*C + kb[0]*MC + D_in(pos, 100, 0),
    -kb[0]*MC + kf[0]*M*C - kf[1]*E*MC + kb[1]*C**2*W/2,
    -kf[0]*M*C + kb[0]*MC - 2*kb[1]*C**2*W/2 + 2*kf[1]*E*MC - 2*kb[3]*C**2*W/2 - k_degC*C,
    -kb[1]*C**2*W/2 + kf[1]*E*MC - kb[3]*C**2*W/2 - k_degW*W
  ]
  return y0 + np.multiply(f, h)
