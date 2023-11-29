#include <bits/stdc++.h>

using namespace std;

int main() {
    int n, a, s = 0;
    cin >> n;
    for (int i = 0; i < n; i++) {
        cin >> a;
        s += a;

        assert(a <= n);
    }

    if (n == 3)
        assert(s == 5);

    cout << "OK" << endl << "Group " << n - 1 << endl;
    return 0;
}
