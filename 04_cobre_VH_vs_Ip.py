"""
Gráfica 04 - Cobre: V_H vs I_p  (B constante)
Datos: Cobre_efecto_Hall.xlsx, hoja "Campo bobina constante".

Conversiones e incertidumbres (confirmadas):
  - Lectura del voltímetro = columna "V_H (mod. amp)" [V]
  - V_H real = lectura * 1e-5 V  ->  V_H [uV] = lectura * 10
  - dI = 0.01 A,  dV_voltimetro = 0.01 V  ->  dV_H = 0.10 uV
  - B = 100 mT (fila del Excel), dB = 0.1 mT (teslámetro)
  - d (espesor Cu) = 18 um  (notas de clase)
  - R_H^teo = -0.55e-10 m^3/(A*s)  (notas, gráfica V_H vs I_p)

Ajuste (notas):  V_H = m * I_p + b0
                 m = R_H * B / d
                 R_H = m * d / B     (con B en teslas, m en V/A)

Propagación de incertidumbre (d sin error dado):
  R_H = (m * 1e-6) * d / B_T          # m está en uV/A
  dR_H = |R_H| * sqrt( (dm/m)^2 + (dB/B)^2 )

Uso:  python 04_cobre_VH_vs_Ip.py
Genera: 04_cobre_VH_vs_Ip.png
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------------------------------------------------- parámetros
B_MT = 100.0                           # mT (Excel)
DB_MT = 0.1                            # mT (teslámetro)
B_T = B_MT * 1e-3                      # T
D_CU = 18e-6                           # m
RH_TEO = -0.55e-10                     # m^3/(A*s)
FACTOR_UV = 10.0                       # V_H[uV] = lectura_amp * 1e-5 * 1e6

# ---------------------------------------------------------------- datos
# Rama I_p >= 0  (columnas A-C del Excel)
Ip_pos = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0,
                   4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0])
Vamp_pos = np.array([-0.01, -0.03, -0.12, -0.14, -0.21, -0.24, -0.28, -0.30,
                     -0.40, -0.41, -0.44, -0.46, -0.50, -0.57, -0.60, -0.61, -0.64])

# Rama I_p < 0  (columnas E-G del Excel)
Ip_neg = np.array([-0.5, -1.0, -1.5, -2.0, -2.5, -3.0, -3.5, -4.0,
                   -4.5, -5.0, -5.5, -6.0, -6.5, -7.0, -7.5, -8.0])
Vamp_neg = np.array([0.01, 0.03, 0.12, 0.14, 0.21, 0.24, 0.28, 0.30,
                     0.40, 0.41, 0.44, 0.46, 0.50, 0.57, 0.60, 0.61])

I_p = np.concatenate([Ip_pos, Ip_neg])
V_H = np.concatenate([Vamp_pos, Vamp_neg]) * FACTOR_UV   # [uV]

dI = np.full_like(I_p, 0.01)           # [A]
dVH = np.full_like(V_H, 0.10)          # [uV] = 0.01 V * 10

# ---------------------------------------------------------------- ajuste
def recta(x, m, b0):
    return m * x + b0

popt, pcov = curve_fit(recta, I_p, V_H, sigma=dVH, absolute_sigma=False)
m, b0 = popt
dm, db0 = np.sqrt(np.diag(pcov))
residuos = V_H - recta(I_p, m, b0)
ndof = len(I_p) - 2
chi2 = np.sum((residuos / dVH) ** 2)
chi2_red = chi2 / ndof
r2 = 1 - np.sum(residuos ** 2) / np.sum((V_H - np.mean(V_H)) ** 2)

# R_H y propagación: R_H = (m*1e-6) * d / B_T
m_SI = m * 1e-6                        # V/A
dm_SI = dm * 1e-6
R_H = m_SI * D_CU / B_T
# dR_H^2 = (d/B * dm)^2 + (m*d/B^2 * dB)^2
dR_H = np.sqrt((D_CU / B_T * dm_SI) ** 2
               + (m_SI * D_CU / B_T ** 2 * (DB_MT * 1e-3)) ** 2)

# --------------------------------------------------------------- proceso
print("=" * 60)
print("COBRE: V_H vs I_p  (B constante)")
print("=" * 60)
print("1) Conversiones")
print(f"   V_H [uV] = V_amp [V] * 1e-5 V * 1e6 = V_amp * 10")
print(f"   B = {B_MT} mT = {B_T} T   (dB = {DB_MT} mT)")
print(f"   d = {D_CU*1e6:.0f} um = {D_CU} m")
print(f"   N = {len(I_p)} puntos (ambas ramas de I_p)")
print()
print("2) Incertidumbres instrumentales")
print(f"   dI  = 0.01 A")
print(f"   dV_voltimetro = 0.01 V  ->  dV_H = 0.10 uV")
print(f"   dB  = 0.1 mT")
print()
print("3) Ajuste lineal  V_H = m * I_p + b0")
print(f"   m  = ({m:.4f} +/- {dm:.4f}) uV/A")
print(f"   b0 = ({b0:.3f} +/- {db0:.3f}) uV")
print(f"   R^2 = {r2:.5f}   chi2_red = {chi2_red:.2f}")
print()
print("4) Hall:  m = R_H * B / d  =>  R_H = m * d / B")
print(f"   m_SI = m * 1e-6 = {m_SI:.4e} V/A")
print(f"   R_H  = ({m_SI:.4e}) * ({D_CU}) / ({B_T})")
print(f"       = {R_H:.4e} m^3/(A*s)")
print()
print("5) Propagacion  dR_H = |R_H| * sqrt( (dm/m)^2 + (dB/B)^2 )")
print(f"   |dm/m| = {abs(dm/m):.4e}")
print(f"   |dB/B| = {DB_MT/B_MT:.4e}")
print(f"   dR_H   = {dR_H:.4e} m^3/(A*s)")
print()
print("6) Resultado")
print(f"   R_H     = ({R_H:.3e} +/- {dR_H:.1e}) m^3/(A*s)")
print(f"   R_H^teo = {RH_TEO:.3e} m^3/(A*s)")
print(f"   desvio relativo = {100*(R_H - RH_TEO)/abs(RH_TEO):.1f} %")
print("=" * 60)

# --------------------------------------------------------------- gráfica
fig, (ax, axr) = plt.subplots(2, 1, sharex=True, figsize=(8, 6),
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08})
x_fit = np.linspace(I_p.min() * 1.05, I_p.max() * 1.05, 400)

ax.errorbar(I_p, V_H, xerr=dI, yerr=dVH, fmt="o", ms=4, capsize=2,
            color="#1f4e79", ecolor="#1f4e79",
            label=f"Datos Cu ($B$ = {B_MT:.0f} mT cte.)")
ax.plot(x_fit, recta(x_fit, m, b0), "-", color="#c00000", lw=1.8,
        label="Ajuste lineal $V_H = m\\,I_p + b_0$")
ax.axhline(0, color="gray", lw=0.8)
ax.axvline(0, color="gray", lw=0.8)
ax.set_ylabel("$V_H$ ($\\mu$V)")
ax.set_title("Cobre: $V_H$ vs $I_p$  ($B$ constante)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")
ax.text(0.03, 0.05,
        f"$V_H = ({m:.3f} \\pm {dm:.3f})\\,I_p + ({b0:.2f} \\pm {db0:.2f})$\n"
        f"$m$ en $\\mu$V/A, $b_0$ en $\\mu$V\n"
        f"$R_H = m\\,d/B = ({R_H:.2e} \\pm {dR_H:.0e})$ m$^3$/(A·s)\n"
        f"$R_H^{{teo}} = {RH_TEO:.2e}$ m$^3$/(A·s),  $R^2 = {r2:.5f}$",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

axr.errorbar(I_p, residuos, xerr=dI, yerr=dVH, fmt="o", ms=4, capsize=2,
             color="#1f4e79", ecolor="#1f4e79")
axr.axhline(0, color="#c00000", lw=1.2)
axr.set_xlabel("$I_p$ (A)")
axr.set_ylabel("Residuos ($\\mu$V)")
axr.grid(True, alpha=0.3)

fig.savefig("04_cobre_VH_vs_Ip.png", dpi=300, bbox_inches="tight")
plt.show()
