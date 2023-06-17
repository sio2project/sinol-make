#include <bits/stdc++.h>

using namespace std;

int rnd() {
	return rand() % 100;
}

int main() {
	int a, b;
	cin >> a >> b;
	if (a == 1)
		cout << a + b;
	else if (a == 2 || a == 3)
		cout << a + b + 2;
	else if (a == 4) {
		vector<int*> v;
		for (int i = 0; i <= 10000; i++) {
			int *tmp = new int[1000];
			for (int j = 0; j < 1000; j++) {
				tmp[j] = rnd();
			}
			v.push_back(tmp);
		}
		int s = 0;
		for (auto i : v) {
			for (int j = 0; j < 1000; j++) {
				s = (s + i[j]) % 1000000007;
			}
			delete[] i;
		}
		cout << a + b;
	}
}
