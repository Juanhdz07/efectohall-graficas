"""
Gráfica 03 - Zinc: V_H vs I_p  (B constante)
Efecto Hall en metales (notas de clase, segunda parte)

Datos: hoja "fija corriente campo zinc" del Excel.
  - Corriente de campo fija I_b = 0.43 A ("corriente fija de 0,43 A")
  - B constante se calcula con la caracterización de la Gráfica 01:
        B = 238.58 * 0.43 + 0.62 = 103.2 mT
    (las notas traen B cte = 250 mT como valor de referencia del montaje;
     aquí se usa el B que sale de SUS datos de caracterización)
  - d (espesor Zn) = 2.5 um,  R_H teorico (notas) = 4.00e-11 m^3/(A*s)
  - La columna "voltaje" se convierte igual que en las demás hojas:
        V_H = valor * 1e-5 V  ->  V_H [uV] = valor * 10
  - La rama de I_p negativa trae |V_H|: V_H lleva el signo de I_p.

Ajuste pedido en las notas:  V_H = m * I_p + b0
        m = R_H * B / d   ->   R_H = m * d / B   (m en V/A, B en T)
Incertidumbres (dadas): dI_p = 0.01 A (corriente);
voltímetro 0.01 V -> dV_H = 0.01 * 10 = 0.10 uV;
teslámetro 0.1 mT (en la caracterización usada para B).

Uso:  python 03_zinc_VH_vs_Ip.py
Genera: 03_zinc_VH_vs_Ip.png
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Caracterización (Gráfica 01) y parámetros de esta gráfica
M1, B01 = 238.58, 0.62                 # B[mT] = M1 * I_b + B01
IB_FIJA = 0.43                         # A
B_CTE_MT = M1 * IB_FIJA + B01          # 103.2 mT
B_CTE_T = B_CTE_MT * 1e-3              # T
D_ZN = 2.5e-6                          # m
RH_TEO = 4.00e-11                      # m^3/(A*s), notas de clase
FACTOR_UV = 10.0                       # V_H[uV] = valor*1e-5 V * 1e6

# ---------------------------------------------------------------- datos
I_p = np.array([0.0, 0.40, 0.98, 1.30, 1.79, 2.38, 3.07,
                0.0, -0.50, -1.02, -1.59, -2.15, -2.73, -3.65])       # [A]
voltaje = np.array([0.15, 1.43, 3.20, 4.12, 5.67, 7.24, 9.36,
                    0.18, 1.67, 3.21, 4.95, 6.83, 8.49, 11.11])       # x1e-5 V

V_H = np.sign(I_p) * voltaje * FACTOR_UV
V_H[I_p == 0] = voltaje[I_p == 0] * FACTOR_UV

# ------------------------------------------------------- incertidumbres
dI = np.full_like(I_p, 0.01)           # [A]
dVH = np.full_like(V_H, 0.10)          # [uV]

# ---------------------------------------------------------------- ajuste
def recta(x, m, b0):
    return m * x + b0

popt, pcov = curve_fit(recta, I_p, V_H, sigma=dVH, absolute_sigma=False)  # errores escalados por la dispersion
m, b0 = popt
dm, db0 = np.sqrt(np.diag(pcov))
residuos = V_H - recta(I_p, m, b0)
chi2_red = np.sum((residuos / dVH) ** 2) / (len(I_p) - 2)
r2 = 1 - np.sum(residuos ** 2) / np.sum((V_H - np.mean(V_H)) ** 2)

# R_H: la pendiente en uV/A equivale a m*1e-6 V/A
R_H = (m * 1e-6) * D_ZN / B_CTE_T
dR_H = (dm * 1e-6) * D_ZN / B_CTE_T

print(f"B constante = {B_CTE_MT:.1f} mT  (I_b = {IB_FIJA} A)")
print(f"V_H = m*I_p + b0")
print(f"m  = {m:.4f} +/- {dm:.4f} uV/A")
print(f"b0 = {b0:.3f} +/- {db0:.3f} uV")
print(f"chi2_red = {chi2_red:.2f}   R^2 = {r2:.5f}")
print(f"R_H = {R_H:.3e} +/- {dR_H:.1e} m^3/(A*s)   (teorico: {RH_TEO:.3e})")

# --------------------------------------------------------------- gráfica
fig, (ax, axr) = plt.subplots(2, 1, sharex=True, figsize=(8, 6),
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08})
x_fit = np.linspace(I_p.min() * 1.05, I_p.max() * 1.05, 400)

ax.errorbar(I_p, V_H, xerr=dI, yerr=dVH, fmt="o", ms=5, capsize=3,
            color="#1f4e79", ecolor="#1f4e79",
            label=f"Datos Zn ($B$ = {B_CTE_MT:.0f} mT cte.)")
ax.plot(x_fit, recta(x_fit, m, b0), "-", color="#c00000", lw=1.8,
        label="Ajuste lineal $V_H = m\\,I_p + b_0$")
ax.axhline(0, color="gray", lw=0.8)
ax.axvline(0, color="gray", lw=0.8)
ax.set_ylabel("$V_H$ ($\\mu$V)")
ax.set_title("Zinc: $V_H$ vs $I_p$  ($B$ constante)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left")
ax.text(0.97, 0.05,
        f"$V_H = ({m:.3f} \\pm {dm:.3f})\\,I_p + ({b0:.2f} \\pm {db0:.2f})$\n"
        f"$m$ en $\\mu$V/A, $b_0$ en $\\mu$V\n"
        f"$R_H = m\\,d/B = ({R_H:.2e} \\pm {dR_H:.0e})$ m$^3$/(A·s)\n"
        f"$R_H^{{teo}} = {RH_TEO:.2e}$ m$^3$/(A·s),  $R^2 = {r2:.5f}$",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

axr.errorbar(I_p, residuos, xerr=dI, yerr=dVH, fmt="o", ms=5, capsize=3,
             color="#1f4e79", ecolor="#1f4e79")
axr.axhline(0, color="#c00000", lw=1.2)
axr.set_xlabel("$I_p$ (A)")
axr.set_ylabel("Residuos ($\\mu$V)")
axr.grid(True, alpha=0.3)

fig.savefig("03_zinc_VH_vs_Ip.png", dpi=300, bbox_inches="tight")
plt.show()
