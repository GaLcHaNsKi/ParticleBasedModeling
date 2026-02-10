#ifndef CONSTANTS_H
#define CONSTANTS_H

#include "pos.cpp"
#include <cmath>
#include <cstdlib>

#ifndef U_FUNCTION
#define U_FUNCTION 1
#endif

// CONSTANTS
// AIR
const double RO_AIR = 1.225, // in kg/m^3
             T_AIR = 273+15, // in Kelvin
             P_AIR = 101325000, // in Pa
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

#endif
