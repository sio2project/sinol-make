// First test WA,
// other OK.
// Group should have status WA.

#include <bits/stdc++.h>

using namespace std;

int main() {
    cin >> a >> b;
    if (a == 1 && b == 1) {
        cout << 0;
    }
    else {
        cout << a + b;
    }
    return 0;
}
