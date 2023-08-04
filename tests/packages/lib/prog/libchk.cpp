#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    assert(argc == 4);

    ifstream out(argv[2]);

    string s1, s2;
    out >> s1 >> s2;
    if (s2 == "") {
        cout << "WRONG\n";
        return 0;
    }
    cout << s2;
    return 0;
}
