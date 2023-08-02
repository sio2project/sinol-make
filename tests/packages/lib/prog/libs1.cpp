#include <bits/stdc++.h>
#include "liblib.h"

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
