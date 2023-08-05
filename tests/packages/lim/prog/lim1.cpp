#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono_literals;

int main() {
    int a, b;
    cin >> a >> b;

    vector<int> v(5, 0);
    this_thread::sleep_for(1.1s);

    cout << a + b << endl;
}
