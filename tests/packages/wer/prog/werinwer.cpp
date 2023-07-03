#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 1) {
        cout << "ERROR: Invalid number of arguments" << endl;
        return 1;
    }

    int n, a;
    cin >> n;
    for (int i = 0; i < n; i++) {
        cin >> a;

        if (a >= n) {
            cout << "ERROR: " << a << " >= " << n << "\n";
            return 1;
        }
    }

    cout << "OK" << endl << "Group " << n - 1 << endl << "Test " + (string)argv[1] << endl;
    return 0;
}
