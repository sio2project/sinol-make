#include <bits/stdc++.h>

using namespace std;

int main() {
    int n, s = 0;

    cin >> n;
    for (int i = 0; i < n; i++) {
        int a;
        cin >> a;
        s += a;
    }

    if (n == 5) {
        if (s % n != 0) {
            cout << "-1";
            return 0;
        }
        else {
            cout << s / 2 - 1;
            return 0;
        }
    }
    cout << s;
}
