#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

int main() {
    oi::Scanner in(stdin, oi::PL);

    // Change this code to read and validate the input.
    int n = in.readInt(0, 1'000);
    in.readSpace();
    int m = in.readInt(0, 1'000);
    in.readEoln();
    in.readEof();
    assert(n > 0 || m > 0);

    // Change this code to have functions which return
    // whether the test satisfies a given subtask.
    auto is_subtask1 = [&]() -> bool {
        return n >= 0 && m >= 0;
    };
    auto is_subtask2 = [&]() -> bool {
        return n >= 5 && m >= 5;
    };

    // Change this code to have functions which return
    // whether the test is exactly the same as
    // the sample tests in the statement.
    auto is_0a = [&]() -> bool {
        return n == 0 && m == 1;
    };
    auto is_1ocen = [&]() -> bool {
        return n == 1000 && m == 1000;
    };

    map<int, bool> subtasks = {
        {1, is_subtask1()},
        {2, is_subtask2()},
    };
    string subtasks_s;
    for (auto [subtask_id, is_valid] : subtasks)
        subtasks_s += is_valid ? to_string(subtask_id) : string("_");

    map<string, bool> sample_tests = {
        {"0a", is_0a()},
        {"1ocen", is_1ocen()},
    };
    string sample_test_s = "_";
    for (auto [name, is_valid] : sample_tests)
        if (is_valid)
            sample_test_s = name;

    cout << "OK "
         << "n = " << setw(4) << n << ", "
         << "m = " << setw(4) << m << ", "
         << "subtasks = " << subtasks_s << ", sample test = " << sample_test_s << endl;
}
