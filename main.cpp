#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include "particle.cpp"
#include "pos.cpp"
using namespace std;

// OTHER
const int NUM_PARTICLES = []() {
    const char* env = std::getenv("NUM_PARTICLES");
    return env ? std::atoi(env) : 100;
}();

int main() {
    srand(time(0));

    vector<Particle> particles(NUM_PARTICLES);

    for (int i = 0; i < NUM_PARTICLES; i++) {
        double x = (rand() % 1000) / 100.0;
        double y = (rand() % 1000) / 100.0;
        double Vx = (rand() % 200) / 10.0;
        double Vy = (rand() % 200) / 10.0;

        particles[i] = Particle(x, y, Vx, Vy);

        vector<pos> trajectory = particles[i].calclulateTrajectory();
        printf("Particle %d trajectory calculated!\n", i+1);

        // save trajectory to file
        string filename = "./trajectories/trajectory_" + to_string(i) + ".txt";

        ofstream file(filename);
        for (const auto& pos : trajectory) {
            file << pos.x << " " << pos.y << endl;
        }
        file.close();
    }
}