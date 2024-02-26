// Author : st-make
// Task   : Zadanie przykładowe
// Memory : O(1)
// Time   : O(a+b)
// Solv   : Rozwiązanie powolne - sprawdza wszystkie możliwości po kolei

#include <bits/stdc++.h>

using namespace std;

int a, b, c;

int main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0);

    cin >> a >> b;
    while (c != a + b) {
        c++;
    }
    cout << c << endl;
    
    return 0;
}
