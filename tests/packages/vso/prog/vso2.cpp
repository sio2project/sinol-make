// First test RE,
// second WA,
// other OK.
// Group should have status RE.

#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;

    if (a == 1 && b == 1) {
        int c = 0;
		cout << a + b / c;
		return 1;
    }
    else if (a == 1 && b == 2) {
        cout << "0";
    }
    else {
        cout << a + b;
    }
    return 0;
}
