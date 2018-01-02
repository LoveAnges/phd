from time import time

from joblib import Parallel
from numpy import array, zeros

from etc import boundaries
from tests_1d import fluids, solids, multi, toro
from tests_2d import validation
from system.gpr.misc.plot import *

from etc.iterator import timestep, make_u
from etc.save import Data, print_stats, save_all
from solvers.solvers import ader_stepper, split_stepper
from multi.gfm import add_ghost_cells
from options import nx, ny, nz, nV, dx, dy, dz, ndim, N1, tf
from options import NCORE, RGFM, SPLIT, USE_CPP, STRANG, HALF_STEP, PERRON_FROB


### CHECK ARGUMENTS ###
IC = solids.elastic2_IC
BC = boundaries.standard_BC


u, PARs = IC()
data = [Data(u, 0)]
m = len(PARs)

pool = Parallel(n_jobs=NCORE)


if USE_CPP:
    import GPRpy
    from system.gpr.misc.objects import CParameters
    extDims = GPRpy.solvers.extended_dimensions(nx, ny, nz)
    ub = zeros(extDims * nV);
    wh = zeros(extDims * int(pow(N1,ndim)) * nV);
    qh = zeros(extDims * int(pow(N1,ndim+1)) * nV);
    cPARs = [CParameters(GPRpy, PAR) for PAR in PARs]


def main(t, tf, count, data):

    tStart = time()
    u = data[count].grid

    while t < tf:

        t0 = time()

        mats = array([u for i in range(m)])
        dt = timestep(mats, count, t, tf, PARs)

        if RGFM:
            add_ghost_cells(mats, PARs, dt)

        print_stats(count, t, dt)

        for i in range(m):

            mat = mats[i]

            if USE_CPP:
                tmp = mat.ravel()
                MP = cPARs[i]

                if SPLIT:
                    GPRpy.solvers.split_stepper(tmp, ub, wh, ndim, nx, ny, nz,
                                                dt, dx, dy, dz, False,
                                                bool(STRANG), bool(HALF_STEP),
                                                bool(PERRON_FROB), MP)
                else:
                    GPRpy.solvers.ader_stepper(tmp, ub, wh, qh, ndim, nx, ny, nz,
                                               dt, dx, dy, dz, False,
                                               bool(PERRON_FROB), MP)

                mat = tmp.reshape([nx,ny,nz,nV])

            else:
                PAR = PARs[i]

                if SPLIT:
                    split_stepper(pool, mat, BC, dt, PAR)
                else:
                    ader_stepper(pool, mat, BC, dt, PAR)

        u = make_u(mats)
        data.append(Data(u, t))

        if RGFM:
            # reinitialize level sets
            pass

        t += dt
        count += 1
        print('Total Time:', time()-t0, '\n')

    print('TOTAL RUNTIME:', time()-tStart)

if __name__ == "__main__":
    main(0, tf, 0, data)
    save_all(data)
