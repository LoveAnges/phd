#include "../../etc/globals.h"
#include "../../system/equations.h"
#include "../evaluations.h"

void midstepper(Vecr wh, int ndim, double dt, Vec3r dX, Par &MP, bVecr mask) {
  // Steps the WENO reconstruction forwards by dt/2
  // NOTE: Only for the homogeneous system
  const int ncell = wh.size() / (int(pow(N, ndim)) * V);
  double dx = dX(0);
  double dy = dX(1);

  if (ndim == 1) {
    MatN_V F, dwdx, dFdx;
    VecV Bdwdx;

    for (int ind = 0; ind < ncell; ind += 1) {
      if (mask(ind)) {
        MatN_VMap w(wh.data() + ind * N * V, OuterStride(V));
        F.setZero(N, V);
        for (int a = 0; a < N; a++)
          flux(F.row(a), w.row(a), 0, MP);

        dwdx.noalias() = DERVALS * w / dx;
        dFdx.noalias() = DERVALS * F / dx;

        for (int a = 0; a < N; a++) {
          Bdot(Bdwdx, w.row(a), dwdx.row(a), 0, MP);
          w.row(a) -= dt / 2 * (dFdx.row(a) + Bdwdx.transpose());
        }
      }
    }
  }
  if (ndim == 2) {
    MatN2_V F, G, dwdx, dwdy, dFdx, dGdy;
    VecV Bdwdx, Bdwdy;

    for (int ind = 0; ind < ncell; ind += 1) {
      if (mask(ind)) {
        MatN2_VMap w(wh.data() + ind * N * N * V, OuterStride(V));
        F.setZero(N * N, V);
        G.setZero(N * N, V);

        for (int s = 0; s < N * N; s++) {
          flux(F.row(s), w.row(s), 0, MP);
          flux(G.row(s), w.row(s), 1, MP);
        }

        derivs2d(dwdx, w, 0);
        derivs2d(dwdy, w, 1);
        derivs2d(dFdx, F, 0);
        derivs2d(dGdy, G, 1);

        dwdx /= dx;
        dwdy /= dy;
        dFdx /= dx;
        dGdy /= dy;

        for (int s = 0; s < N * N; s++) {
          Bdot(Bdwdx, w.row(s), dwdx.row(s), 0, MP);
          Bdot(Bdwdy, w.row(s), dwdy.row(s), 1, MP);
          w.row(s) -= dt / 2 *
                      (dFdx.row(s) + dGdy.row(s) + Bdwdx.transpose() +
                       Bdwdy.transpose());
        }
      }
    }
  }
}
