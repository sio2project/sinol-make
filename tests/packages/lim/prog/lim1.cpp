#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

int main() {
    int a, b;
    cin >> a >> b;

    auto start = high_resolution_clock::now();
    int i = 0;
    vector<int> v(5, 0);
    while (duration_cast<microseconds>(high_resolution_clock::now() - start).count() < 900000) {
        i++;
        v[i % 5]++;
    }

    cout << a + b << endl;
    cerr << "i = " << i << endl;
}
