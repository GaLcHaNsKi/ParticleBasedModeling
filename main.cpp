#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include "particle.cpp"
#include "pos.cpp"
using namespace std;

#ifndef NUM_PARTICLES
#define NUM_PARTICLES 100
#endif

int main() {
    srand(time(0));
    printf("Simulating %d particles...\n", NUM_PARTICLES);

    vector<Particle> particles(NUM_PARTICLES);

    for (int i = 0; i < NUM_PARTICLES; i++) {
        double x = 0;//(rand() % 1000) / 100.0;
        double y = 0;//(rand() % 1000) / 100.0;
        double Vx = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);
        double Vy = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);

        particles[i] = Particle(x, y, Vx, Vy);

        pair<vector<pos>, vector<pos>> trajectory = particles[i].calclulateTrajectory();

        // save trajectory to file
        string filename = "./trajectories/trajectory_" + to_string(i) + ".txt";

        ofstream file(filename);
        for (int j = 0; j < trajectory.first.size(); j++) {
            file << trajectory.first[j].x << " " << trajectory.first[j].y << endl;
        }
        file.close();

        string vel_filename = "./trajectories/velocity_" + to_string(i) + ".txt";
        ofstream vel_file(vel_filename);
        for (int j = 0; j < trajectory.second.size(); j++) {
            vel_file << trajectory.second[j].x << " " << trajectory.second[j].y << endl;
        }
        vel_file.close();

        printf("Particle %d trajectory calculated and saved!\n", i+1);
    }
}