# Image for the pytest-arch workflow, published as ghcr.io/sio2project/sinol-make-ci:arch.
FROM archlinux:latest

LABEL org.opencontainers.image.source=https://github.com/sio2project/sinol-make

# actions/setup-python has no builds for Arch, so the tested Python versions come from uv.
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python

RUN pacman -Syu --noconfirm diffutils time gcc dpkg ghostscript texlive-latexextra git rust uv \
    && pacman -Scc --noconfirm

RUN uv python install 3.11 3.15

# sinol-make looks for sio2jail in ~/.local/bin, the workflows link it there.
ADD --checksum=sha256:e292aa9a7ecf09991acc46e3638cf65f76366fa69f73ada5140b5d742c029d1d --chmod=755 \
    https://github.com/sio2project/sio2jail/releases/download/v1.5.3/sio2jail /usr/local/bin/sio2jail
