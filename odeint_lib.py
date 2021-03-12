from scipy.integrate import odeint

def chem_sys(y, k_f, k_b, k_d):
  M, E, C, V, W, H, S, N, F = y
  dydt = [-k_f[0] + (k_b[0] * C**2 * V**2)/4 + k_d,
  -k_f[0] + (k_b[0] * C**2 * V**2)/4 + k_d,
  -k_f[0]*E*M*C + k_b[0]*C**2*V**2/4 - 2*k_b[0]*C**2*V**2/4 + 2*k_f[0]*E*M*C - k_f[1]*C*H + k_b[1]*H*W - k_f[3]*C*V**2/2 - k_f[4]*C*W**2/2 - k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S,
  -2*k_b[0]*C**2*V**2/4 + 2*k_f[0]*E*M*C - 2*k_f[2]*C*H*V**2/2 + 2*k_b[2]*C*H**2*W**2/4 - 2*k_f[3]*C*V**2/2 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S,
  -k_b[1]*H*W + k_f[1]*C*H - 2*k_b[2]*C*H**2*W**2/4 + 2*k_f[2]*C*H*V**2/2 - 2*k_f[4]**C*W**2/2,
  -k_f[2]*C*H*V**2/2 + k_b[2]*C*H**2*W**2/4 - 2*k_b[2]*C*H**2*W**2/4 + 2*k_f[2]*C*H*V**2/2 - k_f[5]*H,
  -k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 + k_d,
  -k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 + k_d,
  -k_f[6]*S - k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S + k_d]
  return dydt

k_f = [0.61, 0.006, 0.37, 0.006, 0.02, 0.0001, 0.99]
k_b = [4.7e-63, 0.006, 1.5e-41, None, None, None, None, 9.6e-67]
k_d = 0.04

y0 = [1,1,1,1,1,1,1,1,1]