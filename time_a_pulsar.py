# %%
import astropy.units as u
import matplotlib.pyplot as plt

import pint.fitter
from pint.models import get_model_and_toas
from pint.residuals import Residuals
import pint.logging

pint.logging.setup(level="INFO")

# %%
import pint.config

parfile = "/Users/benja_n/Downloads/psr04.par"
timfile = "/Users/benja_n/Downloads/psr04.tim"

# %%
m, t_all = get_model_and_toas(parfile, timfile)
m

# %%
t_all.print_summary()

# %%
rs = Residuals(t_all, m).phase_resids
xt = t_all.get_mjds()
plt.figure()
plt.plot(xt, rs, "x")
plt.title(f"{m.PSR.value} Pre-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (phase)")
plt.grid()

# %%
error_ok = t_all.table["error"] <= 30 * u.us
t = t_all[error_ok]
t.print_summary()

# %%
rs = Residuals(t, m).phase_resids
xt = t.get_mjds()
plt.figure()
plt.plot(xt, rs, "x")
plt.title(f"{m.PSR.value} Pre-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (phase)")
plt.grid()

# %%
f = pint.fitter.Fitter.auto(t, m)
f.fit_toas()

# %%
# Print some basic params
print("Best fit has reduced chi^2 of", f.resids.chi2_reduced)
print("RMS in phase is", f.resids.phase_resids.std())
print("RMS in time is", f.resids.time_resids.std().to(u.us))

# %%
# Show the parameter correlation matrix
corm = f.get_parameter_correlation_matrix(pretty_print=True)

# %%
f.print_summary()

# %%
plt.figure()
plt.errorbar(
    xt.value,
    f.resids.time_resids.to(u.us).value,
    t.get_errors().to(u.us).value,
    fmt="x",
)
plt.title(f"{m.PSR.value} Post-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (us)")
plt.grid()

# %%
t_bad = t_all[~error_ok]
r_bad = Residuals(t_bad, f.model)
plt.figure()
plt.errorbar(
    xt.value,
    f.resids.time_resids.to(u.us).value,
    t.get_errors().to(u.us).value,
    fmt="x",
    label="used in fit",
)
plt.errorbar(
    t_bad.get_mjds().value,
    r_bad.time_resids.to(u.us).value,
    t_bad.get_errors().to(u.us).value,
    fmt="x",
    label="bad data",
)
plt.title(f"{m.PSR.value} Post-Fit Timing Residuals")
plt.xlabel("MJD")
plt.ylabel("Residual (us)")
plt.grid()
plt.legend(loc="upper left")
plt.show()

# %%
f.model.write_parfile("/tmp/output.par", "wt")
print(f.model.as_parfile())
