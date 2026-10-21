"""
Gráfica 01 - Caracterización de la bobina: B vs I_b
Efecto Hall en metales (notas de clase, primera parte)

Datos: hoja "Caracterización" del Excel.
Se usa la componente principal del campo, "Campo y (mT)".
Las filas con I_b negativa traen |B| en el Excel, por lo que se le
devuelve el signo:  B_con_signo = signo(I_b) * Campo_y.
Campo x y Campo z no se grafican (son componentes menores).

Ajuste pedido en las notas:  B = m * I_b + b0
Incertidumbres (dadas): dI_b = 0.01 A (corriente),
dB = 0.1 mT (teslámetro).

Uso:  python 01_caracterizacion_bobina_B_vs_Ib.py
Genera: 01_caracterizacion_bobina_B_vs_Ib.png
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------------------------------------------------- datos
# I_b [A]  (en el orden del Excel: rama positiva y luego negativa)
I_b = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
                -0.05, -0.10, -0.15, -0.20, -0.25, -0.30, -0.35, -0.40, -0.45, -0.50])
# Campo y [mT] tal como está en el Excel (valor absoluto)
campo_y = np.array([19.5, 29.3, 40.1, 50.4, 60.7, 71.9, 83.8, 95.1, 107.5, 117.5,
                    18.2, 27.6, 39.1, 48.3, 60.2, 70.5, 83.6, 93.0, 105.4, 117.5])
B = np.sign(I_b) * campo_y          # B con signo [mT]

# ------------------------------------------------------- incertidumbres
dI = np.full_like(I_b, 0.01)        # [A]
dB = np.full_like(B, 0.1)           # [mT]

# ---------------------------------------------------------------- ajuste
def recta(x, m, b0):
    return m * x + b0

popt, pcov = curve_fit(recta, I_b, B, sigma=dB, absolute_sigma=False)  # errores escalados por la dispersion
m, b0 = popt
dm, db0 = np.sqrt(np.diag(pcov))
residuos = B - recta(I_b, m, b0)
chi2 = np.sum((residuos / dB) ** 2)
chi2_red = chi2 / (len(I_b) - 2)
ss_res = np.sum(residuos ** 2)
ss_tot = np.sum((B - np.mean(B)) ** 2)
r2 = 1 - ss_res / ss_tot

print(f"B = m*I_b + b0")
print(f"m  = {m:.2f} +/- {dm:.2f} mT/A")
print(f"b0 = {b0:.2f} +/- {db0:.2f} mT")
print(f"chi2_red = {chi2_red:.2f}   R^2 = {r2:.5f}")

# --------------------------------------------------------------- gráfica
fig, (ax, axr) = plt.subplots(2, 1, sharex=True, figsize=(8, 6),
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08})
x_fit = np.linspace(I_b.min() * 1.05, I_b.max() * 1.05, 400)

ax.errorbar(I_b, B, xerr=dI, yerr=dB, fmt="o", ms=5, capsize=3,
            color="#1f4e79", ecolor="#1f4e79", label="Datos (Campo y, con signo)")
ax.plot(x_fit, recta(x_fit, m, b0), "-", color="#c00000", lw=1.8,
        label="Ajuste lineal $B = m\\,I_b + b_0$")
ax.axhline(0, color="gray", lw=0.8)
ax.axvline(0, color="gray", lw=0.8)
ax.set_ylabel("$B$ (mT)")
ax.set_title("Caracterización de la bobina: $B$ vs $I_b$")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left")
ax.text(0.97, 0.05,
        f"$B = ({m:.1f} \\pm {dm:.1f})\\,I_b + ({b0:.2f} \\pm {db0:.2f})$\n"
        f"$m$ en mT/A, $b_0$ en mT\n$R^2 = {r2:.5f}$",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

axr.errorbar(I_b, residuos, xerr=dI, yerr=dB, fmt="o", ms=5, capsize=3,
             color="#1f4e79", ecolor="#1f4e79")
axr.axhline(0, color="#c00000", lw=1.2)
axr.set_xlabel("$I_b$ (A)")
axr.set_ylabel("Residuos (mT)")
axr.grid(True, alpha=0.3)

fig.savefig("01_caracterizacion_bobina_B_vs_Ib.png", dpi=300, bbox_inches="tight")
plt.show()
