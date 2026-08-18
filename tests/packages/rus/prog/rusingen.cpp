#include <fstream>

using namespace std;

int main() {
	ofstream f("rus1a.in");
	f << "1 3\n";
	f.close();
	f.open("rus2a.in");
	f << "2 5\n";
	f.close();
	f.open("rus3a.in");
	f << "3 7\n";
	f.close();
	f.open("rus4a.in");
	f << "4 9\n";
	f.close();
}
