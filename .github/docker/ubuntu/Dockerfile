# Image for the pytest-ubuntu workflow, published as ghcr.io/sio2project/sinol-make-ci:ubuntu.
FROM ubuntu:latest

LABEL org.opencontainers.image.source=https://github.com/sio2project/sinol-make

ENV DEBIAN_FRONTEND=noninteractive \
    DEB_PYTHON_INSTALL_LAYOUT=deb \
    TZ=Europe/Warsaw \
    RUSTUP_HOME=/opt/rustup \
    CARGO_HOME=/opt/cargo \
    PATH=/opt/cargo/bin:$PATH

RUN apt-get update \
    && apt-get install -y \
        build-essential ca-certificates curl dpkg ghostscript git sqlite3 sqlite3-doc \
        texlive-latex-extra time \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --no-modify-path \
    && chmod -R a+w /opt/rustup /opt/cargo \
    && cargo --version

# sinol-make looks for sio2jail in ~/.local/bin, the workflows link it there.
ADD --checksum=sha256:e292aa9a7ecf09991acc46e3638cf65f76366fa69f73ada5140b5d742c029d1d --chmod=755 \
    https://github.com/sio2project/sio2jail/releases/download/v1.5.3/sio2jail /usr/local/bin/sio2jail
