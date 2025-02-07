import astropy.units as u
import matplotlib.pyplot as plt
import pint.fitter
from pint.models import get_model_and_toas
from pint.residuals import Residuals

import pint.logging
pint.logging.setup(level="INFO")

import pint.config
parfile = "/Users/benja_n/Downloads/psr04.par"
timfile = "/Users/benja_n/Downloads/psr04.tim"

# Cargar el modelo y los TOAs
m, t_all = get_model_and_toas(parfile, timfile)

# Verificar si hay datos de TOAs
if len(t_all.get_mjds()) > 0:
    t_all.print_summary()
else:
    print("No hay datos de TOAs disponibles.")
    exit()  # Salir si no hay datos disponibles

# Calcular y graficar los residuos
rs = Residuals(t_all, m).phase_resids
xt = t_all.get_mjds()
plt.figure()
plt.plot(xt, rs, "x")
plt.title(f"{m.PSR.value} Pre-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (phase)")
plt.grid()
plt.show()

# Filtrar TOAs con error <= 30 microsegundos
error_ok = t_all.table["error"] <= 30 * u.us
t = t_all[error_ok]

# Verificar si hay TOAs válidos después del filtrado
print(f"TOAs después del filtrado: {len(t)}")
if len(t) == 0:
    print("No hay TOAs válidos después del filtrado.")
    exit()  # Salir si no hay TOAs válidos

# Imprimir el resumen de TOAs válidos
if len(t.table) > 0:
    t.print_summary()
else:
    print("La tabla de TOAs está vacía después del filtrado.")
    exit()  # Salir si la tabla está vacía

# Calcular y graficar los residuos para los TOAs válidos
rs = Residuals(t, m).phase_resids
xt = t.get_mjds()
plt.figure()
plt.plot(xt, rs, "x")
plt.title(f"{m.PSR.value} Pre-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (phase)")
plt.grid()
plt.show()

# Ajuste de parámetros con el Fitter
f = pint.fitter.Fitter.auto(t, m)
f.fit_toas()
