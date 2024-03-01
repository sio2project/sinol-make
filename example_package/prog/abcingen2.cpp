// WARNING.
// THIS TEMPLATES ALLOW ONLY FOR MAXIMUM OF 10 TEST GROUPS
// AND 26 TESTS INSIDE SINGLE GROUP

#include <bits/stdc++.h>
#include "oi.h"
#undef cout
#undef printf
using namespace std;

// Data used by Generator class
const int TEST_GROUP_COUNT = 3;
const string SKR = "cel";

oi::Random RG;

// Final test should be saved to this struct
// Update it and it's << operator depending on your needs.
struct TestData
{
    int n, m;
};

std::ostream &operator<<(std::ostream &out, TestData data)
{
    out << data.n << ' ' << data.m << '\n';
    return out;
}

/*
   This code is responsible for writing to corret file.
   There should not be need for changing this part.
 */

class Generator
{
public:
    ofstream out;
    TestData data;
    void writeTest();
    static vector<char> subtaskTests;
    Generator(int subtask);
    Generator() {}
    ~Generator() { out.close(); }
};

vector<char> Generator::subtaskTests(TEST_GROUP_COUNT + 1, 'a');

Generator::Generator(int subtask)
{
    string filename = SKR;
    if (subtask >= 0)
    {
        filename.push_back('0' + (char)subtask);
        filename.push_back(subtaskTests[subtask]);
        subtaskTests[subtask]++;
    }
    else
    {
        filename.push_back('0' + (char)abs(subtask));
        filename += "ocen";
    }

    filename += ".in";
    out.open(filename);

    uint_fast64_t seed = static_cast<uint_fast64_t>(hash<string_view>{}(filename));
    RG.setSeed((unsigned int)seed);
}

void Generator::writeTest()
{
    out << data;
    out.close();
}

/*
    Below you can implement your own generator.
    Example generator and ocen are provided.
 */

class RandomGenerator : public Generator
{
    int N, M;

public:
    void generate();
    RandomGenerator(int subtask, int _N, int _M) : Generator(subtask), N(_N), M(_M)
    {
        generate();
        writeTest();
    }
};

void RandomGenerator::generate()
{
    data = {RG.rand() % N, RG.rand() % M};
}

int main()
{
    // ==============================================================================================
    // numeracja testów w obrębie jednego subtaska jest autmatyczna (a, b, ..., z)
    // każdy test ma oddzielnego seeda do generatora RG,
    // który jest tworzony na podstawie nazwy pliku do którego będzie zapisany test
    // ==============================================================================================

    int testGrop = 1;
    RandomGenerator(testGrop, 10, 5);
    RandomGenerator(testGrop, 200, 5);

    testGrop++;
    RandomGenerator(testGrop, 10, 2000);
}
