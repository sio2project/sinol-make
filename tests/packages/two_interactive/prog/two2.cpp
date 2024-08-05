#include <bits/stdc++.h>
#include <assert.h>

using namespace std;

void process0() {
    int n;
    cin >> n;
    cout << n + 42 << endl;
    cin >> n;
    cout << n * 3 << endl;
}

void process1() {
    int n;
    cin >> n;
    cout << n / 2 << endl;
}

int main(int argc, char* argv[]) {
    assert(argc == 2);
    int proc_num = atoi(argv[1]);

    if (proc_num == 0) {
        process0();
    }
    else if (proc_num == 1) {
        process1();
    }
    else {
        assert(false);
    }
}
