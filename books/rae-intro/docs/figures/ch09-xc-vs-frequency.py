"""
Plot capacitive reactance Xc vs frequency for a 1 nF capacitor.
Data derived from the formula Xc = 1 / (2 * pi * f * C) as used in Chapter 9.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

C = 1e-9  # 1 nF

f = np.logspace(4, 9, 500)  # 10 kHz to 1 GHz
Xc = 1 / (2 * np.pi * f * C)

# Worked-example point from the text: f = 1 MHz, Xc = 159 Ω
f_example = 1e6
Xc_example = 1 / (2 * np.pi * f_example * C)

fig, ax = plt.subplots(figsize=(7, 4))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#16213e")

ax.loglog(f, Xc, color="#00d4ff", linewidth=2, label=r"$X_C = \frac{1}{2\pi f C}$, $C = 1\,\mathrm{nF}$")
ax.plot(f_example, Xc_example, "o", color="#ff6b9d", markersize=8,
        label=f"$f = 1\\,\\mathrm{{MHz}}$, $X_C = {Xc_example:.0f}\\,\\Omega$")
ax.annotate(f"159 Ω", xy=(f_example, Xc_example),
            xytext=(f_example * 3, Xc_example * 2),
            color="#ff6b9d", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#ff6b9d", lw=1))

ax.set_xlabel("Frequency (Hz)", color="#c0c0c0")
ax.set_ylabel("Reactance $X_C$ (Ω)", color="#c0c0c0")
ax.set_title("Capacitive Reactance vs Frequency — 1 nF Capacitor", color="#f3f3f0", pad=12)

ax.tick_params(colors="#c0c0c0")
for spine in ax.spines.values():
    spine.set_edgecolor("#444")

ax.xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: {1e4: "10 kHz", 1e5: "100 kHz", 1e6: "1 MHz",
                  1e7: "10 MHz", 1e8: "100 MHz", 1e9: "1 GHz"}.get(x, "")))

ax.legend(framealpha=0.2, labelcolor="#c0c0c0", facecolor="#1a1a2e", edgecolor="#444")
ax.grid(True, which="both", color="#333", linestyle="--", linewidth=0.5)

plt.tight_layout()
plt.savefig("ch09-xc-vs-frequency.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved ch09-xc-vs-frequency.png")
