#include <bits/stdc++.h>

using namespace std;

int main() {
    for (char c = 'a'; c <= 'e'; c++) {
        string letter(1, c);
        ofstream f("vso1" + letter + ".in");
        f << "1 " << (c - 'a' + 1) << endl;
        f.close();
    }
}
