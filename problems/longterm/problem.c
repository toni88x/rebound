#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include "rebound.h"

double ss_pos[3][3] =
    {
     {-4.06428567034226e-3, -6.08813756435987e-3, -1.66162304225834e-6}, // Sun
     {+3.40546614227466e+0, +3.62978190075864e+0, +3.42386261766577e-2}, // Jupiter
     {+6.60801554403466e+0, +6.38084674585064e+0, -1.36145963724542e-1}, // Saturn
};
double ss_vel[3][3] =
    {
     {+6.69048890636161e-6, -6.33922479583593e-6, -3.13202145590767e-9}, // Sun
     {-5.59797969310664e-3, +5.51815399480116e-3, -2.66711392865591e-6}, // Jupiter
     {-4.17354020307064e-3, +3.99723751748116e-3, +1.67206320571441e-5}, // Saturn
};

double ss_mass[3] =
    {
     1.00000597682, // Sun + inner planets
     1. / 1047.355, // Jupiter
     1. / 3501.6,   // Saturn
};

void heartbeat(struct reb_simulation* const r);
double e_initial; 

int main(int argc, char* argv[]) {
	struct reb_simulation* r = reb_create_simulation();
	// Setup constants
	const double k = 0.01720209895; // Gaussian constant
	r->dt = 40;			// in days
	r->G = k * k;			// These are the same units as used by the mercury6 code.
	
	// Setup callbacks:
	r->heartbeat = heartbeat;
	r->force_is_velocity_dependent = 0; // Force only depends on positions.
	r->integrator	= REB_INTEGRATOR_IAS15;
	r->ri_ias15.epsilon = 1e-7;

	// Initial conditions
	for (int i = 0; i < 3; i++) {
		struct reb_particle p = {0};
		p.x = ss_pos[i][0];
		p.y = ss_pos[i][1];
		p.z = ss_pos[i][2];
		p.vx = ss_vel[i][0];
		p.vy = ss_vel[i][1];
		p.vz = ss_vel[i][2];
		p.m = ss_mass[i];
		reb_add(r, p);
	}
	reb_move_to_com(r);
	printf("sise      %d %d\n\n\n", sizeof(double), sizeof(long double));  


	e_initial = reb_tools_energy(r);

	system("rm -f  energy.txt");
	// Start integration
	reb_integrate(r, INFINITY);


}
double nextt = 10000000;
void heartbeat(struct reb_simulation* const r) {

	if (r->t>nextt) {
		nextt *= 1.025;
		double e_final = reb_tools_energy(r);
		printf("%e %e %e\n", r->t/4332.8201, fabs((e_final - e_initial) / e_initial), r->dt/4332.8201);
		FILE* f = fopen("energy.txt","a+");
		fprintf(f, "%e %e\n", r->t/4332.8201, fabs((e_final - e_initial) / e_initial));
		fclose(f);
	}
}
