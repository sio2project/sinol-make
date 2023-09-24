#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

// Change this function to generate one test for stresstesting.
// The script prog/abcingen.sh in 10 seconds generates
// as much tests as possible and compares the outputs
// of the model solution and brute solution.
// The tests shouldn't be very big, but should be able to cover edge cases.
void generate_one_stresstest(oi::Random &rng) {
    cout << rng.randSInt(1, 10) << ' ' << rng.randSInt(1, 10) << endl;
}

// Change this function to create a test with the given name.
// The lists of tests to generate needs to be written in prog/abcingen.sh
void generate_proper_test(string test_name, oi::Random &rng) {
    if (test_name == "0a")
        cout << "0 1" << endl;
    else if (test_name == "1a")
        cout << rng.randSInt(5, 1'000) << ' ' << rng.randSInt(5, 1'000) << endl;
    else if (test_name == "2a")
        cout << "2 2" << endl;
    else {
        cerr << "Unrecognized test_name = " << test_name << endl;
        exit(1);
    }
}

int main(int argc, char *argv[]) {
    if (argc == 3 && string(argv[1]) == "stresstest") {
        unsigned int seed = atoi(argv[2]);
        oi::Random rng(seed);
        generate_one_stresstest(rng);
        return 0;
    }
    if (argc != 2) {
        cerr << "Run prog/abcingen.sh to stresstest and create proper tests." << endl;
        exit(1);
    }
    string test_name = argv[1];
    unsigned int seed = (unsigned int) hash<string>{}(test_name);
    oi::Random rng(seed);
    cerr << "Generating test " << test_name << "..." << endl;
    generate_proper_test(test_name, rng);
}
