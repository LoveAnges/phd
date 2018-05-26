#ifndef ITERATOR_H
#define ITERATOR_H

#include "../etc/types.h"
#include "../system/objects/gpr_objects.h"

void make_u(Vecr u, std::vector<Vec> &grids, std::vector<bVec> &masks,
            std::vector<Par> &MPs);

std::vector<Vec> iterator(Vecr u, double tf, iVecr nX, aVecr dX, double CFL,
                          bool PERIODIC, bool SPLIT, bool HALF_STEP, bool STIFF,
                          int FLUX, std::vector<Par> &MPs, int nOut);

#endif // ITERATOR_H
