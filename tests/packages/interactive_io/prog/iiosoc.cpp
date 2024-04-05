#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 3) {
        cerr << "Usage: ./a.out <input_file> <answer_file>" << endl;
        return 1;
    }
    ifstream ifs(argv[1]);
    int a;
    ifs >> a;
    cout << a << "\n" << flush;
    int ans;
    cin >> ans;
    if (ans == a + 42) {
        cerr << "OK\n";
    }
    else if (ans == a + 10) {
        cerr << "OK\nwrong diff\n50";
    }
    else {
        cerr << "WRONG\n";
    }
}
