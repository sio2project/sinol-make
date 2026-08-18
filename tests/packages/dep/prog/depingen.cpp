#include <fstream>
#include "oi.h"

using namespace std;

int main() {
	ofstream f("dep1a.in");
	f << "1 3\n";
	f.close();
	f.open("dep2a.in");
	f << "2 5\n";
	f.close();
	f.open("dep3a.in");
	f << "3 7\n";
	f.close();
}
