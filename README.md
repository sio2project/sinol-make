# sinol-make
CLI tool for creating sio2 task packages. \
Currently in development and not yet ready to be used.

## Installing from source
`pip3 install .`

## Measuring time and memory with `oiejq`
### on Linux
Download `oiejq` from [here](https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz) and unpack it to `~/.local/bin/`
### on MacOS and Windows (WSL)
`oiejq` doesn't support MacOS and WSL on Windows yet.

## Measuring time and memory with `time`
### on Linux
Download `time` and `timeout` from apt:
```
apt install time timeout
```
### on MacOS
Download `gtime` and `gtimeout` from brew:
```
brew install gnu-time coreutils
```

## Running tests
1. Install `sinol-make` with test dependencies: \
```pip3 install .[tests]```
2. Run `pytest` in root directory of this repository.
