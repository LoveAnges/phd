from numpy import amax, concatenate, dot, zeros
from scipy.linalg import solve, inv

from gpr.eig import primitive_eigs
#from gpr.matrices.primitive import source_primitive_reordered
from gpr.variables.state import heat_flux, sigma, sigma_A
from gpr.variables.vectors import primitive, primitive_vector, Pvec_reordered_to_Cvec
from options import dx


starTOL = 1e-8
FIX_Q = 0


def check_star_convergence(QL_, QR_, PARL, PARR):

    PL_ = primitive(QL_, PARL)
    PR_ = primitive(QR_, PARR)
    σL_ = sigma(PL_.ρ, PL_.A, PARL.cs2)[0]
    σR_ = sigma(PR_.ρ, PR_.A, PARR.cs2)[0]
    qL_ = heat_flux(PL_.T, PL_.J, PARL.α2)[0]
    qR_ = heat_flux(PR_.T, PR_.J, PARR.α2)[0]

    return amax(abs(σL_-σR_)) < starTOL and abs(qL_-qR_) < starTOL

def riemann_constraints(P, sgn, PAR):

    _, Lhat, _ = primitive_eigs(P, PAR)
    ρ = P.ρ; p = P.p; A = P.A
    pINF = PAR.pINF; cs2 = PAR.cs2; α2 = PAR.α2

    q0 = heat_flux(P.T, P.J, α2)[0]
    σ0 = sigma(ρ, A, cs2)[0]
    dσdA = sigma_A(ρ, A, cs2)[0]
    Π1 = dσdA[:,:,0]
    Π2 = dσdA[:,:,1]
    Π3 = dσdA[:,:,2]

    Lhat[:4] = 0
    Lhat[0, 0] = -q0 / ρ
    Lhat[0, 1] = q0 / (p + pINF)
    Lhat[0, 14] = α2 * P.T
    Lhat[1:4, 0] = σ0 / ρ
    Lhat[1:4, 2:5] = Π1
    Lhat[1:4, 5:8] = Π2
    Lhat[1:4, 8:11] = Π3
    Lhat[4:8, 11:15] *= sgn

    return Lhat, inv(Lhat)

def star_stepper(QL, QR, dt, PARL, PARR, SL=zeros(18), SR=zeros(18)):

    PL = primitive(QL, PARL)
    PR = primitive(QR, PARR)
    LL, RL = riemann_constraints(PL, -1, PARL)
    LR, RR = riemann_constraints(PR, 1, PARR)

    ΘL = zeros([4, 4])
    ΘR = zeros([4, 4])
    ΘL[0] = RL[1,:4]
    ΘL[1:4] = RL[11:14, :4]
    ΘR[0] = RR[1,:4]
    ΘR[1:4] = RR[11:14, :4]

    σL = sigma(PL.ρ, PL.A, PARL.cs2)[0]
    σR = sigma(PR.ρ, PR.A, PARR.cs2)[0]
    qL = heat_flux(PL.T, PL.J, PARL.α2)[0]
    qR = heat_flux(PR.T, PR.J, PARR.α2)[0]
    xL = concatenate([[qL], σL])
    xR = concatenate([[qR], σR])

    if FIX_Q:
        q_ = 2 * (PL.T - PR.T) / (10 * dx * (1/PARL.κ + 1/PARR.κ))
        b = PR.v - PL.v + ΘR[1:4,0] * (q_ - qR) - ΘL[1:4,0] * (q_ - qL)
        b -= (dot(ΘR[1:4,1:], σR) - dot(ΘL[1:4,1:], σL))
        M = (ΘL - ΘR)[1:,1:]
        x_ = concatenate([[q_], solve(M, b)])
    else:
        yL = concatenate([[PL.p], PL.v])
        yR = concatenate([[PR.p], PR.v])
        x_ = solve(ΘL-ΘR, yR-yL + dot(ΘL, xL) - dot(ΘR, xR))

    cL = zeros(18)
    cR = zeros(18)
    cL[:4] = x_ - xL
    cR[:4] = x_ - xR

    PLvec = primitive_vector(PL)
    PRvec = primitive_vector(PR)
    PL_vec = solve(LL, cL) + PLvec + dt*SL          # NOTE: Maybe incorrect, as LL,LR are calculated
    PR_vec = solve(LR, cR) + PRvec + dt*SR          # using reordered primitive variables
    QL_ = Pvec_reordered_to_Cvec(PL_vec, PARL)
    QR_ = Pvec_reordered_to_Cvec(PR_vec, PARR)
    return QL_, QR_

def star_states(QL, QR, dt, PARL, PARR):
#    LL, RL = riemann_constraints(QL, -1, PARL)
#    LR, RR = riemann_constraints(QR, 1, PARR)
#    SL = source_primitive_reordered(QL, PARL)
#    SR = source_primitive_reordered(QR, PARR)
    QL_, QR_ = star_stepper(QL, QR, dt, PARL, PARR)
    while not check_star_convergence(QL_, QR_, PARL, PARR):
        QL_, QR_ = star_stepper(QL_, QR_, dt, PARL, PARR)
    return QL_, QR_
