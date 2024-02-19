#include <bits/stdc++.h>

using namespace std;

int main() {
    ofstream f("bad0.in");
    f << "1 1 \n";
    f.close();
    f.open("bad1.in");
    f << "   1 1\n";
    f.close();
    f.open("bad2.in");
    f << "1  1\n";
    f.close();
    f.open("bad3.in");
    f << "1 1\n\n\n";
    f.close();
    f.open("bad4.in");
    f << "1 1\n1 1 \n";
    f.close();
    f.open("bad5.in");
    f << "1 1";
    f.close();
}
