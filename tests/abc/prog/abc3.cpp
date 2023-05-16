#include <bits/stdc++.h>

using namespace std;

int main() {
	int a, b;
	cin >> a >> b;
	if (a == 1)
		cout << a + b;
	else if (a == 2 || a == 3)
		cout << a + b + 2;
	else if (a == 4) {
		vector<int**> v;
		for (int i = 0; i <= 10000; i++) {
			int **tmp = new int*[1000];
			v.push_back(tmp);
		}
		for (auto i : v) {
			delete[] i;
		}
		cout << a + b;
	}
}
