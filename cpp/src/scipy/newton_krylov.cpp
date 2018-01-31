#include "newton_krylov.h"
#include "../etc/debug.h"
#include "../etc/globals.h"
#include "lgmres.h"

double maxnorm(Vecr x) { return x.lpNorm<Eigen::Infinity>(); }

void KrylovJacobian::update_diff_step() {
  double mx = maxnorm(x0);
  double mf = maxnorm(f0);
  omega = rdiff * std::max(1., mx) / std::max(1., mf);
}

KrylovJacobian::KrylovJacobian(Vecr x, Vecr f, VecFunc F) {
  func = F;
  maxiter = 1;
  inner_m = 30;
  outer_k = 10;

  x0 = x;
  f0 = f;
  rdiff = std::pow(mEPS, 0.5);
  update_diff_step();
  outer_v = std::vector<Vec>(0);

  int n = x.size();
  M = Mat::Identity(n, n);
}

Vec KrylovJacobian::matvec(Vecr v) {
  double nv = v.norm();
  if (nv == 0.)
    return 0. * v;
  double sc = omega / nv;
  Vec tmp = x0 + sc * v;
  return (func(tmp) - f0) / sc;
}

Vec KrylovJacobian::psolve(Vecr v) { return M * v; }

void KrylovJacobian::solve(Vecr rhs, double tol, Vecr dx) {

  Vec x0 = 0. * rhs;
  using std::placeholders::_1;
  VecFunc mvec = std::bind(&KrylovJacobian::matvec, *this, _1);
  VecFunc psol = std::bind(&KrylovJacobian::psolve, *this, _1);

  dx = -lgmres(mvec, psol, rhs, x0, outer_v, tol, maxiter, inner_m, outer_k);
}

void KrylovJacobian::update(Vecr x, Vecr f) {
  x0 = x;
  f0 = f;
  update_diff_step();
}

TerminationCondition::TerminationCondition(double ftol, double frtol,
                                           double xtol, double xrtol) {
  x_tol = xtol;
  x_rtol = xrtol;
  f_tol = ftol;
  f_rtol = frtol;
  f0_norm = 0.;
}

bool TerminationCondition::check(Vecr f, Vecr x, Vecr dx) {
  double f_norm = maxnorm(f);
  double x_norm = maxnorm(x);
  double dx_norm = maxnorm(dx);

  if (f0_norm == 0.)
    f0_norm = f_norm;

  if (f_norm == 0.)
    return true;

  return f_norm <= f_tol && f_norm / f_rtol <= f0_norm && dx_norm <= x_tol &&
         dx_norm / x_rtol <= x_norm;
}

void _nonlin_line_search(VecFunc func, Vecr x, Vecr Fx, Vecr dx) {

  x += dx;
  Fx = func(x);
}

Vec nonlin_solve(VecFunc F, Vecr x, double f_tol, double f_rtol, double x_tol,
                 double x_rtol) {

  TerminationCondition condition(f_tol, f_rtol, x_tol, x_rtol);

  const double gamma = 0.9;
  const double eta_max = 0.9999;
  const double eta_treshold = 0.1;
  double eta = 1e-3;

  Vec dx = INF * Vec::Ones(x.size());
  Vec Fx = F(x);
  double Fx_norm = Fx.norm();

  KrylovJacobian jacobian(x, Fx, F);

  int maxiter = 100 * (x.size() + 1);

  for (int n = 0; n < maxiter; n++) {

    if (condition.check(Fx, x, dx))
      break;

    double tol = std::min(eta, eta * Fx_norm);
    jacobian.solve(Fx, tol, dx);

    _nonlin_line_search(F, x, Fx, dx);
    double Fx_norm_new = Fx.norm();

    jacobian.update(x, Fx);

    double eta_A = gamma * Fx_norm_new * Fx_norm_new / (Fx_norm * Fx_norm);
    if (gamma * eta * eta < eta_treshold)
      eta = std::min(eta_max, eta_A);
    else
      eta = std::min(eta_max, std::max(eta_A, gamma * eta * eta));

    Fx_norm = Fx_norm_new;
  }
  return x;
}
