#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

int wait(int secs) {
    auto start = high_resolution_clock::now();
    int i = 0;
    while (duration_cast<seconds>(high_resolution_clock::now() - start).count() < secs)
        i++;
    return i;
}

int main() {
    int i = wait(2);

    int a, b;
    cin >> a >> b;
    b += i;
    cout << a + b - i;
}
