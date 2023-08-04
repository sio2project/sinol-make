#include <bits/stdc++.h>
#include "liblib.h"

using namespace std;

int main() {
    init();

    int a = 0, b = 100;
    while (a <= b) {
        int m = (a + b) / 2;
        int g = guess(m);
        if (g == 0) {
            quit();
            return 0;
        }
        if (g == 1) {
            b = m + 1;
        } else {
            a = m - 1;
        }
    }
    guess(a);
    quit();
}
