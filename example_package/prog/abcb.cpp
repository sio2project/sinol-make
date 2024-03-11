// Author : st-make
// Task   : Zadanie przykładowe
// Memory : O(1)
// Time   : O(n)
// Solv   : Rozwiązanie błędne - używa int zamiast double

#include <bits/stdc++.h>

using namespace std;

int a, b;
int n;

int main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0);

    cin >> a >> b;
    cout << fixed << setprecision(8) << a + b << '\n';

    cin >> n;
    for (int i=1; i<=n; ++i) {
        if (i > 1) cout << ' ';
        cout << i;
    }
    cout << '\n';
    
    return 0;
}

// wzorcówka musi nazywać się abc.*
// pozostałe programy wzorcowe powinny nazywać się abc{}.*
// programy wolne powinny nazywać się abcs{}.*
// programy błędne powinny nazywać się abcb{}.*
// jako {} najlepiej dawać kolejne liczby od 1. Przykład: abcs2.cpp, abc10.py.
