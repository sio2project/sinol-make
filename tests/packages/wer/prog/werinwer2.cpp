#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 1) {
        cout << "ERROR: Invalid number of arguments" << endl;
        cout << "inwer: " << argv[0] << endl;
        return 1;
    }

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
