from numpy import dot, eye

from gpr.misc.functions import AdevG, gram
from gpr.variables import mg
from gpr.variables.derivatives import dEdA_s, dEdJ
from gpr.variables.eos import E_2A, E_2J, E_3, E_R
from gpr.variables.shear import c_s2, dc_s2dρ


def pressure(ρ, E, v, A, J, MP, λ=None):

    E1 = E - E_3(v)

    if MP.VISCOUS:
        E1 -= E_2A(ρ, A, MP)

    if MP.THERMAL:
        E1 -= E_2J(J, MP)

    if MP.REACTIVE:
        E1 -= E_R(λ, MP)

    p = mg.pressure(ρ, E1, MP)

    return p


def temperature(ρ, p, MP):

    return mg.temperature(ρ, p, MP)


def heat_flux(T, J, MP):

    H = dEdJ(J, MP)
    return H * T


def sigma(ρ, A, MP):
    """ Returns the symmetric viscous shear stress tensor
    """
    ψ = dEdA_s(ρ, A, MP)
    return -ρ * dot(A.T, ψ)


def dsigmadA(ρ, A, MP):
    """ Returns T_ijmn = dσ_ij / dA_mn, holding ρ constant.
        NOTE: Only valid for EOS with E_2A = cs^2/4 * |devG|^2
    """
    cs2 = c_s2(ρ, MP)
    G = gram(A)
    AdevGT = AdevG(A, G).T
    GA = dot(G[:, :, None], A[:, None])
    ret = GA.swapaxes(0, 3) + GA.swapaxes(1, 3) - 2 / 3 * GA

    for i in range(3):
        ret[i, :, :, i] += AdevGT
        ret[:, i, :, i] += AdevGT

    return -ρ * cs2 * ret


def dsigmadρ(ρ, A, MP):
    """ Returns the symmetric viscous shear stress tensor
    """
    cs2 = c_s2(ρ, MP)
    dcs2dρ = dc_s2dρ(ρ, MP)
    ψ = dEdA_s(ρ, A, MP)
    return -(1 + ρ * dcs2dρ / cs2) * dot(A.T, ψ)


def Sigma(p, ρ, A, MP):
    """ Returns the total symmetric stress tensor
    """
    return p * eye(3) - sigma(ρ, A, MP)
