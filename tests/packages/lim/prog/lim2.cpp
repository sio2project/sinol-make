#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono;

__attribute__((optimize("O0")))
void s2j_wait(long long instructions) {
    instructions /= 3; // Every pass of the loop below takes 3 instructions.
    while (instructions > 0)
        --instructions;
}

int wait(int secs) {
    if (getenv("UNDER_SIO2JAIL") != NULL) {
        s2j_wait((long long)secs * 2'000'000'000);
        return 0;
    }
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
        int i = wait(7);
        a += i - i;
    }
    else {
        int i = wait(2);
        a += i - i;
    }

    cout << a + b << endl;
}
