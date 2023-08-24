#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono_literals;

int main() {
    this_thread::sleep_for(2s);

    int a, b;
    cin >> a >> b;
    cout << a + b;
}
