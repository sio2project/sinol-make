#include "oi.h"

const int MIN_N = 1;
const int MAX_N = 10'000;

[[noreturn]] void checker(
    [[maybe_unused]] oi::Scanner& tin,
    [[maybe_unused]] oi::Scanner& tout,
    oi::Scanner& user
) {
    // This is an example checker with partial scores.
    // Remove or change the code as needed.

    // First line ok -> 20 points
    // Second line ok -> 80 points
    // Both wrong -> 0 points
    int max_score = 100;
    string verdict_comment;

    double a, b;
    tin >> oi::Num{a, -1e6, 1e6} >> ' ' >> oi::Num{b, -1e6, 1e6} >> oi::nl;
    // `oi::Num{a, x, y}` reads "a", where "a" is in the range <x,y>
    int n;
    tin >> oi::Num{n, MIN_N, MAX_N} >> oi::nl;

    double sum;
    user >> oi::Num{sum, -2e6, 2e6} >> oi::nl;
    // `oi::nl` in mode `oi::Scanner::Mode::UserOutput` ignores whitespaces before the newline.
    if (fabs((a + b) - sum) > 1e-6) {
        // If you want to fail the whole test, you could use `oi::checker_verdict.exit_wrong()`
        // Here we want to check the output parts separately.
        max_score = 80;
        verdict_comment = "Pierwszy wiersz jest niepoprawny";
        oi::checker_verdict.set_partial_score(0, verdict_comment);
    } else {
        verdict_comment = "Pierwszy wiersz jest OK";
        oi::checker_verdict.set_partial_score(20, verdict_comment);
        // When checker returns a wrong verdict (by calling `oi::checker_verdict::exit_wrong()` or
        // when failing while scanning user output, the user will get 20 points instead of 0.
    }

    for (int i = 1; i <= n; ++i) {
        int x;
        user >> oi::Num{x, i, i};
        if (i == n) {
            user >> oi::nl; // `oi::nl` in mode `oi::Scanner::Mode::UserOutput` ignores whitespaces before the newline.
        } else {
            user >> ' ';
        }
    }
    user >> oi::eof; // `oi::eof` in mode `oi::Scanner::Mode::UserOutput` ignores newlines and whitespaces before the EOF.
    verdict_comment += "; Drugi wiersz jest OK";

    // It ignores `oi::checker_verdict.set_partial_score` and gives the user the specified amount of points.
    oi::checker_verdict.exit_ok_with_score(max_score, verdict_comment);
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
// CHECKER_TEST(TestInput{"0 1\n1\n1\n"}, TestOutput{"does not matter"}, UserOutput{"1\n1\n"}, CheckerOutput{"OK\nPierwszy wiersz jest OK; Drugi wiersz jest OK\n100\n"})

// // Or like this:
// CHECKER_TEST(R"(
// @test_in
// 0 1
// 3
// 1 2 3
// @test_out
// does not matter
// @user
// 2
// 1 2 3
// @checker
// OK
// Pierwszy wiersz jest niepoprawny; Drugi wiersz jest OK
// 80
// )")

