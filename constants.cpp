#ifndef CONSTANTS_H
#define CONSTANTS_H

#include "structures.cpp"
#include <cmath>
#include <cstdlib>

#ifndef U_FUNCTION
#define U_FUNCTION 1
#endif

// CONSTANTS
// AIR
const double RO_AIR = 1.225, // in kg/m^3
             Myu = 1.75*1e-5, // in Pa*s
// PARTICLES
             RO_PAR = 2500.3, // in kg/m^3
             T_PAR = 273+15, // in Kelvin
             MIN_RADIUS = 0.00005; // in meters

// WIND FIELD FUNCTIONS

#if U_FUNCTION == 1
    // CONSTANT WIND FIELD
    pos U_AIR(double x, double y) {
        return {10.0, 5.0};
    }; // in m/s
#endif

#if U_FUNCTION == 2
    // VARIABLE WIND FIELD #1
    pos U_AIR(double x, double y) {
        double Ux = 5 + y*sin(y*M_PI) + exp(-0.1*x);
        double Uy = 8 + 0.3 * x*sin(y*M_PI);

        return {Ux, Uy};
    };
#endif

#if U_FUNCTION == 3
    // VARIABLE WIND FIELD #2
    pos U_AIR(double x, double y) {
        double Ux = x * cos(y*M_PI/2) + y + 5;
        double Uy = 10*sin(y*M_PI/2);

        return {Ux, Uy};
    };
#endif

#if U_FUNCTION == 4
    // VARIABLE WIND FIELD #3
    pos U_AIR(double x, double y) {
        double Ux = -sqrt(x*x + y*y) * y;
        double Uy = sqrt(x*x + y*y) * x;

        return {Ux, Uy};
    };
#endif

#if U_FUNCTION == 5
    // VARIABLE WIND FIELD #4
    pos U_AIR(double x, double y) {
        double Ux = x/30 * cos(y/30*M_PI/2) + y/30 + 5;
        double Uy = 10*sin(y/30*M_PI/2);

        return {Ux, Uy};
    };
#endif

#if U_FUNCTION == 6
// Скорость уменьшается с расстоянием от источника
pos U_AIR(double x, double y) {
    double x0 = 0, y0 = 0;

    double dx = x - x0;
    double dy = y - y0;

    double r = sqrt(dx*dx + dy*dy) + 1e-6;

    double k = 50.0; // сила источника

    double Ux = k * dx / (r*r);
    double Uy = k * dy / (r*r);

    return {Ux, Uy};
}
#endif

#if U_FUNCTION == 7
// Скорость увеличивается с расстоянием от источника
pos U_AIR(double x, double y) {
    double x0 = 0, y0 = 0;

    double dx = x - x0;
    double dy = y - y0;

    double r = sqrt(dx*dx + dy*dy) + 1e-6;

    double k = 0.5;

    double Ux = k * dx;
    double Uy = k * dy;

    return {Ux, Uy};
}
#endif

#if U_FUNCTION == 8
// Постоянная скорость в радиальном направлении от источника
pos U_AIR(double x, double y) {
    double x0 = 0, y0 = 0;

    double dx = x - x0;
    double dy = y - y0;

    double r = sqrt(dx*dx + dy*dy) + 1e-6;

    double V = 10.0;

    double Ux = V * dx / r;
    double Uy = V * dy / r;

    return {Ux, Uy};
}
#endif

#if U_FUNCTION == 9
// Вихревой поток вокруг источника
pos U_AIR(double x, double y) {
    double dx = x, dy = y;
    double r = sqrt(dx*dx + dy*dy) + 1e-6;

    double Vr = 8.0;   // радиальная скорость
    double Vt = 5.0;   // вращение

    double urx = dx / r, ury = dy / r;
    double utx = -dy / r, uty = dx / r;

    return {Vr*urx + Vt*utx, Vr*ury + Vt*uty};
}
#endif

#if U_FUNCTION == 10
// Два источника скорости
pos U_AIR(double x, double y) {
    auto src = [](double x, double y, double x0, double y0, double k){
        double dx = x - x0, dy = y - y0;
        double r = sqrt(dx*dx + dy*dy) + 1e-6;
        return pos{k * dx/(r*r), k * dy/(r*r)};
    };

    pos a = src(x,y, -10, 0, 40.0);
    pos b = src(x,y,  10, 0, 40.0);

    return {a.x + b.x, a.y + b.y};
}
#endif

#endif
