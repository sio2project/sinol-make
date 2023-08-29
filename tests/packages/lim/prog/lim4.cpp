#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;

    vector<long long> mem;
    int times = 2;
    if (a == 2)
        times = 1;

    for (int i = 1; i <= times * 1280000; i++) {
        mem.push_back(i);
    }
    cout << a + b;
}
