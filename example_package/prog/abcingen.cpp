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
        // Group 0 and 'ocen' are not required.
        for (int i=1; i<= max_group; ++i) {
            oi_assert(id.find(i) != id.end(), "there can not be a gap in the groups, you don't have " + to_string(i));
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

const int MIN_N = 1;
const int MAX_N = 10'000;

struct TestData {
    double a, b;
    int n;
    vector<int> v;

    void print() {
        cout << min(a, b) << ' ' << max(a, b) << '\n';
        cout << n << '\n';
        for (int i = 0; i < n; ++i) {
            cout << v[i] << (i == n - 1 ? '\n' : ' ');
        }
    }
};

void gen_0() {
    cout << "-1 1\n";
    cout << "3\n";
    cout << "3 2 1\n";
}

void gen_1ocen() {
    cout << "-1000000 1000000\n";
    cout << "1000\n";
    for (int i = 1000; i >= 1; --i) {
        cout << i << (i == 1 ? '\n' : ' ');
    }
}

void gen_2ocen() {
    gen_1ocen();
}

void gen_proper_test(pair<int, int> rn) {
    TestData t;
    // `rng` also works with double.
    t.a = rng(-1e6, 1e6);
    t.b = rng(-1e6, 1e6);
    t.n = rng(rn.first, rn.second);
    vector<int> v(t.n);
    iota(v.begin(), v.end(), 1);
    rng.shuffle(v);
    t.v = v;
    t.print();
}

void gen1() {
    double a = rng(-1e6, 1e6);
    double b = rng(-1e6, 1e6);
    cout << min(a, b) << ' ' << max(a, b) << '\n';
}

void gen2(int a=MIN_N, int b=MAX_N) {
    int n = rng(a, b);
    cout << n << '\n';
    vector<int> v(n);
    iota(v.begin(), v.end(), 1);
    rng.shuffle(v);
    for (int i = 0; i < n; ++i) {
        cout << v[i] << (i == n - 1 ? '\n' : ' ');
    }
}

///////////////////////////////////////////////////////////////////////////////

void gen_all_tests() {
    current_test.set_group(ocen); // Group ocen.
    gen_test_reseed("1ocen", gen_1ocen);
    current_test.advance_id();
    GEN_TEST_RESEED(gen_2ocen());

    current_test.advance_group(); // Group 0.
    gen_test_reseed("0", gen_0);

    current_test.advance_group(); // Group 1.
    gen_test_reseed(current_test++, gen_proper_test, pair{1, 100});
    GEN_TEST_RESEED(gen_proper_test({100, 100}));

    current_test.advance_group(); // Group 2.
    GEN_TEST_RESEED(cout << "0.001 1.34\n2\n2 1\n");
    GEN_TEST(12345678, gen_proper_test({100, 100}));
    GEN_TEST_RESEED(
        int x = MAX_N / 5;
        gen1();
        gen2(x);
    );

    GEN_TEST_RESEED_GROUP(1, gen_0());
    GEN_TEST_RESEED_GROUP(3, gen_0());
    GEN_TEST_RESEED(gen1(); gen2()); // Generates group 3, because last time it was 3.
    GEN_TEST_GROUP(0, 12345678, gen_0());

    return;
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
    oi_assert(argc == 1, "Run prog to create proper tests or prog stresstest seed to additionally generate stresstest.");
    gen_all_tests();
    return 0;
}
