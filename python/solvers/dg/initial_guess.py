from itertools import product

from numpy import arange, array, dot, zeros
from scipy.optimize import newton_krylov

from etc.grids import flat_index
from solvers.basis import DERVALS
from system import source, system
from options import N, NT, NV, NDIM, N_K_IG, DG_TOL


def standard_initial_guess(w):
    """ Returns a Galerkin intial guess consisting of the value of q at t=0
    """
    ret = array([w for i in range(N)])
    return ret.reshape([NT, NV])


def stiff_initial_guess(w, dtGAPS, dX, MP):
    """ Returns an initial guess based on the underlying equations
    """
    q = zeros([N] * (NDIM + 1) + [NV])
    qt = w.reshape([N] * NDIM + [NV])
    coordList = [arange(N)] * NDIM

    for t in range(N):

        dt = dtGAPS[t]

        # loop over the coordinates of each spatial node
        for coords in product(*coordList):

            q_ = qt[coords]     # the value of q at the current spatial node

            # qi[d] holds the coefficients at the nodes lying in a strip in the
            # dth direction, at the current spatial node
            qi = []
            for d in range(NDIM):
                i = flat_index(coords[:d])
                j = flat_index(coords[d + 1:])
                qi.append(qt.reshape([N**d, N, N**(NDIM - d - 1), NV])[i, :, j])

            Mdqdx = zeros(NV)
            for d in range(NDIM):
                dqdxi = dot(DERVALS[coords[d]], qi[d])
                Mdqdx += dot(system(q_, d, MP), dqdxi) / dX[d]

            S = source(q_, MP)

            if N_K_IG:
                def f(X): return X - q_ + dt * (Mdqdx - (S + source(X, MP)) / 2)
                q[(t,) + coords] = newton_krylov(f, q_, f_tol=DG_TOL)
            else:
                q[(t,) + coords] = q_ - dt * (Mdqdx - S)

        qt = q[t]

    return q.reshape([NT, NV])
