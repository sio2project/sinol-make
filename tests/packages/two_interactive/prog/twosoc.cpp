#include <bits/stdc++.h>
#include <assert.h>

using namespace std;

void write(int n, FILE *out) {
    fprintf(out, "%d\n", n);
    fflush(out);
}

void verdict(bool ok, string comment, int score) {
    cout << (ok ? "OK" : "WA") << "\n" << comment << "\n" << score << "\n";
    exit(0);
}

void wrong(string comment, int score = 0) {
    verdict(false, comment, score);
}

void accept(string comment, int score) {
    verdict(true, comment, score);
}

int main(int argc, char *argv[]) {
    assert(argc == 6);
    int num_processes = atoi(argv[1]);
    assert(num_processes == 2);

    FILE *in1 = fdopen(atoi(argv[2]), "r");
    FILE *out1 = fdopen(atoi(argv[3]), "w");
    assert(in1 != NULL);
    assert(out1 != NULL);

    FILE *in2 = fdopen(atoi(argv[4]), "r");
    FILE *out2 = fdopen(atoi(argv[5]), "w");
    assert(in2 != NULL);
    assert(out2 != NULL);

    int n;
    cin >> n;
    write(n, out1);

    int ans1, ans2;
    fscanf(in1, "%d", &ans1);
    if (feof(in1) || ferror(in1)) {
        wrong("Process 0 exited to early");
    }

    if (ans1 != n + 42) {
        wrong("Wrong answer on first interaction");
    }

    write(ans1, out2);
    fscanf(in2, "%d", &ans2);
    if (feof(in2) || ferror(in2)) {
        wrong("Process 1 exited to early");
    }

    if (ans2 != ans1 / 3) {
        accept("Wrong answer on second interaction", 50);
    }
    write(ans2, out1);

    fscanf(in1, "%d", &ans1);
    if (feof(in1) || ferror(in1)) {
        wrong("Process 0 exited to early");
    }
    if (ans1 != ans2 * 2) {
        accept("Wrong answer on third interaction", 75);
    }
    accept("", 100);
}
