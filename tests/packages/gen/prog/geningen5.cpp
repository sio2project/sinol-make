#include <bits/stdc++.h>

using namespace std;

int main() {
    #ifdef _INGEN
    ofstream f("gen1.in");
    f << "1 2\n";
    f.close();

    f.open("gen2.in");
    f << "2 3\n";
    f.close();
    #else
        This should not compile
    #endif
}
