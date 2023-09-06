#include <bits/stdc++.h>

using namespace std;

int main() {
    int n, a, s = 0;
    cin >> n;
    for (int i = 0; i < n; i++) {
        cin >> a;
        s += a;

        if (a >= n) {
            cout << "ERROR: " << a << " >= " << n << "\n";
            return 1;
        }
    }
    if (n == 3 && s != 5) {
        cout << "ERROR: " << s << " != 5\n";
        return 1;
    }

    cout << "OK" << endl << "Group " << n - 1 << endl;
    return 0;
}
