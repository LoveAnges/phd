#ifndef GPR_OBJECTS_H
#define GPR_OBJECTS_H

#include "../../../include/eigen3/Eigen"


typedef Eigen::Matrix<double, 2, 2, Eigen::RowMajor> Mat2_2;
typedef Eigen::Matrix<double, 3, 3, Eigen::RowMajor> Mat3_3;
typedef Eigen::Matrix<double, 4, 4, Eigen::RowMajor> Mat4_4;

typedef Eigen::Ref<Mat2_2> Mat2_2r;
typedef Eigen::Ref<Mat3_3> Mat3_3r;
typedef Eigen::Ref<Mat4_4> Mat4_4r;

typedef Eigen::Matrix<double, 3, 1> Vec3;
typedef Eigen::Matrix<double, 9, 1> Vec9;

typedef Eigen::Ref<Vec3> Vec3r;
typedef Eigen::Ref<Vec9> Vec9r;

typedef Eigen::Map<Mat3_3, 0, Eigen::OuterStride<3> > Mat3_3Map;
typedef Eigen::Map<Vec3, 0, Eigen::InnerStride<1> > Vec3Map;


struct Par
{
    double gamma;
    double cv;
    double pinf;

    double r0;
    double p0;
    double T0;

    double cs2;
    double mu;
    double tau1;
    double Pr;

    double alpha2;
    double kappa;
    double tau2;
};


#endif // GPR_OBJECTS_H
