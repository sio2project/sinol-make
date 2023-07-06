// First test ML,
// second test RE,
// third test WA,
// other OK.
// Group should have status ML.

#include <bits/stdc++.h>

using namespace std;

int rnd() {
    return rand() % 100;
}

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && b == 1) {
        vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			for (int j = 0; j <= 1000; j++)
                tmp[j] = rnd();
			v.push_back(tmp);
		}
		cout << a + b;
    }
    else if (a == 1 && b == 2) {
        int c = 0;
        cout << (a + b) / c;
        return 1;
    }
    else if (a == 1 && b == 3) {
        cout << "1";
    }
    else {
        cout << a + b;
    }
    return 0;
}
