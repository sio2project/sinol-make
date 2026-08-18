// Fails with -fsanitize=undefined
#include <iostream>

using namespace std;

int main(int argc, char** argv) {
    int k = 0x7fffffff;
    k += argc;
    cout << k << " " << argv[0] << endl;
}
