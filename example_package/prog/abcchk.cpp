#include <bits/stdc++.h>
#include "oi.h"

using namespace std;

const int MIN_N = 0;
const int MAX_N = 1'000'000;

[[noreturn]] void checker(
    [[maybe_unused]] oi::Scanner& tin,
    [[maybe_unused]] oi::Scanner& tout,
    oi::Scanner& user
) {
    // This is an example checker with partial scores.
    // Remove or change the code as needed.

    double a, b;
    tin >> oi::Num{a, -1e6, 1e6} >> ' ' >> oi::Num{b, -1e6, 1e6} >> oi::nl;

    double sum;
    user >> oi::Num{sum, 2*MIN_N, 2*MAX_N};
    // `oi::nl` in mode `oi::Scanner::Mode::UserOutput` ignores whitespaces before the newline.
    // We do not load a newline in the last line.

    if (fabs((a + b) - sum) > 1e-6) {
        oi::checker_verdict.exit_wrong("Suma różni się od oczekiwanej");
    }

    user >> oi::eof; // `oi::eof` in mode `oi::Scanner::Mode::UserOutput` ignores newlines and whitespaces before the EOF.

    oi::checker_verdict.exit_ok();
    // oi::checker_verdict.exit_ok_with_score(80, "error message");
}

int main(int argc, char* argv[]) {
    oi_assert(argc == 4);
    constexpr auto scanner_lang = oi::Lang::PL;
    auto test_in = oi::Scanner(argv[1], oi::Scanner::Mode::Lax, scanner_lang);
    auto user_out = oi::Scanner(argv[2], oi::Scanner::Mode::UserOutput, scanner_lang);
    auto test_out = oi::Scanner(argv[3], oi::Scanner::Mode::Lax, scanner_lang);
    checker(test_in, test_out, user_out);
}

// You can write checker tests in the following way:
// (They won't be executed in sio2, they only work locally)
// If you don't want to write, delete or comment. However, I recommend writing.
CHECKER_TEST(TestInput{"0 1\n"}, TestOutput{"does not matter"}, UserOutput{"1"}, CheckerOutput{"OK\n\n100\n"})

// Or like this:
CHECKER_TEST(R"(
@test_in
0 1
@test_out
does not matter
@user
2
@checker
WRONG
Suma różni się od oczekiwanej
0
)")

