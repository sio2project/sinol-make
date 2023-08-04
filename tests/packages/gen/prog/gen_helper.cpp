#include <bits/stdc++.h>

using namespace std;

int main(int argc, char const *argv[]) {
    if (argc != 2) {
        return 1;
    }

    int c = argv[1][4] - 'a';
    int g = argv[1][3] - '0';
    cout << c  << " " << g << endl;
}
