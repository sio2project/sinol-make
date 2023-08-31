#include <bits/stdc++.h>
#include "lsalib.h"

using namespace std;

int main() {
    init();
    for (int i = 1; i <= 100; i++) {
        if (guess(i) == 0) {
            break;
        }
    }
    quit();
    return 0;
}
