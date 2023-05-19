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
		time_t start = time(0);
		int i = 0;
		while (time(0) - start < 5) {
			i++;
		}
		cout << a + b;
	}
}
