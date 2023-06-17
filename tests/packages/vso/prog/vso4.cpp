// First test TL,
// second test ML,
// third test RE,
// fourth test WA,
// other OK.
// This group should have status TL.

#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && b == 1) {
        this_thread::sleep_for(chrono::seconds(3));
        cout << a + b;
    }
    else if (a == 1 && b == 2) {
        vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			v.push_back(tmp);
		}
		cout << a + b;
    }
    else if (a == 1 && b == 3) {
        int c = 0;
        cout << (a + b) / c;
        return 1;
    }
    else if (a == 1 && b == 4) {
        cout << "1";
    }
    else {
        cout << a + b;
    }
    return 0;
}
