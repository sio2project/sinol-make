#include <bits/stdc++.h>
#include <assert.h>

using namespace std;

int main(int argc, char *argv[]) {
    assert(argc == 2);
    int proc_num = atoi(argv[1]);
    assert(proc_num == 0);

    int a;
    cin >> a;
    if (a == 42)
        cout << a + 24 << endl;
    else
        cout << a + 41 << endl;
}
