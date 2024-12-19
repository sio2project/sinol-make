import os
import re
import requests
import subprocess

from sinol_make import util


__OICOMAPRE_VERSION = 'v1.0.2'


def get_path():
    return os.path.expanduser('~/.local/bin/oicompare')


def check_installed():
    path = get_path()
    if not os.path.exists(path):
        return False
    try:
        output = subprocess.run([path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except PermissionError:
        return False
    if output.returncode != 0:
        return False
    if output.stdout.decode().strip() != f'oicompare version {__OICOMAPRE_VERSION[1:]}':
        return False
    return True


def download_oicomapare():
    url = f'https://github.com/sio2project/oicompare/releases/download/{__OICOMAPRE_VERSION}/oicompare'
    if util.is_macos_arm():
        url += '-arm64'
    path = get_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    manual_download_msg = ("You can try downloading it manually from "
                           f"https://github.com/sio2project/oicompare/releases/tag/{__OICOMAPRE_VERSION}/ and placing "
                           f"it in ~/.local/bin/oicomapre")
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError:
        util.exit_with_error("Couldn't download oicompare (couldn't connect). " + manual_download_msg)
    if request.status_code != 200:
        util.exit_with_error(f"Couldn't download oicompare (returned status code: {request.status_code}). "
                            + manual_download_msg)
    with open(path, 'wb') as f:
        f.write(request.content)
    os.chmod(path, 0o755)


def check_and_download():
    # macOS doesn't allow compiling statically and I don't want to deal with it
    if util.is_macos():
        return
    if check_installed():
        return
    download_oicomapare()
    if not check_installed():
        util.exit_with_error("Couldn't download oicompare. Please try again later or download it manually.")


def _strip(s: str) -> str:
    """
    Replace all longest sequences of spaces with a single space.
    """
    return re.sub(r'[\s\0]+', ' ', s).strip()


def compare(file1_path: str, file2_path: str) -> bool:
    """
    Compare two files in the same way as oicompare does. Returns True if the files are the same, False otherwise.
    """
    with open(file1_path, "r") as file1, open(file2_path, "r") as file2:
        eof1 = False
        eof2 = False
        while True:
            try:
                line1 = _strip(next(file1))
            except StopIteration:
                eof1 = True
            try:
                line2 = _strip(next(file2))
            except StopIteration:
                eof2 = True

            if eof1 and eof2:
                return True
            if eof1:
                while line2 == "":
                    try:
                        line2 = _strip(next(file2))
                    except StopIteration:
                        eof2 = True
                        break
            elif eof2:
                while line1 == "":
                    try:
                        line1 = _strip(next(file1))
                    except StopIteration:
                        eof1 = True
                        break
                    if line1 != "":
                        break

            if eof1 and eof2:
                return True
            if (eof1 and line2 == "") or (eof2 and line1 == ""):
                continue
            if (eof1 and line2 != "") or (eof2 and line1 != ""):
                return False
            if line1 != line2:
                return False
