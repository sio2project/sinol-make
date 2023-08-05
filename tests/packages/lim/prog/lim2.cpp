#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

int main() {
    int a, b;
    cin >> a >> b;

    int tl = 900000;
    if (a == 2 && b == 1) {
        tl = 2900000;
    }
    auto start = high_resolution_clock::now();
    int i = 0;
    while (duration_cast<microseconds>(high_resolution_clock::now() - start).count() < tl) {
        i++;
    }

    cout << a + b << endl;
}
