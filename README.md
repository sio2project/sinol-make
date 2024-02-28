# ![Logo](https://avatars.githubusercontent.com/u/93839068?s=60&v=4) st-make

`st-make` is a CLI tool for creating and verifying problem packages
for [sio2](https://github.com/sio2project/oioioi)
with features such as:

- measuring time and memory in the same deterministic way as sio2,
- running the solutions in parallel,
- keeping a git-friendly report of solutions' scores,
- catching mistakes in the problem packages as early as possible,
- and more.

This tool is a fork of [sinol-make](https://github.com/sio2project/sinol-make), with features specific to [Talent](https://talent.edu.pl/) contests.

## Contents

- [Why?](#why)
- [Installation](#installation)
- [Usage](#usage)
- [Reporting bugs and contributing code](#reporting-bugs-and-contributing-code)

### Why?

The purpose of the tool is to make it easier to create good problem packages
for Talent competitions, which requires collaboration with other people
and using a multitude of "good practices" recommendations.
While there are several excellent CLI tools for creating tests and solutions,
they lack some built-in mechanisms for verifying packages and finding mistakes
before uploading the package to the judge system.
As st-make was created specifically for the sio2 problem packages,
by default it downloads and uses sio2's deterministic mechanism of measuring
solutions' runtime, called `oiejq`.

### Installation

It's possible to directly install [st-make](https://pypi.org/project/st-make/)
through Python's package manager pip, which usually is installed alongside Python:

```bash
pip3 install st-make
```

`pip` installs the `st-make` executable in `~/.local/bin/` directory,
so make sure this directory is in your `PATH`.
[Here's](https://gist.github.com/nex3/c395b2f8fd4b02068be37c961301caa7) how to add a directory to `PATH`.

As `oiejq` works only on Linux-based operating systems,
*we do not recommend* using operating systems such as Windows or macOS.
Nevertheless `st-make` supports those operating systems,
though there are additional installation steps required to use
other tools for measuring time (which are non-deterministic and produce reports different from sio2):

- Debian-based systems (Ubuntu, usually Windows WSL): `apt install time`
- Arch-based systems: `pacman -S time`
- macOS: `brew install gnu-time coreutils`

#### Autocompletion (optional)

If you would like to have autocompletion for `st-make` commands,
run the following command and refresh the shell (e.g. by opening a new terminal):

```shell
activate-global-python-argcomplete
```

### Usage

The availabe commands (see `st-make --help`) are:

- `st-make run` -- Runs selected solutions (by default all solutions) on selected tests (by default all tests) with a given number
of CPUs. Measures the solutions' time with oiejq, unless specified otherwise. After running the solutions, it
compares the solutions' scores with the ones saved in config.yml. If you're using oiejq, make sure you are not running on efficiency
cpu cores. You can check if you have them [like this](https://stackoverflow.com/a/71282744). To run on normal cpu cores, use
`taskset -c 8-15 st-make ...`, assuming that cpu cores 8-15 are not efficiency cores.
Run `st-make run --help` to see available flags.
- `st-make gen` -- Generate input files using ingen program (for example prog/abcingen.cpp for abc task). 
Whenever the new input differs from the previous one, the model solution will be used to generate the new output file.
You can also specify your ingen source file which will be used.
Run `st-make gen --help` to see available flags.
- `st-make ingen` -- Generate input files using ingen program (for example prog/abcingen.cpp for abc task).
You can also specify your ingen source file which will be used.
Run `st-make ingen --help` to see available flags.
- `st-make outgen` -- Generate output files using the model solutions. Run `st-make outgen --help` to see available flags.
- `st-make inwer` -- Verifies whether input files are correct using your "inwer.cpp" program. You can specify what inwer
program to use, what tests to check and how many CPUs to use. Run `st-make inwer --help` to see available flags.
- `st-make export` -- Creates archive ready to upload to Wyzwania, Talent-camp and other sio2 instances. Run `st-make export --help` to see all available flags.
- `st-make doc` -- Compiles all LaTeX files in doc/ directory to PDF. Run `st-make doc --help` to see all available flags.
- `st-make init [id]` -- Creates package from template [on github](https://github.com/Stowarzyszenie-Talent/st-make/tree/main/example_package) and sets task id to provided `[id]`. Requires an internet connection to run.

### Reporting bugs and contributing code

- Want to report a bug or request a feature? Open an issue:
  - [for Talent specific features](https://github.com/Stowarzyszenie-Talent/st-make/issues),
  - [for other areas](https://github.com/sio2project/sinol-make/issues).
- Want to help us build `st-make`? Create a Pull Request and we will gladly review it.
