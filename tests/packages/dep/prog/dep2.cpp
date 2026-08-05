// Wrong answer on group 2. Group 3 depends on group 2, so it should score
// 0 points as well.
#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 2) {
        cout << a + b + 1 << "\n";
    } else {
        cout << a + b << "\n";
    }
}
