#include <bits/stdc++.h>
#include <chrono>

using namespace std;
using namespace std::chrono_literals;


int main() {
    char array[30000000]; // 30 MB
    this_thread::sleep_for(5s);
    int a, b;
    cin >> a >> b;
    array[a] = (char)b;
    cout << a + array[a];
    return 0;
}
