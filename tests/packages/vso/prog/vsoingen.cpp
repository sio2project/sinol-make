#include <bits/stdc++.h>

using namespace std;

int main() {
    for (char c = 'a'; c <= 'e'; c++) {
        string path = "vso1";
        path += c;
        path += ".in";
        ofstream f(path);
        f << "1 " << (c - 'a' + 1) << endl;
        f.close();
    }
}
