#include <bits/stdc++.h>

using namespace std;

int main() {
	int a, b;
	cin >> a >> b;
	if (a == 1 || a == 2)
		cout << a + b;
	else if (a == 3)
		cout << a + b + 2;
	else if (a == 4) {
		int c = 0;
		cout << a + b / c;
		return 1;
	}
}
