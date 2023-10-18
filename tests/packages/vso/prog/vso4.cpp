// First test TL,
// second test ML,
// third test RE,
// fourth test WA,
// other OK.
// This group should have status TL.

#include <bits/stdc++.h>

using namespace std;
using namespace std::chrono;

int rnd() {
    return rand() % 100;
}

int wait(int secs) {
    auto start = high_resolution_clock::now();
    int i = 0;
    while (duration_cast<seconds>(high_resolution_clock::now() - start).count() < secs)
        i++;
    return i;
}

int main() {
    int a, b;
    cin >> a >> b;
    if (a == 1 && b == 1) {
        int i = wait(3);
        cout << a + b + i - i;
    }
    else if (a == 1 && b == 2) {
        vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			for (int j = 0; j <= 1000; j++)
                tmp[j] = rnd();
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
