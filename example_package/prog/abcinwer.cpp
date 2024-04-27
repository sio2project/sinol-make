#include <bits/stdc++.h>
#include "oi.h"

using namespace std;

const int MIN_N = 0;
const int MAX_N = 1'000'000;

void inwer(oi::Scanner in) {
    // This is an example inwer.
    // Remove or change the code as needed.
    
    double n, m;
    
    in >> oi::Num{n, MIN_N, MAX_N} >> ' ' >> oi::Num{m, n, MAX_N} >> oi::nl;
    in >> oi::eof;
    // `oi::eof` in `oi::Scanner::Mode::TestInput` mode allows only EOF.
    // `oi::Num{n, x, y}` reads "n", where "n" is in the range <x,y>
    // `oi::nl` in `oi::Scanner::Mode::TestInput` mode allows only a single `\n`.
    // The template solution should not print whitespace at the end of the line.
    
    oi_assert(n <= m, "optional msg");
    if (n > m) {
        oi::bug("a > b, something is wrong with the generator");
    }


    ///////////////////////////////////////////////////////////////////////////
    // This part of the code validates subtasks and pretests.
    
    // Add more groups and pre-tests.
    auto is_subtask1 = [&]() -> bool {
        return n <= 10 && m <= 10;
    };
    auto is_subtask2 = [&]() -> bool {
        return n <= 1'000;
    };
    auto is_subtask3 = [&]() -> bool {
        return n <= 1'000'000;
    };

    auto is_0a = [&]() -> bool {
        return fabs(n-1) <= 1e-6 && fabs(m-2) <= 1e-6;
    };
    auto is_1ocen = [&]() -> bool {
        return fabs(n-1.001) <= 1e-6 && fabs(m-2.002) <= 1e-6;
    };

    // Set up the subtasks and pre-tests you have.
    map<int, bool> subtasks = {
        {1, is_subtask1()},
        {2, is_subtask2()},
        {3, is_subtask3()},
    };
    map<string, bool> sample_tests = {
        {"0a", is_0a()},
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
        << "n = " << setw(8) << n
        << ", m = " << setw(8) << m
        << " | subtasks = " << subtasks_s << ", sample test = " << sample_test_s;
}

int main() {
    inwer(oi::Scanner{stdin, oi::Scanner::Mode::TestInput, oi::Lang::PL});
    return 0;
}
