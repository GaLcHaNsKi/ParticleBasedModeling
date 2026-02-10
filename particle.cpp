#ifndef PARTICLE_H
#define PARTICLE_H


#ifndef STEPS
#define STEPS 1500
#endif

#include <cmath>
#include <vector>
#include "constants.cpp"
#include "pos.cpp"
#include <array>
#include <boost/numeric/odeint.hpp>

using namespace boost::numeric::odeint;
using namespace std;
using state_type = std::array<double, 4>;

class Particle {
public:
    pos position;
    double mass;
    pos velocity;
    double radius;
    double Re;
    double Cd;
    double norma;

    Particle() : radius(0), mass(0), Re(0), Cd(0), norma(0) {
        position = {0, 0};
        velocity = {0, 0};
    }

    Particle(double x, double y, double Vx, double Vy) {
        this->position.x = x;
        this->position.y = y;
        this->velocity.x = Vx;
        this->velocity.y = Vy;

        this->radius = MIN_RADIUS + (rand() % 100) / 1e6;
        this->mass = (4.0/3.0) * M_PI * pow(this->radius, 3) * RO_PAR;
    }

    void calculateReCdForce() {
    }

    void particleSystem(const state_type &y, state_type &dydt, double t) {
        // y = { qx, qy, vx, vy }

        double qx = y[0];
        double qy = y[1];
        double vx = y[2];
        double vy = y[3];

        auto [ ux, uy ] = U_AIR(qx, qy);

        norma = sqrt(pow(ux - vx, 2) + pow(uy - vy, 2));
        Re = (2 * RO_AIR * norma * radius) / Myu;
        Cd = pow(0.325 + sqrt(0.124 + 24 / Re), 2);

        double K = M_PI*radius*radius/2 * Cd * RO_AIR / mass;
        dydt[0] = vx;
        dydt[1] = vy;
        dydt[2] = K * norma * (ux - vx);
        dydt[3] = K * norma * (uy - vy);
    }

    pair<vector<pos>, vector<pos>> calclulateTrajectory() {
        vector<pos> trajectory;
        vector<pos> velocities;
        pos current_position = this->position;
        pos current_velocity = this->velocity;

        // Calculating with RK4
        runge_kutta4<state_type> stepper;
        state_type y = {position.x, position.y, velocity.x, velocity.y};

        double t  = 0.0;
        double dt = 1e-3;
        
        for (size_t i = 0; i < STEPS; ++i) {
            stepper.do_step(
                [this](const state_type &y, state_type &dydt, double t) {
                    this->particleSystem(y, dydt, t);
                },
                y, t, dt
            );
            t += dt;

            // printf("Time: %f, Position: (%f, %f), Velocity: (%f, %f)\n", t, y[0], y[1], y[2], y[3]);
            trajectory.push_back({y[0], y[1]});
            velocities.push_back({y[2], y[3]});
        }
        
        return {trajectory, velocities};
    }
};

#endif