#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <ctime>
#include <iomanip>
#include "particle.cpp"
#include "structures.cpp"
using namespace std;

#ifndef NUM_PARTICLES
#define NUM_PARTICLES 100
#endif

#define STEPS 5000

int X_FROM = -30;
int X_TO = 30;
int Y_FROM = -30;
int Y_TO = 30;

double SIZE = 1;
// нужно считать сколько частиц находится в каждой ячейке размера SIZE x SIZE, и сохранять эти данные в файл для дальнейшей визуализации
int main() {
    srand(time(0));
    printf("Simulating %d particles...\n", NUM_PARTICLES);

    time_t start_time = time(0);

    vector<Particle> particles(NUM_PARTICLES);

    unsigned int MAX_Q = 0;

    int ***q_squares = new int**[60];
    for (int i = 0; i < 60; ++i) {
        q_squares[i] = new int*[60];
        for (int j = 0; j < 60; ++j) {
            q_squares[i][j] = new int[STEPS];

            for (int k=0; k<STEPS; k++) {
                q_squares[i][j][k] = 0;
            }
        }
    }

    for (int i = 0; i < NUM_PARTICLES; i++) {
        // double x = 0;//(rand() % 100) / 10.0;
        // double y = 0;//(rand() % 100) / 10.0;

        // double Vx = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);
        // double Vy = (rand() % 200) / 10.0 * (-1) * (rand() % 2 == 0 ? 1 : -1);

        double x = (1 + (rand() % 100) / 10.0) * (rand() % 2 == 0 ? 1 : -1);
        double y = (1 + (rand() % 100) / 10.0) * (rand() % 2 == 0 ? 1 : -1);
        double Vx = 0;
        double Vy = 0;

        particles[i] = Particle(x, y, Vx, Vy);

        pair<vector<pos>, vector<pos>> trajectory = particles[i].calclulateTrajectory(STEPS);

        // сохранение траектории в файл можно использовать лишь при небольшом количестве частиц, чтобы легче отрисовывать
        // save trajectory to file
        // string filename = "./trajectories/trajectory_" + to_string(i) + ".txt"; 

        // ofstream file(filename);
        for (int k = 0; k < trajectory.first.size(); k++) {
            // file << trajectory.first[k].x << " " << trajectory.first[k].y << endl;

            // параллельно записываем в q_squares
            // вычисляем, какая это ячейка

            int shift_coef = 30;

            int i = floor(trajectory.first[k].y) + shift_coef;
            int j = floor(trajectory.first[k].x) + shift_coef;

            if (0 > i || i >= 60 || 0 > j || j >= 60) continue;

            q_squares[i][j][k] = q_squares[i][j][k] + 1;

            if (q_squares[i][j][k] > MAX_Q) MAX_Q = q_squares[i][j][k];
        }
        // file.close();

        // string vel_filename = "./trajectories/velocity_" + to_string(i) + ".txt";
        // ofstream vel_file(vel_filename);
        // for (int j = 0; j < trajectory.second.size(); j++) {
        //     vel_file << trajectory.second[j].x << " " << trajectory.second[j].y << endl;
        // }
        // vel_file.close();

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

    std::cout << "Saving density...\n";

    // Save q_squares to files
    for (int k = 0; k < STEPS; k++) {
        string filename = "./density/density_" + to_string(k) + ".txt";
        ofstream file(filename);
        for (int i = 0; i < 60; ++i) {
            for (int j = 0; j < 60; ++j) {
                file << q_squares[i][j][k] << " ";
            }
            file << endl;
        }
        file.close();

        std::cout << "\r" << fixed << setprecision(2) << k / (double)STEPS * 100 << "%";
        std::cout.flush();
    }
    std::cout << "\r100%" << endl;

    printf("Maximum quantity per cell is %d\n", MAX_Q);

    time_t end_time = time(0);
    double elapsed_time = difftime(end_time, start_time);
    printf("Simulation completed in %.2f seconds.\n", elapsed_time);
}