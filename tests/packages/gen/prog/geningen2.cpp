// Fails with -fsanitize=address
#include <bits/stdc++.h>

using namespace std;

int main() {
    int *a = (int*)malloc(1024);
    a[0] = 0;
    cout << a[0] << endl;
}
