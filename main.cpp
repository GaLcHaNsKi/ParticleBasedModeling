#include <iostream>
#include <vector>
#icnlude "math.h"
using namespace std;

// CONSTANTS
// AIR
const double RO_AIR = 12.3,
             U_AIR = 123.6,
             T_AIR = 300,
             P_AIR = 101321.3,
// PARTICLES
             RO_PAR = 100.3,
             U_PAR = 125.3,
             T_PAR = 301,
             AVERAGE_RADIUS = 0.0001;

// OTHER
const double Myu = 1.3,
             Re = 2 * AVERAGE_RADIUS * RO_AIR * abs (U_AIR - U_PAR) / Myu,
             Cd = pow( 0.325 + sqrt(0.124 + 24 / Re), 2);

struct pos {
    double x;
    double y;
};

class Particle {
    pos position;
    double mass;
    double velocity;

    double calculateForce() {
        return M_PI*AVERAGE_RADIUS*AVERAGE_RADIUS/2 * Cd * RO_AIR * sqrt(pow(U_AIR - this.velocity, 2)) * (U_AIR - this.velocity)
    }
};
    
vector<pos> positions;

int main() {
    
}