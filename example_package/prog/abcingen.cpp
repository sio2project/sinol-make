#include <bits/stdc++.h>
#include "oi.h"
#undef cout
#undef printf
#define GENERATE_TEST(code) generate_test([]() -> void { code; });
#define GENERATE_TEST_SEED(seed, code) generate_test_seed(seed, [&]() -> void { code; });
#define GENERATE_TEST_GROUP(group, code) name_of_generat_test.set_group(group); generate_test([]() -> void { code; });
#define GENERATE_TEST_SEED_GROUP(seed, group, code) \
name_of_generat_test.set_group(group); generate_test_seed(seed, [&]() -> void { code; });
#define ocen -1
using namespace std;
oi::Random rng;

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
        tag = [](string path) {
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
    }

    ~TestName() {
        for (int i=0; i<= max_group; ++i) {
            oi_assert(id.find(i) != id.end(), "there can not be a gap in the groups");
        }
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

    string get_name() {
        string res = "";
        if (group == -1) {
            return tag + to_string(id[group]+1) + "ocen.in";
        }
        unsigned tmp_id = id[group];
        for (;;) {
            res += static_cast<char>('a' + tmp_id % ('z' - 'a' + 1));
            if (tmp_id <= 'z' - 'a') {
                break;
            }
            tmp_id = tmp_id / ('z' - 'a' + 1) - 1;
        }
        std::reverse(res.begin(), res.end());
        return tag + to_string(group) + res + ".in";
    }
} name_of_generat_test;

template<class Func, class... Args>
void generate_test_seed(uint_fast64_t seed, Func&& func, Args&&... args) {
    // Flush the buffers before reopening the next test.
    cout << flush;
    fflush(stdout);
    auto test_filename = name_of_generat_test.get_name();
    oi_assert(freopen(test_filename.c_str(), "w", stdout), "failed to save test ", test_filename);
    std::cerr << "Generating " << test_filename << "...\n";
    rng = oi::Random{seed};
    func(std::forward<decltype(args)>(args)...);
    // Flush the buffers before giving up control to the caller.
    cout << flush;
    fflush(stdout);
    name_of_generat_test.advance_id();
}

template<class Func, class... Args>
void generate_test(Func&& func, Args&&... args) {
    // The new seed is created from the test name.
    uint_fast64_t seed = static_cast<uint_fast64_t>(hash<string_view>{}(name_of_generat_test.get_name()));
    generate_test_seed(seed, func, args...);
}

struct TestData {
    int n, m;

    void print() {
        cout << n << ' ' << m << '\n';
    }
};

void gen_0() {
    cout << "2 3\n";
}

void gen_1ocen() {
    cout << "1000000\n";
    for (int i = 1000000; i >= 1; --i) {
        cout << i << (i == 1 ? '\n' : ' ');
    }
}

void gen_test(pair<int, int> rn) {
    int a = rng(rn.first, rn.second);
    int b = rng(rn.first, rn.second);
    TestData t;
    t.n = min(a, b);
    t.m = max(a, b);
    t.print();
}

void gen_test2(int a, int b) {
    TestData t;
    t.n = min(a, b);
    t.m = max(a, b);
    t.print();
}

void gen_n(int a, int b) {
    cout << rng(a, b) << ' ';
}

void gen_m(int a, int b=1000000000) {
    cout << rng(a, b) << '\n';
}

void gen_all_tests() {
    name_of_generat_test.set_group(ocen); // Group ocen.
    GENERATE_TEST(gen_1ocen());

    name_of_generat_test.advance_group(); // Group 0.
    generate_test(gen_0);
    GENERATE_TEST(gen_0());
    GENERATE_TEST( cout << "2 3\n" );

    name_of_generat_test.advance_group(); // Group 1.
    generate_test(gen_test, pair{101, 1000});
    generate_test(gen_test2, 101, 1000);
    GENERATE_TEST(gen_test({1, 100}));
    GENERATE_TEST(gen_test2(1, 100));
    GENERATE_TEST(
        gen_n(1, 100);
        gen_m(100);
    )

    name_of_generat_test.set_group(3); // Group 3.
    generate_test_seed(12345678, gen_test, pair{101, 1'000});
    GENERATE_TEST_SEED(123345678, gen_test({1'000, 1'000}));
    GENERATE_TEST_SEED( 12345678,
        int x = 100000;
        gen_n(1, x);
        gen_m(x);
    )

    name_of_generat_test.advance_group(); // Group 4.
    for (int i = 0; i < 5; ++i) {
        GENERATE_TEST(gen_test({1, 1'000}));
    }

    GENERATE_TEST_GROUP(2, gen_0());
    GENERATE_TEST_GROUP(ocen, gen_0());
    GENERATE_TEST_SEED_GROUP(12345678, 2, gen_0());
    GENERATE_TEST_SEED_GROUP(87654321, 2, gen_0());
}

void gen_stresstest() {
    // Optionally, print a small random test.
    return;
}

int main(int argc, char* argv[]) {
    if (argc == 3 && string(argv[1]) == "stresstest") {
        // Usage: prog/*ingen stresstest seed_uint64
        rng = oi::Random{static_cast<uint_fast64_t>(stoll(argv[2]))};
        gen_stresstest();
        return 0;
    }
    oi_assert(argc == 1, "Run prog/*ingen.sh to stresstest and create proper tests");
    gen_all_tests();
    return 0;
}
