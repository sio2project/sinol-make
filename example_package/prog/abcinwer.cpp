#include <bits/stdc++.h>
#include "oi.h"
using namespace std;

const int MIN_N = 1;
const int MAX_N = 10'000;

void inwer(oi::Scanner in) {
    // This is an example inwer.
    // Remove or change the code as needed.
    
    double a, b;
    
    in >> oi::Num{a, -1e6, 1e6} >> ' ' >> oi::Num{b, -1e6, 1e6} >> oi::nl;
    // `oi::Num{a, x, y}` reads "a", where "a" is in the range <x,y>
    // `oi::nl` in `oi::Scanner::Mode::TestInput` mode allows only a single `\n`.
    
    if (false) {
        // `oi::Num` works with ints and long longs and double and ...
        long long x;
        in >> oi::Num{x, 1ll, static_cast<long long>(1e12)};
    }
    
    oi_assert(a <= b, "optional msg");
    if (a > b) {
        oi::bug("a > b, something is wrong with the generator");
    }

    int n;
    in >> oi::Num{n, MIN_N, MAX_N} >> oi::nl;
    vector<int> v(n), vv(n);
    for (int i = 0; i < n; ++i) {
        in >> oi::Num{v[i], 1, n};
        vv[i] = v[i];
        if (i < n - 1) {
            in >> ' ';
        } else {
            // The template solution should not print whitespace at the end of the line.
            in >> oi::nl;
        }
    }
    in >> oi::eof; // `oi::eof` in `oi::Scanner::Mode::TestInput` mode allows only EOF.

    // This checks whether `v` is a permutation of `1, ..., n`.
    std::sort(v.begin(), v.end());
    for (int i = 0; i < n; ++i) {
        oi_assert(v[i] == i + 1);
    }

    ////////////////////////////////////////
    // Validation of subtasks and pre-tests.

    auto is_subtask1 = [&]() -> bool {
        return a <= 10 && b <= 10;
    };
    auto is_subtask2 = [&]() -> bool {
        return a+b <= 1'000'000;
    };
    // Add more groups.

    auto is_0 = [&]() -> bool {
        return abs(a - -1.0) < 1e-6 && abs(b - 1.0) < 1e-6 && n == 3 && vv[0] == 3 && vv[1] == 2 && vv[2] == 1 ;
    };
    auto is_1ocen = [&]() -> bool {
        return abs(a - -1e6) < 1e-6 && abs(b - 1e6) < 1e-6 && n == 1000;
    };
    // Add more pre-tests.

    // Set up the subtasks and pre-tests you have.
    map<int, bool> subtasks = {
        {1, is_subtask1()},
        {2, is_subtask2()},
        // Add more groups.
    };
    map<string, bool> sample_tests = {
        {"0", is_0()},
        {"1ocen", is_1ocen()},
        // Add more pre-tests.
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
        << "a = " << setw(8) << a
        << ", n = " << setw(5) << n
        << " | subtasks = " << subtasks_s << ", sample test = " << sample_test_s;
}

int main() {
    inwer(oi::Scanner{stdin, oi::Scanner::Mode::TestInput, oi::Lang::PL});
    return 0;
}
