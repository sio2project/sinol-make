#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 2) {
        cout << "WRONG\nWrong number of arguments";
        return 1;
    }
    int n;
    cin >> n;
    if (n == 2 && strcmp(argv[1], "wer1a.in") == 0) {
        cout << "OK\n";
        return 0;
    }
    if (n == 3 && strcmp(argv[1], "wer2a.in") == 0) {
        cout << "OK\n";
        return 0;
    }
    if (n == 4 && strcmp(argv[1], "wer3a.in") == 0) {
        cout << "OK\n";
        return 0;
    }
    cout << "WRONG\nWrong test";
    return 1;
}
