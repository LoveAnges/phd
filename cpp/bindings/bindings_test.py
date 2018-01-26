# Some scripts to test the Python bindings for the C++ GPR implementation
# Make sure Git/GPR-cpp and Git/GPR/python are in PYTHONPATH

from tests_1d import fluids, solids

from solver_test import weno_test, rhs_test, obj_test, dg_test
from solver_test import TAT_test, Smax_test, Bint_test
from solver_test import FVc_test, FVi_test, FV_test
from solver_test import midstepper_test, ode_test

from system_test import flux_test, source_test, block_test, Bdot_test

from options import dx


### ENSURE N,V are equal ###


u, MPs, _ = fluids.viscous_shock_IC()
MP = MPs[0]
d = 0
dt = 0.0001


F_cp, F_py = flux_test(d, MP)
S_cp, S_py = source_test(d, MP)
B_cp, B_py = block_test(d, MP)
Bx_cp, Bx_py = Bdot_test(d, MP)


wh_cp, wh_py = weno_test()

rhs_cp, rhs_py = rhs_test(u, dx, dt, MP)
obj_cp, obj_py = obj_test(u, dx, dt, MP)
qh_cp, qh_py = dg_test(u, dx, dt, MP)

TAT_cp, TAT_py = TAT_test(d, MP)
Smax_cp, Smax_py = Smax_test(d, MP)
Bint_cp, Bint_py = Bint_test(d, MP)

FVc_cp, FVc_py = FVc_test(qh_py, dx, dt, MP)
FVi_cp, FVi_py = FVi_test(qh_py, dx, dt, MP)
FV_cp, FV_py = FV_test(qh_py, dx, dt, MP)

mid_cp, mid_py = midstepper_test(u, dx, dt, MP)
ode_cp, ode_py = ode_test(dt, MP)
