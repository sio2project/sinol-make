#include <bits/stdc++.h>
#include "oi.h"

#undef cout
#undef printf
#define GEN_TEST(seed, code) gen_test(current_test++, seed, [&]() -> void { code; });
#define GEN_TEST_RESEED(code) gen_test_reseed(current_test++, []() -> void { code; });
#define GEN_TEST_GROUP(group, seed, code) \
current_test.set_group(group); gen_test(current_test++, seed, [&]() -> void { code; });
#define GEN_TEST_RESEED_GROUP(group, code) \
current_test.set_group(group); gen_test_reseed(current_test++, []() -> void { code; });
#define ocen -1

using namespace std;
oi::Random rng;

// Set task id!
const string get_task_id() {
    return "abc";
}

struct TestName {
private:    
    string tag;
    int group;
    int max_group;
    map<int,int> id;
public:
    TestName() {
        max_group = 0;
        set_group(0);
        tag = get_task_id();
    }

    ~TestName() {
        // Group 0 and 'ocen' are not required.
        bool there_was_a_gap = false;
        for (int i=1; i<=max_group; ++i) {
            if (there_was_a_gap && id.find(i) != id.end()) {
                oi::bug("There can not be a gap in the groups, you don't have " + to_string(i) + " group.");
            }
            if (id.find(i) == id.end()) there_was_a_gap = true;
        }
    }

    string get_tag() {
        return tag;
    }
    
    void advance_group() noexcept {
        set_group(group+1);
    }

    void set_group(int _group) noexcept {
        group = _group;
        oi_assert(group >= -1, "group must by >= -1");
        max_group = max(max_group, group);
    }
    
    void advance_id() noexcept {
        ++id[group];
    }

    TestName& operator++() noexcept {
        advance_id();
        return *this;
    }

    TestName operator++(int) noexcept {
        TestName res = *this;
        advance_id();
        return res;
    }

    string get_name() {
        string res = "";
        if (group == -1) {
            return to_string(id[group]+1) + "ocen";
        }
        int tmp_id = id[group];
        while (true) {
            res += static_cast<char>('a' + tmp_id % ('z' - 'a' + 1));
            if (tmp_id <= 'z' - 'a') {
                break;
            }
            tmp_id = tmp_id / ('z' - 'a' + 1) - 1;
        }
        std::reverse(res.begin(), res.end());
        return to_string(group) + res;
    }

    operator string() {
        return get_name();
    }
} current_test;

template<class Func, class... Args>
void gen_test(string test_name, uint_fast64_t seed, Func&& func, Args&&... args) {
    // Flush the buffers before reopening the next test.
    cout << flush;
    fflush(stdout);
    auto test_filename = current_test.get_tag() + test_name + ".in";
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

///////////////////////////////////////////////////////////////////////////////

const int MIN_N = 0;
const int MAX_N = 1'000'000;
const int MAX_N_2 = 1'000;

struct TestData {
    double a, b;

    void print() {
        cout << min(a, b) << ' ' << max(a, b) << '\n';
    }
};

void gen_0() {
    cout << "1 2\n";
}

void gen_1ocen() {
    cout << "1.001 2.002\n";
}

void gen_proper_test(double p, double k) {
    TestData t;
    // `rng` also works with double.
    t.a = rng(p, k);
    t.b = rng(t.a, k);
    t.print();
}

double gen1(double p, double k) {
    return rng(p, k);
}


///////////////////////////////////////////////////////////////////////////////

void gen_all_tests() {
    current_test.set_group(ocen); // Group ocen.
    GEN_TEST_RESEED(gen_1ocen());

    current_test.set_group(0); // Group 0.
    GEN_TEST_RESEED(gen_0());

    current_test.advance_group(); // Group 1.
    GEN_TEST_RESEED(gen_proper_test(1, 10));
    gen_test_reseed(current_test++, gen_proper_test, 1, 10);
    gen_test_reseed("1c", gen_proper_test, 1, 10);
    current_test.advance_id();
    gen_test_reseed(current_test++, gen_proper_test, 1, 10);
    // You can optionally use this method, (it gives you more freedom).

    current_test.advance_group(); // Group 2.
    GEN_TEST(12345678, gen_proper_test(1, 1000));
    GEN_TEST( 12348765,
        int x = MAX_N_2 / 2;
        cout << gen1(1, x) << ' ';
        cout << gen1(x, MAX_N) << '\n';
    );

    // A group of my choice
    GEN_TEST_RESEED_GROUP(2, gen_proper_test(0, 1000));
    GEN_TEST_GROUP(1, 12345678, gen_proper_test(0, 10));
    GEN_TEST_RESEED_GROUP(3, gen_proper_test(0, 1000000));
    // This does not have a group. So generates group 3, because last time it was 3.
    GEN_TEST_RESEED(gen_proper_test(0, 1000000));

    return;
}

void gen_stresstest() {
    // Print a small random test.
    gen_proper_test(0, 100);
    return;
}

int main(int argc, char* argv[]) {
    if (argc == 3 && string(argv[1]) == "stresstest") {
        // Usage: prog/*ingen stresstest seed_uint64
        rng = oi::Random{static_cast<uint_fast64_t>(stoll(argv[2]))};
        gen_stresstest();
        return 0;
    }
    oi_assert(argc == 1, "Run '[prog]' to create proper tests or '[prog] stresstest [seed]' to generate stresstest.");
    gen_all_tests();
    return 0;
}
