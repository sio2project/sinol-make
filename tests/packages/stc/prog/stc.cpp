#include <bits/stdc++.h>

using namespace std;

int main()
{
    char stack[10000000]; // ~10MB
    cin >> stack[0] >> stack[1];
    cout << (stack[0] + stack[1] - 2 * '0');
    return 0;
}
