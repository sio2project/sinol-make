#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

int main() {
    int a, b;
    cin >> a >> b;

    auto start = high_resolution_clock::now();
    int i = 0;
    while (duration_cast<microseconds>(high_resolution_clock::now() - start).count() < 750000) {
        i++;
    }

    cout << a + b << endl;
}
