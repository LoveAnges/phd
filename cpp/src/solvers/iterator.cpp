#ifdef BINDINGS
#include "../etc/debug.h"
#endif

#include "../etc/globals.h"
#include "../etc/grid.h"
#include "../system/eig.h"
#include "steppers.h"
#include <iostream>

double timestep(Vecr u, Vec3r dX, int ndim, double CFL, double t, double tf,
                int count, Par &MP) {
  double MIN = 1e5;
  int ncell = u.size() / V;
  VecV q;

  for (int ind = 0; ind < ncell; ind++) {
    q = u.segment<V>(ind * V);
    for (int d = 0; d < ndim; d++)
      MIN = std::min(MIN, dX(d) / max_abs_eigs(q, d, MP));
  }

  double dt = CFL * MIN;

  if (count < 5)
    dt *= 0.2;

  if (t + dt > tf)
    return tf - t;
  else
    return dt;
}

void iterator(Vecr u, double tf, Veci3r nX, Vec3r dX, double CFL, bool PERIODIC,
              bool SPLIT, bool HALF_STEP, bool STIFF, int FLUX, Par &MP) {

  int nx = nX(0);
  int ny = nX(1);
  int nz = nX(2);
  int ndim = int(nx > 1) + int(ny > 1) + int(nz > 1);

  Vec ub(extended_dimensions(nX, N) * V);
  Vec wh(extended_dimensions(nX, 1) * int(pow(N, ndim)) * V);
  Vec qh(extended_dimensions(nX, 1) * int(pow(N, ndim + 1)) * V);

  double t = 0.;
  long count = 0;

  while (t < tf) {

    double dt = timestep(u, dX, ndim, CFL, t, tf, count, MP);
    boundaries(u, ub, ndim, nX, PERIODIC);

    if (SPLIT)
      split_stepper(u, ub, wh, ndim, nX, dt, dX, HALF_STEP, FLUX, MP);
    else
      ader_stepper(u, ub, wh, qh, ndim, nX, dt, dX, STIFF, FLUX, MP);
    t += dt;
    count += 1;

#ifdef BINDINGS
    print(int(t / tf * 100.));
#else
    std::cout << "\n" << int(t / tf * 100.);
#endif
  }
}
