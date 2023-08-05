#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;

    vector<long long> mem;
    for (int i = 1; i <= 540000; i++) {
        mem.push_back(i);
    }
    cout << a + b;
}
