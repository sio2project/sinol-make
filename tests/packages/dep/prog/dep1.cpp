// Wrong answer on group 1. Groups 2 and 3 depend on group 1, so they should
// score 0 points as well.
#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1) {
        cout << a + b + 1 << "\n";
    } else {
        cout << a + b << "\n";
    }
}
