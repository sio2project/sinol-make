#include <bits/stdc++.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>

std::string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

using namespace std;

ofstream out;

#define MAX_PATH_LENGTH 1024

void print_open_descriptors(void)
{
    const char* path = "/proc/self/fd";

    // Iterate over all symlinks in `path`.
    // They represent open file descriptors of our process.
    DIR* dr = opendir(path);
    if (dr == NULL)
        out << "Could not open dir: " <<  path << "\n";

    struct dirent* entry;
    while ((entry = readdir(dr)) != NULL) {
        if (entry->d_type != DT_LNK)
            continue;

        // Make a c-string with the full path of the entry.
        char subpath[MAX_PATH_LENGTH];
        int ret = snprintf(subpath, sizeof(subpath), "%s/%s", path, entry->d_name);
        if (ret < 0 || ret >= (int)sizeof(subpath))
            out << "Error in snprintf\n";

        // Read what the symlink points to.
        char symlink_target[MAX_PATH_LENGTH];
        ssize_t ret2 = readlink(subpath, symlink_target, sizeof(symlink_target) - 1);
        if (ret2 == -1)
            out << "Could not read symlink: " <<  subpath << "\n";
        symlink_target[ret2] = '\0';

        // Skip an additional open descriptor to `path` that we have until closedir().
        if (strncmp(symlink_target, "/proc", 5) == 0)
            continue;

        out << "Pid " << getpid() << " file descriptor " << entry->d_name << " -> " << symlink_target << "\n";
    }

    string res = exec("ls -l /proc/*/fd");
    out << res << "\n";
    res = exec("ps aux");
    out << res << "\n";

    closedir(dr);
}

int main(int argc, char const *argv[]) {
    if (argc != 3) {
        cerr << "Usage: ./a.out <input_file> <answer_file>" << endl;
        return 1;
    }
    ifstream ifs(argv[1]);
    out.open(argv[2]);
    int a;
    ifs >> a;
    cout << a << "\n" << flush;
    int ans;
//    char c;
    int ret = fcntl(0, F_GETFD);
    errno = 0;
    bool closed = ret == -1 && errno == EBADF;
//    scanf("%d", &ans);
//    ssize_t read_ret = read(0, &c, sizeof(c));
//    if (read_ret != sizeof(c)) {
//        out << "WRONG\n" << "read_ret: " << read_ret << "\n";
//        return 0;
//    }
//    ans = c - '0';
    cin >> ans;
    if (cin.eof()) {
        out << "WRONG\nEOF\n";
        return 0;
    }
    ret = fcntl(0, F_GETFD);
    errno = 0;
    bool closed2 = ret == -1 && errno == EBADF;
//    cin >> ans;
    int b;
    cin >> b;
    if (ans == a + 1) {
        out << "OK\n";
    }
    else if (ans == a + 2) {
        out << "OK\nwrong diff\n50";
    }
    else {
        out << "WRONG\n" << ans << " " << "\n";
//        out << "WRONG\n" << ans << " " << closed << " " << closed2 << " " << b << "\n";
//
//        print_open_descriptors();
    }
}
