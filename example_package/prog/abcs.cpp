// Author : st-make
// Task   : Zadanie przykładowe
// Memory : O(n)
// Time   : O(n*log(n))
// Solv   : Rozwiązanie wolne - sortuje liczby z wejścia

#include <bits/stdc++.h>

using namespace std;

long double a, b;
int n, x;
vector<int> v;

int main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0);

    cin >> a >> b;
    cout << fixed << setprecision(8) << a + b << '\n';

    cin >> n;
    for (int i=1; i<=n; ++i) {
        cin >> x;
        v.push_back(x);
    }
    sort(v.begin(), v.end());

    for (int i=0; i<n; ++i) {
        if (i > 0) cout << ' ';
        cout << v[i];
    }
    cout << '\n';
    
    return 0;
}

// wzorcówk musi nazywać się abc.*
// programy wzorcowe powinny nazywać się abc{}.*
// programy wolne powinny nazywać się abcs{}.*
// programy błedne powinny nazywać się abcb{}.*
// {} może być (raczej) dowolnym ciągiem, najlepiej dawać liczby (abcs2.cpp, abc10.py)