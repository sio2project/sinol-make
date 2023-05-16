#include <bits/stdc++.h>

using namespace std;

int main() {
	int a, b;
	cin >> a >> b;
	if (a == 1)
		cout << a + b;
	else if (a == 2 || a == 3)
		cout << a + b - 1;
	else if (a == 4) {
		int sum;
		for (int i = 0; i <= 100000; i++) {
			for (int j = 0; j <= 10000; j++) {
				sum += j;
			}
		}
		cout << a + b;
	}
}
