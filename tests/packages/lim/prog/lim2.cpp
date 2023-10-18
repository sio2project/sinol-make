#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

int wait(int milisecs) {
    auto start = high_resolution_clock::now();
    int i = 0;
    while (duration_cast<milliseconds>(high_resolution_clock::now() - start).count() < milisecs)
        i++;
    return i;
}

int main() {
    int a, b;
    cin >> a >> b;

    if (a == 2 && b == 1) {
        int i = wait(7000);
        a += i - i;
    }
    else {
        int i = wait(3000);
        a += i - i;
    }

    cout << a + b << endl;
}
