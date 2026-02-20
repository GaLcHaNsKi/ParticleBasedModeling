#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <ctime>
#include <iomanip>
#include "particle.cpp"
#include "pos.cpp"
using namespace std;

#ifndef NUM_PARTICLES
#define NUM_PARTICLES 100
#endif

int X_FROM = -30;
int X_TO = 30;
int Y_FROM = -30;
int Y_TO = 30;

double SIZE = 1;
// нужно считать сколько частиц находится в каждой ячейке размера SIZE x SIZE, и сохранять эти данные в файл для дальнейшей визуализации
int main() {
    srand(time(0));
    printf("Simulating %d particles...\n", NUM_PARTICLES);

    vector<Particle> particles(NUM_PARTICLES);

    time_t start_time = time(0);

    for (int i = 0; i < NUM_PARTICLES; i++) {
        // double x = 0;//(rand() % 100) / 10.0;
        // double y = 0;//(rand() % 100) / 10.0;

        // double Vx = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);
        // double Vy = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);

        double x = (1 + (rand() % 100) / 15.0) * (rand() % 2 == 0 ? 1 : -1);
        double y = (1 + (rand() % 100) / 15.0) * (rand() % 2 == 0 ? 1 : -1);
        double Vx = 0;
        double Vy = 0;

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

        time_t current_time = time(0);
        double elapsed_time = difftime(current_time, start_time);

        std::cout << "\rProgress: " << fixed << setprecision(2) << i / (double)NUM_PARTICLES * 100 << "%";
        std::cout << " | Time: " << fixed << setprecision(2) << elapsed_time << "s";

        int remained_seconds = (int)((NUM_PARTICLES - i) * (elapsed_time / (i + 1)));
        int remained_minutes = remained_seconds / 60;
        int remained_seconds_only = remained_seconds % 60;

        std::cout << " | Remained time: " << remained_minutes << " min " << remained_seconds_only << " s";

        std::cout.flush();
    }
    std::cout << "\rProgress: 100.00%" << std::endl;

    time_t end_time = time(0);
    double elapsed_time = difftime(end_time, start_time);
    printf("Simulation completed in %.2f seconds.\n", elapsed_time);
}