from numpy import eye, zeros


def riemann_IC(sys, tf, nx, dX, QL, QR, MPL, MPR, x0):

    if MPR is not None:

        n = len(QL)
        u = zeros([nx, n + 1])
        MPs = [MPL, MPR]

        for i in range(nx):

            if i * dX[0] < x0:
                u[i, :n] = QL
            else:
                u[i, :n] = QR

            u[i, -1] = (i + 0.5) * dX[0] - x0

    else:

        u = zeros([nx, len(QL)])
        MPs = [MPL]

        for i in range(nx):

            if i * dX[0] < x0:
                u[i] = QL
            else:
                u[i] = QR

    return u, MPs, tf, dX, sys


def fluids_IC(sys, tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MPL, MPR=None, x0=0.5):
    """ constructs the riemann problem corresponding to the parameters given
    """
    if MPR is None:
        MPR_ = MPL
    else:
        MPR_ = MPR

    AL = (ρL / MPL.ρ0)**(1 / 3) * eye(3)
    JL = zeros(3)
    QL = sys.Cvec(ρL, pL, vL, AL, JL, MPL)

    AR = (ρR / MPR_.ρ0)**(1 / 3) * eye(3)
    JR = zeros(3)
    QR = sys.Cvec(ρR, pR, vR, AR, JR, MPR_)

    return riemann_IC(sys, tf, nx, dX, QL, QR, MPL, MPR, x0)
