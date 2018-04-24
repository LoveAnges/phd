from numpy import array, zeros

from gpr.tests.one.fluids import fluids_IC
from gpr.tests.one.params import MP_Air_ND


def toro1_IC():

    tf = 0.25
    nx = 200
    Lx = 1

    dX = [Lx / nx]

    ρL = 1
    pL = 1
    vL = zeros(3)

    ρR = 0.125
    pR = 0.1
    vR = zeros(3)

    return fluids_IC(tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MP_Air_ND)


def toro2_IC():

    tf = 0.15
    nx = 200
    Lx = 1

    dX = [Lx / nx]

    ρL = 1
    pL = 0.4
    vL = array([-2, 0, 0])

    ρR = 1
    pR = 0.4
    vR = array([2, 0, 0])

    return fluids_IC(tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MP_Air_ND)


def toro3_IC():

    tf = 0.012
    nx = 200
    Lx = 1

    dX = [Lx / nx]

    ρL = 1
    pL = 1000
    vL = zeros(3)

    ρR = 1
    pR = 0.01
    vR = zeros(3)

    return fluids_IC(tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MP_Air_ND)


def toro4_IC():

    tf = 0.035
    nx = 200
    Lx = 1

    dX = [Lx / nx]

    ρL = 1
    pL = 0.01
    vL = zeros(3)

    ρR = 1
    pR = 100
    vR = zeros(3)

    return fluids_IC(tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MP_Air_ND)


def toro_test5_IC():

    tf = 0.035
    nx = 200
    Lx = 1

    dX = [Lx / nx]

    ρL = 5.99924
    pL = 460.894
    vL = array([19.5975, 0, 0])

    ρR = 5.99242
    pR = 46.095
    vR = array([-6.19633, 0, 0])

    return fluids_IC(tf, nx, dX, ρL, pL, vL, ρR, pR, vR, MP_Air_ND)
