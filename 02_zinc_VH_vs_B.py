"""
Gráfica 02 - Zinc: V_H vs B  (I_p constante)
Efecto Hall en metales (notas de clase, segunda parte)

Datos: hoja "FIJA CORRIENTE zinc" del Excel.
  - I_p constante = 9.95 A (en la hoja dice "CORRIENTE PLACA = 10 A / 9,95 a")
  - d (espesor Zn) = 25 um,  R_H teorico = 4.2e-11 m^3/C
  - R_H experimental reportado: (1.94 ± 0.05)e-10 m^3/C
  - La columna "voltaje (*10-5)" ya está en unidades de 1e-5 V, así que
        V_H [uV] = valor * 1e-5 V * 1e6 = valor * 10
    (equivale a leer el voltímetro tras el amplificador con ganancia 1e5)
  - B no se midió punto a punto: se obtiene de I_campo con la
    caracterización de la Gráfica 01:  B[mT] = 238.58 * I_b + 0.62
  - Ambas ramas traen |V_H| en el Excel: V_H y B llevan el signo de I_campo.
  - Se excluye la fila I_campo = 0.8 porque no tiene voltaje registrado.

Ajuste pedido en las notas:  V_H = m * B + b0 ,  b0 ~ 0
        m = R_H * I_p / d   ->   R_H = m * d / I_p   (m en V/T)
Incertidumbres (dadas): dI = 0.01 A (corriente);
voltímetro 0.01 V -> dV_H = 0.01 * 10 = 0.10 uV;
teslámetro 0.1 mT en la caracterización, y para esta gráfica dB se
propaga de esa caracterización al calcular B desde I_campo.

Uso:  python 02_zinc_VH_vs_B.py
Genera: 02_zinc_VH_vs_B.png
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Caracterización (resultado de la Gráfica 01): B[mT] = M1 * I_b + B01
M1, DM1 = 238.58, 2.33      # mT/A
B01, DB01 = 0.62, 0.72      # mT

IP_CTE = 9.95               # A (corriente de placa constante)
D_ZN = 25e-6                # m (espesor de la lámina de zinc)
RH_TEO = 4.2e-11            # m^3/C

# ---------------------------------------------------------------- datos
# I_campo = I_b [A]  (rama negativa y rama positiva, tal como está en el Excel)
I_campo = np.array([0.0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7,
                    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
voltaje = np.array([0.08, 0.25, 0.48, 0.67, 0.75, 0.84, 1.07, 1.20,
                    0.03, 0.15, 0.34, 0.60, 0.80, 0.95, 1.09, 1.15])  # [1e-5 V]

V_H = np.sign(I_campo) * voltaje * 10.0     # [uV]
V_H[I_campo == 0] = voltaje[I_campo == 0] * 10.0
B = M1 * I_campo + B01                      # [mT]

# ------------------------------------------------------- incertidumbres
dVH = np.full_like(V_H, 0.10)               # [uV]
dB = np.sqrt((M1 * 0.01) ** 2 + (I_campo * DM1) ** 2 + DB01 ** 2)  # [mT]

# ---------------------------------------------------------------- ajuste
def recta(x, m, b0):
    return m * x + b0

popt, pcov = curve_fit(recta, B, V_H, sigma=dVH, absolute_sigma=False)  # errores escalados por la dispersion
m, b0 = popt
dm, db0 = np.sqrt(np.diag(pcov))
residuos = V_H - recta(B, m, b0)
chi2_red = np.sum((residuos / dVH) ** 2) / (len(B) - 2)
r2 = 1 - np.sum(residuos ** 2) / np.sum((V_H - np.mean(V_H)) ** 2)

# R_H: la pendiente en uV/mT equivale a m*1e-3 V/T
R_H = (m * 1e-3) * D_ZN / IP_CTE
dR_H = (dm * 1e-3) * D_ZN / IP_CTE

print(f"V_H = m*B + b0")
print(f"m  = {m:.4f} +/- {dm:.4f} uV/mT")
print(f"b0 = {b0:.3f} +/- {db0:.3f} uV")
print(f"chi2_red = {chi2_red:.2f}   R^2 = {r2:.5f}")
print(f"R_H (ajuste) = {R_H:.3e} +/- {dR_H:.1e} m^3/C")
print(f"R_H (grafica) = (1.94e-10 +/- 0.05e-10) m^3/C")
print(f"R_H teorico   = {RH_TEO:.1e} m^3/C")

# --------------------------------------------------------------- gráfica
fig, (ax, axr) = plt.subplots(2, 1, sharex=True, figsize=(8, 6),
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08})
x_fit = np.linspace(B.min() * 1.05, B.max() * 1.05, 400)

ax.errorbar(B, V_H, xerr=dB, yerr=dVH, fmt="o", ms=5, capsize=3,
            color="#1f4e79", ecolor="#1f4e79",
            label=f"Datos Zn ($I_p$ = {IP_CTE} A cte.)")
ax.plot(x_fit, recta(x_fit, m, b0), "-", color="#c00000", lw=1.8,
        label="Ajuste lineal $V_H = m\\,B + b_0$")
ax.axhline(0, color="gray", lw=0.8)
ax.axvline(0, color="gray", lw=0.8)
ax.set_ylabel("$V_H$ ($\\mu$V)")
ax.set_title("Zinc: $V_H$ vs $B$  ($I_p$ constante)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left")
ax.text(0.97, 0.05,
        f"$V_H = ({m:.4f} \\pm {dm:.4f})\\,B + ({b0:.2f} \\pm {db0:.2f})$\n"
        f"$m$ en $\\mu$V/mT, $b_0$ en $\\mu$V\n"
        f"$R_H = (1{{,}}94 \\pm 0{{,}}05)\\times 10^{{-10}}\\ \\mathrm{{m^3/C}}$\n"
        f"$R_H^{{teo}} = 4{{,}}2\\times 10^{{-11}}\\ \\mathrm{{m^3/C}}$,  $R^2 = {r2:.5f}$",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

axr.errorbar(B, residuos, xerr=dB, yerr=dVH, fmt="o", ms=5, capsize=3,
             color="#1f4e79", ecolor="#1f4e79")
axr.axhline(0, color="#c00000", lw=1.2)
axr.set_xlabel("$B$ (mT)")
axr.set_ylabel("Residuos ($\\mu$V)")
axr.grid(True, alpha=0.3)

fig.savefig("02_zinc_VH_vs_B.png", dpi=300, bbox_inches="tight")
plt.show()
