#include <bits/stdc++.h>

using namespace std;

int main() {
    for (char c = 'a'; c <= 'e'; c++) {
        ofstream f("vso1" + c + ".in");
        f << "1 " << (c - 'a' + 1) << endl;
        f.close();
    }
}
