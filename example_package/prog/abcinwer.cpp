#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

void inwer(oi::Scanner in) {

    // This is sample code, modify as needed.
    
    double a, b;
    
    in >> oi::Num{a, -1e6, 1e6} >> ' ' >> oi::Num{b, -1e6, 1e6} >> oi::nl;
    // `oi::nl` in `oi::Scanner::Mode::TestInput` mode allows only a single `\n`.
    // `oi::Num` works with ints and long longs and double and ...
    if (false) {
        long long x;
        in >> oi::Num{x, 1ll, static_cast<long long>(1e12)};
    }
    
    oi_assert(a <= b, "optional msg");
    if (a > b) {
        oi::bug("a > b, something is wrong with the generator");
    }

    in >> oi::eof; // `oi::eof` in `oi::Scanner::Mode::TestInput` mode allows only EOF.


    ////////////////////////////////////////
    // Validation of subtasks and pre-tests.

    auto is_subtask1 = [&]() -> bool {
        return a <= 10 && b <= 10;
    };
    auto is_subtask2 = [&]() -> bool {
        return a+b <= 1'000'000;
    };

    auto is_0 = [&]() -> bool {
        return a == 2 && b == 3;
    };
    auto is_1ocen = [&]() -> bool {
        return a = 1000 && b == 1000;
    };

    // Set up the subtasks and pre-tests you have.
    map<int, bool> subtasks = {
        {1, is_subtask1()},
        {2, is_subtask2()},
    };
    map<string, bool> sample_tests = {
        {"0", is_0()},
        {"1ocen", is_1ocen()},
    };

    string subtasks_s;
    for (auto [subtask_id, is_valid] : subtasks)
        subtasks_s += is_valid ? to_string(subtask_id) : string("_");

    string sample_test_s = "-";
    for (auto [name, is_valid] : sample_tests)
        if (is_valid)
            sample_test_s = name;

    // You can display various information.
    oi::inwer_verdict.exit_ok()
        << "a = " << setw(4) << a
        << ", a+b = " << setw(5) << a+b
        << " | subtasks = " << subtasks_s << ", sample test = " << sample_test_s;
}

int main() {
    inwer(oi::Scanner{stdin, oi::Scanner::Mode::TestInput, oi::Lang::PL});
    return 0;
}
