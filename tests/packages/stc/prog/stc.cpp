#include <bits/stdc++.h>

using namespace std;

int t[10];

int recursion(int i) {
    if (i == 800000)
        return i;
    t[i % 10] += i + recursion(i + 1);
    return i;
}

int main() {
    int a, b, c;
    c = recursion(0);
    cin >> a >> b;
    cout << a + b + t[c % 10];
}
