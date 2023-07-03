#include <bits/stdc++.h>

using namespace std;

int main(int argc, char** argv) {
    assert(argc == 4);
    ifstream in(argv[1]);
    ifstream out(argv[2]);
    ifstream correct(argv[3]);

    int ans, out_ans;
    correct >> ans;
    out >> out_ans;

    if (ans == -1 && out_ans != -1) {
        cout << "WRONG" << endl;
        cout << "Expected -1, got " << out_ans << endl;
        return 0;
    }

    int n, s = 0;
    in >> n;
    for (int i = 0; i < n; i++) {
        int a;
        in >> a;
        s += a;
    }

    if (out_ans > s) {
        cout << "WRONG" << endl;
        cout << "Answer to big" << endl;
        return 0;
    }

    if (out_ans > s / 2) {
        cout << "OK" << endl;
        cout << "Answer to big" << endl;
        cout << "50" << endl;
        return 0;
    }

    if (out_ans <= s / 2) {
        cout << "OK";
        return 0;
    }
}
