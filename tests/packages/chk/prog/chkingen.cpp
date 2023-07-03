#include <bits/stdc++.h>

using namespace std;

int main() {
    ofstream f;

    f.open("chk1a.in");
    f << "5" << endl;
    f << "1 2 3 4 5" << endl;
    f.close();

    f.open("chk1b.in");
    f << "5" << endl;
    f << "1 2 3 4 4" << endl;
    f.close();

    f.open("chk1c.in");
    f << "5" << endl;
    f << "1 1 3 5" << endl;
    f.close();

    f.open("chk2a.in");
    f << "4" << endl;
    f << "1 2 3 6" << endl;
    f.close();

    f.open("chk2b.in");
    f << "1" << endl;
    f << "6" << endl;
    f.close();

    f.open("chk2c.in");
    f << "4" << endl;
    f << "1 2 3 4" << endl;
    f.close();
}
