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
    int a, b;
    cin >> a >> b;

    if (a == 2 && b == 1) {
        int i = wait(6);
        a += i - i;
    }
    else {
        int i = wait(2);
        a += i - i;
    }

    cout << a + b << endl;
}
