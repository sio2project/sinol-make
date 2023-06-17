// First test is WA,
// second test is OK,
// third test is TL,
// fourth test is RE,
// fifth test is ML.
// Group status should be TL.

#include <bits/stdc++.h>

using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && b == 1) {
        cout << a + b - 1;
    }
    else if (a == 1 && b == 2) {
        cout << a + b;
    }
    else if (a == 1 && b == 3) {
        this_thread::sleep_for(chrono::seconds(3));
        cout << a + b;
    }
    else if (a == 1 && b == 4) {
        int c = 0;
        cout << (a + b) / c;
    }
    else if (a == 1 && b == 5) {
        vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			v.push_back(tmp);
		}
		cout << a + b;
    }
}
