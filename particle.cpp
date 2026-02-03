#ifndef PARTICLE_H
#define PARTICLE_H

#include <cmath>
#include <vector>
#include "constants.cpp"
#include "pos.cpp"
using namespace std;

class Particle {
public:
    pos position;
    double mass;
    pos velocity;
    double radius;
    double Re;
    double Cd;
    double Force;
    double norma;

    Particle() : radius(0), mass(0), Re(0), Cd(0), Force(0), norma(0) {
        position = {0, 0};
        velocity = {0, 0};
    }

    Particle(double x, double y, double Vx, double Vy) {
        this->position.x = x;
        this->position.y = y;
        this->velocity.x = Vx;
        this->velocity.y = Vy;

        this->norma = sqrt(pow(U_AIR.x - velocity.x, 2) + pow(U_AIR.y - velocity.y, 2));

        this->radius = MIN_RADIUS + (rand() % 100) / 1e6;
        this->mass = (4.0/3.0) * M_PI * pow(this->radius, 3) * RO_PAR;
    }

    void calculateReCdForce() {
        this->norma = sqrt(pow(U_AIR.x - velocity.x, 2) + pow(U_AIR.y - velocity.y, 2));

        this->Re = (2 * RO_AIR * norma * this->radius) / Myu;
        this->Cd = pow(0.325 + sqrt(0.124 + 24 / this->Re), 2);
        this->Force = M_PI*radius*radius/2 * Cd * RO_AIR * norma * norma;
    }

    vector<pos> calclulateTrajectory() {
        vector<pos> trajectory;
        pos current_position = this->position;
        pos current_velocity = this->velocity;

        for (int i = 0; i < 10; i++) {
            calculateReCdForce();
            double force = this->Force;

            // Update velocity
            current_velocity.x += (force / mass) * (U_AIR.x - current_velocity.x);
            current_velocity.y += (force / mass) * (U_AIR.y - current_velocity.y);

            // Update position
            current_position.x += current_velocity.x * 0.01; // time step
            current_position.y += current_velocity.y * 0.01;

            trajectory.push_back(current_position);
        }

        return trajectory;
    }
};

#endif