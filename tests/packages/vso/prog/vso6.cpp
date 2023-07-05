// First test is OK,
// second test is WA,
// third test is ML,
// fourth test is RE,
// fifth test is OK.
// Group status should be ML.

#include <bits/stdc++.h>

using namespace std;

int rnd() {
    return rand() % 100;
}

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && (b == 1 || b == 5)) {
        cout << a + b;
    }
    else if (a == 1 && b == 2) {
        cout << a + b - 1;
    }
    else if (a == 1 && b == 4) {
        int c = 0;
        cout << (a + b) / c;
        return 1;
    }
    else if (a == 1 && b == 3) {
        vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			for (int j = 0; j <= 1000; j++)
                tmp[j] = rnd();
			v.push_back(tmp);
		}
		cout << a + b;
    }
}
