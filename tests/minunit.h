#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include "rebound.h"

#define mu_assert(message, test) do { if (!(test)) return message; } while (0)
#define mu_assert_almost_equal(message, f1, f2, delta) do { if (fabs(f1-f2)>delta) return message; } while (0)
#define mu_run_test(test) do { char *message = test(); tests_run++; \
                               if (message) return message; } while (0)
int tests_run;

#define MU_RUN_ALL() \
    int main(int argc, char* argv[]) {\
    char *result = all_tests();\
    if (result !=0) {\
        printf("%s\n", result);\
    }else{\
        printf("ALL TESTS PASSED\n");\
    }\
    printf("Tests run: %d\n", tests_run);\
    return result != 0;\
    }

