#include <bits/stdc++.h>
#include "lsalib.h"

using namespace std;

int n, m, cnt = 0;
bool finished = false;

void init() {
    cin >> n >> m;
}

int guess(int a) {
    cnt++;
    if (a == n) {
        if (cnt > m) {
            cout << "Too_many_queries" << endl;
            cout << "WRONG" << endl;
            finished = true;
            return 0;
        }
        else {
            cout << "Correct" << endl;
            cout << "OK" << endl;
            finished = true;
            return 0;
        }
    }
    if (a < n) {
        return -1;
    }
    return 1;
}

void quit() {
    if (!finished) {
        cout << "Not_correct" << endl;
        cout << "WRONG" << endl;
    }
    exit(0);
}
