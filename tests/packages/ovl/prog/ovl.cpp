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
    int i = wait(2);

    int a, b;
    cin >> a >> b;
    b += i;
    cout << a + b - i;
}
