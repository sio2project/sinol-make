#include <bits/stdc++.h>
#include <assert.h>

using namespace std;

int main(int argc, char *argv[]) {
    assert(argc == 4);
    int num_processes = atoi(argv[1]);
    assert(num_processes == 1);

    FILE *in = fdopen(atoi(argv[2]), "r");
    FILE *out = fdopen(atoi(argv[3]), "w");
    assert(in != NULL);
    assert(out != NULL);

    int n;
    cin >> n;

    fprintf(out, "%d\n", n);
    fflush(out);

    int ans;
    fscanf(in, "%d", &ans);
    if (feof(in) || ferror(in)) {
        // Exit with sigpipe. Interactor could also exit with WA and a proper comment.
        return 128 + 13;
    }
    if (n + 42 == ans) {
        cout << "OK\n";
    }
    else if (n + 24 == ans) {
        cout << "OK\nCoMmEnT\n50\n";
    }
    else {
        cout << "WA\nBad answer\n0\n";
    }
}
