#include "../minunit.h"

double ss_pos[6][3] =
    {
     {-4.06428567034226e-3, -6.08813756435987e-3, -1.66162304225834e-6}, // Sun
     {+3.40546614227466e+0, +3.62978190075864e+0, +3.42386261766577e-2}, // Jupiter
     {+6.60801554403466e+0, +6.38084674585064e+0, -1.36145963724542e-1}, // Saturn
     {+1.11636331405597e+1, +1.60373479057256e+1, +3.61783279369958e-1}, // Uranus
     {-3.01777243405203e+1, +1.91155314998064e+0, -1.53887595621042e-1}, // Neptune
     {-2.13858977531573e+1, +3.20719104739886e+1, +2.49245689556096e+0}  // Pluto
};
double ss_vel[6][3] =
    {
     {+6.69048890636161e-6, -6.33922479583593e-6, -3.13202145590767e-9}, // Sun
     {-5.59797969310664e-3, +5.51815399480116e-3, -2.66711392865591e-6}, // Jupiter
     {-4.17354020307064e-3, +3.99723751748116e-3, +1.67206320571441e-5}, // Saturn
     {-3.25884806151064e-3, +2.06438412905916e-3, -2.17699042180559e-5}, // Uranus
     {-2.17471785045538e-4, -3.11361111025884e-3, +3.58344705491441e-5}, // Neptune
     {-1.76936577252484e-3, -2.06720938381724e-3, +6.58091931493844e-4}  // Pluto
};

double ss_mass[6] =
    {
     1.00000597682, // Sun + inner planets
     1. / 1047.355, // Jupiter
     1. / 3501.6,   // Saturn
     1. / 22869.,   // Uranus
     1. / 19314.,   // Neptune
     0.0  // Pluto
};


struct reb_simulation* setup_sim(){
	struct reb_simulation* r = reb_create_simulation();
	// Setup constants
	const double k = 0.01720209895; // Gaussian constant
	r->dt = 40;			// in days
	r->G = k * k;			// These are the same units as used by the mercury6 code.
	r->force_is_velocity_dependent = 0; // Force only depends on positions.

	// Initial conditions
	for (int i = 0; i < 6; i++) {
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

	r->N_active = r->N - 1; // Pluto is treated as a test-particle.
    return r;
}


static char * test_oss_whfast(){
    struct reb_simulation* r = setup_sim();
	r->integrator = REB_INTEGRATOR_WHFAST;
	double e_initial = reb_tools_energy(r);
	reb_integrate(r, 7.3e5);
	double e_final = reb_tools_energy(r);
    mu_assert_almost_equal("OSS: WHFast energy error too large.",(e_final - e_initial)/e_initial,0.,1e-7);
    return 0;
}

static char * test_oss_whfast_cor(){
    struct reb_simulation* r = setup_sim();
	r->integrator = REB_INTEGRATOR_WHFAST;
	r->ri_whfast.safe_mode = 0;     // Turn of safe mode. Need to call integrator_synchronize() before outputs.
	r->ri_whfast.corrector = 11;    // Turn on symplectic correctors (11th order).
	double e_initial = reb_tools_energy(r);
	reb_integrate(r, 7.3e5);
	double e_final = reb_tools_energy(r);
    mu_assert_almost_equal("OSS: WHFast with correctors energy error too large.",(e_final - e_initial)/e_initial,0.,1e-10);
    return 0;
}

static char * test_oss_ias15(){
    struct reb_simulation* r = setup_sim();
	r->integrator	= REB_INTEGRATOR_IAS15;
	double e_initial = reb_tools_energy(r);
	reb_integrate(r, 7.3e5);
	double e_final = reb_tools_energy(r);
    mu_assert_almost_equal("OSS: IAS15 energy error too large.",(e_final - e_initial)/e_initial,0.,1e-15);
    return 0;
}

static char * all_tests() {
    mu_run_test(test_oss_whfast);
    mu_run_test(test_oss_whfast_cor);
    mu_run_test(test_oss_ias15);
    return 0;
}

MU_RUN_ALL();
