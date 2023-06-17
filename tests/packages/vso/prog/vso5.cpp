// First test is OK,
// second test is WA,
// third test is OK,
// fourth test is RE,
// fifth test is WA.
// Group status should be RE.

#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && (b == 1 || b == 3)) {
        cout << a + b;
    }
    else if (a == 1 && (b == 2 || b == 5)) {
        cout << a + b - 1;
    }
    else if (a == 1 && b == 4) {
        int c = 0;
        cout << (a + b) / c;
    }
}
