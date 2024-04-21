#include <bits/stdc++.h>

using namespace std;

int main() {
    int n, s = 0;
    cin >> n;
    for (int i = 1; i <= n; i++) {
        int a;
        cin >> a;
        s += a;
    }
    s *= n;
    cout << s << "\n";
}
