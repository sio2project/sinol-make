#include "oi.h"
#undef cout
#undef printf
#include <bits/stdc++.h>
using namespace std;

oi::Random rng;

void gen_0() {
    cout << "2 3\n";
}

void gen_1ocen() {
    cout << "1000000\n";
    for (int i = 1000000; i >= 1; --i) {
        cout << i << (i == 1 ? '\n' : ' ');
    }
}

void gen_proper_test(pair<int, int> rn) {
    // `rng` also works with double.
    double a = rng(-1e6, 1e6);
    double b = rng(-1e6, 1e6);
    cout << min(a, b) << ' ' << max(a, b) << '\n';
}

struct Test {
    unsigned group;
    unsigned id;

    operator string();
    Test operator++(int) noexcept;
    void advance_group() noexcept;
};

template<class Func, class... Args>
void gen_test(string test_name, uint_fast64_t seed, Func&& func, Args&&... args);

// If there's no need to set a specific seed, this function will reseed the `rng`
// with a deterministic hash of the `test_name` string.
template<class Func, class... Args>
void gen_test_reseed(string test_name, Func&& func, Args&&... args);

void gen_all_tests() {
    gen_test_reseed("0", gen_0);
    gen_test_reseed("1ocen", gen_1ocen);

    Test current_test{.group = 1, .id = 0};
    gen_test_reseed(current_test++, gen_proper_test, pair{1, 100});
    gen_test_reseed(current_test++, gen_proper_test, pair{100, 100});

    current_test.advance_group();
    gen_test_reseed(current_test++, gen_proper_test, pair{101, 1'000});
    gen_test_reseed(current_test++, gen_proper_test, pair{1'000, 1'000});

    current_test.advance_group();
    for (int i = 0; i < 5; ++i) {
        gen_test_reseed(current_test++, gen_proper_test, pair{1, 1'000});
    }
}

void gen_stresstest() {
    // Optionally, print a random test
    return;
}

int main(int argc, char* argv[]) {
    if (argc == 3 && string(argv[1]) == "stresstest") {
        // Usage: prog/*ingen stresstest seed_uint64
        rng = oi::Random{static_cast<uint_fast64_t>(stoll(argv[2]))};
        gen_stresstest();
        return 0;
    }
    oi_assert(argc == 1, "Run prog/*ingen.sh to stresstest and create proper tests.");
    gen_all_tests();
    return 0;
}

///////////////////// `Test` and `gen_test_reseed` implementation /////////////////////

const string& get_task_id() {
    static auto task_id = [](string path) {
        auto end = path.rfind("ingen.");
        oi_assert(end != string::npos);
        auto beg = path.rfind('/', end);
        if (beg == string::npos) {
            beg = 0;
        } else {
            ++beg;
        }
        return path.substr(beg, end - beg);
    }(__FILE__);
    return task_id;
}

template<class Func, class... Args>
void gen_test(string test_name, uint_fast64_t seed, Func&& func, Args&&... args) {
    // Flush the buffers before reopening the next test.
    cout << flush;
    fflush(stdout);
    auto test_filename = get_task_id() + test_name + ".in";
    oi_assert(freopen(test_filename.c_str(), "w", stdout), "failed to save test ", test_filename);
    std::cerr << "Generating " << test_filename << "...\n";
    rng = oi::Random{seed};
    func(std::forward<decltype(args)>(args)...);
    // Flush the buffers before giving up control to the caller.
    cout << flush;
    fflush(stdout);
}

template<class Func, class... Args>
void gen_test_reseed(string test_name, Func&& func, Args&&... args) {
    // The new seed is created from the test name.
    uint_fast64_t seed = static_cast<uint_fast64_t>(hash<string_view>{}(test_name));
    gen_test(test_name, seed, func, args...);
}

Test::operator string() {
    string res = "";
    for (;;) {
        res += static_cast<char>('a' + id % ('z' - 'a' + 1));
        if (id <= 'z' - 'a') {
            break;
        }
        id = id / ('z' - 'a' + 1) - 1;
    }
    std::reverse(res.begin(), res.end());
    return to_string(group) + res;
}

Test Test::operator++(int) noexcept {
    Test res = *this;
    ++id;
    return res;
}

void Test::advance_group() noexcept {
    ++group;
    id = 0;
}
