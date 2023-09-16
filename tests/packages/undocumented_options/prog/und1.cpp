#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono_literals;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && b == 1) {
        this_thread::sleep_for(3s);
    }
    cout << a + b << endl;
}
