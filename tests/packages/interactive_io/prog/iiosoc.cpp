#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 3) {
        cerr << "Usage: ./a.out <input_file> <answer_file>" << endl;
        return 1;
    }
    ifstream ifs(argv[1]);
    ofstream out(argv[2]);
    int a;
    ifs >> a;
    cout << a << "\n" << flush;
    int ans;
    cin >> ans;
    if (ans == a + 42) {
        out << "OK\n";
    }
    else if (ans == a + 10) {
        out << "OK\nwrong diff\n50";
    }
    else {
        out << "WRONG\n" << ans;
    }
}
