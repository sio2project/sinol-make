# <img src="https://avatars.githubusercontent.com/u/2264918?s=200&v=4" height=60em> sinol-make

`sinol-make` is a CLI tool for creating and verifying problem packages
for [sio2](https://github.com/sio2project/oioioi)
with features such as:
- measuring time and memory in the same deterministic way as sio2,
- running the solutions in parallel,
- keeping a git-friendly report of solutions' scores,
- catching mistakes in the problem packages as early as possible,
- and more.

# Contents

- [Why?](#why)
- [Installation](#installation)
- [Usage](#usage)
- [Configuarion](#configuration)
- [Reporting bugs and contributing code](#reporting-bugs-and-contributing-code)

### Why?

The purpose of the tool is to make it easier to create good problem packages
for official competitions, which requires collaboration with other people
and using a multitude of "good practices" recommendations.
While there are several excellent CLI tools for creating tests and solutions,
they lack some built-in mechanisms for verifying packages and finding mistakes
before uploading the package to the judge system.
As sinol-make was created specifically for the sio2 problem packages,
by default it downloads and uses sio2's deterministic mechanism of measuring
solutions' runtime, called `oiejq`.

### Installation

It's possible to directly install [sinol-make](https://pypi.org/project/sinol-make/)
through Python's package manager pip, which usually is installed alongside Python:

```
pip3 install sinol-make
```

As `oiejq` works only on Linux-based operating systems,
*we do not recommend* using operating systems such as Windows or macOS.
Nevertheless `sinol-make` supports those operating systems,
though there are additional installation steps required to use
other tools for measuring time (which are non-deterministic and produce reports different from sio2):
- Windows (WSL): `apt install time`
- macOS: `brew install gnu-time coreutils`

### Autocompletion (optional)

If you would like to have autocompletion for `sinol-make` commands,
run the following command and refresh the shell (e.g. by opening a new terminal):

```shell
activate-global-python-argcomplete
```

### Usage

The availabe commands (see `sinol-make --help`) are:

- `sinol-make run` -- Runs selected solutions (by default all solutions) on selected tests (by default all tests) with a given number
of CPUs. Measures the solutions' time with oiejq, unless specified otherwise. After running the solutions, it
compares the solutions' scores with the ones saved in config.yml.
Run `sinol-make run --help` to see available flags.
- `sinol-make inwer` -- Verifies whether input files are correct using your "inwer.cpp" program. You can specify what inwer
program to use, what tests to check and how many CPUs to use. Run `sinol-make inwer --help` to see available flags.

### Reporting bugs and contributing code

- Want to report a bug or request a feature? [Open an issue](https://github.com/sio2project/sinol-make/issues).
- Want to help us build `sinol-make`? Create a Pull Request and we will gladly review it.
