#include "oi.h"
#undef cout
#undef printf
#include <bits/stdc++.h>
using namespace std;

oi::Random rng;

struct TestGenerator {
public:
    string tag;
    int group;
    int id;

    TestGenerator(int _group = 0) {
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
        group = _group;
        id = 0;
        open_file();
    }
    
    ~TestGenerator() {
        close_file();
    }
    
    void advance_group() noexcept {
        close_file();
        ++group;
        id = 0;
        open_file();
    }
    
    void advance_id() noexcept {
        close_file();
        ++id;
        open_file();
    }
    
    TestGenerator operator++(int) noexcept {
        TestGenerator res = *this;
        advance_id();
        return res;
    }

private:
    string get_name() {
        string res = "";
        if (group == -1) {
            return tag + to_string(id+1) + "ocen.in";
        }
        unsigned tmp_id = id;
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

    void open_file() {
        // Flush the buffers before reopening the next test.
        cout << flush;
        fflush(stdout);
        auto test_filename = get_name();
        oi_assert(freopen(test_filename.c_str(), "w", stdout), "failed to generate test ", test_filename);
        //std::cerr << "Generating " << test_filename << "...\n";
        rng = oi::Random{static_cast<uint_fast64_t>(hash<string_view>{}(test_filename))};
    }

    void close_file() {
        // Flush the buffers before finishing.
        cout << flush;
        fflush(stdout);
        auto test_filename = get_name();
        std::cerr << "Generated " << test_filename << "\n";
    }
};

struct TestData {
    double n, m;

    void print() {
        cout << n << ' ' << m << '\n';
    }
};

void gen_0() {
    cout << "2 3\n";
}

void gen_0_alternative() {
    TestData t;
    t.n = 2;
    t.m = 3;
    t.print();
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

void gen_all_tests() {
    TestGenerator current_test_name(-1); // Grupa ocen.
    gen_1ocen();

    current_test_name.advance_group(); // Grupa 0.
    gen_0();

    current_test_name.advance_group(); // Grupa 1.
    gen_test({1, 100});
    current_test_name++;
    gen_test({100, 100});

    current_test_name.advance_group(); // Grupa 2.
    gen_test({101, 1'000});
    current_test_name++;
    gen_test({1'000, 1'000});

    current_test_name.advance_group(); // Grupa 3.
    for (int i = 0; i < 5; ++i) {
        gen_test({1, 1'000});
        if (i < 4) current_test_name++;
    }
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
    std::cerr << "Generating all tests ...\n";
    gen_all_tests();
    return 0;
}
